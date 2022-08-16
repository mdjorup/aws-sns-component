import os

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator

from functions.sns_manager.src.utils.response_utils import (
    build_response,
    build_json_message,
)
from functions.sns_manager.src.utils.implementations import (
    get_topics_response,
    get_topic_info_response,
    get_subcribers_of_topic_response,
    create_topic_response,
    publish_message_response,
    subscribe_response,
)

tracer = Tracer()
logger = Logger()
app = APIGatewayRestResolver()


logger = Logger(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    service=os.environ.get("POWERTOOLS_SERVICE_NAME", "lambda_auth"),
)


sns_resource = boto3.resource("sns", endpoint_url=os.environ.get("SNS_ENDPOINT_URL"))


@app.exception_handler(Exception)
@tracer.capture_method
def exception_handler(ex: Exception):
    logger.error(build_json_message("There was an uncaught exception", error=str(ex)))
    return build_response(
        500, build_json_message("There was an uncaught exception", error=str(ex))
    )


@app.not_found
@tracer.capture_method
def not_found(ex: NotFoundError):
    method = app.current_event.http_method
    path = app.current_event.path
    logger.info(build_json_message(f"Route {method} {path} not found", error=str(ex)))
    return build_response(
        404,
        build_json_message(f"Route {method} {path} not found", error=str(ex)),
    )


@app.get("/health")
def health():
    return build_response(200, build_json_message("OK"))


@app.get("/topics")
@tracer.capture_method
def get_topics():

    logger.info(build_json_message("Getting all topics"))

    response = get_topics_response(sns_resource, logger)

    return response


@app.get("/topics/<topic_arn>")
@tracer.capture_method
def get_topic_info(topic_arn):

    logger.info(build_json_message(f"Getting information for topic {topic_arn}"))

    response = get_topic_info_response(sns_resource, topic_arn, logger)

    return response


@app.get("/topics/<topic_arn>/subscribers")
@tracer.capture_method
def get_subcribers_of_topic(topic_arn):

    logger.info(build_json_message(f"Getting subscribers for topic {topic_arn}"))

    response = get_subcribers_of_topic_response(sns_resource, topic_arn, logger)

    return response


@app.post("/topics")
@tracer.capture_method
def create_topic():

    logger.info(build_json_message("Attempting to create topic"))

    request_body = app.current_event.json_body

    response = create_topic_response(sns_resource, request_body, logger)

    return response


@app.post("/topics/<topic_arn>/subscribe")
@tracer.capture_method
def subscribe(topic_arn):

    request_body = app.current_event.json_body

    logger.info(
        build_json_message(f"Subscribing to topic {topic_arn}", body=request_body)
    )

    response = subscribe_response(sns_resource, topic_arn, request_body, logger)

    return response


@app.post("/topics/<topic_arn>")
@tracer.capture_method
def publish_message(topic_arn):

    sqs_resource = boto3.resource("sqs")
    queue = sqs_resource.Queue(os.environ.get("SQS_MESSAGE_ENDPOINT_URL"))

    request_body = app.current_event.json_body

    logger.info(build_json_message(f"Publishing message to topic {topic_arn}"))

    response = publish_message_response(queue, topic_arn, request_body, logger)

    return response


@app.delete("/topics/<topic_arn>")
@tracer.capture_method
def delete_topic(topic_arn):

    logger.info(build_json_message(f"Deleting topic {topic_arn}"))

    topic = sns_resource.Topic(topic_arn)
    topic.delete()

    return build_response(
        200,
        build_json_message("Successfully deleted topic", topic_arn=topic_arn),
    )


@lambda_handler_decorator
def middleware(handler, event, context: LambdaContext):

    ip_address = event.get("headers", {}).get("X-Forwarded-For", "UNK")

    logger.append_keys(ip_address=ip_address)

    # before logic - authorization

    handler_return = handler(event, context)

    # after logic - send changes to the update queue

    return handler_return


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@middleware
def lambda_handler(event, context: LambdaContext):

    return app.resolve(event, context)
