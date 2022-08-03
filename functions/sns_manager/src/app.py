import json
import os

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator

from functions.sns_manager.src.utils import build_response

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
    logger.warning(f"There was an uncaught exception: {str(ex)}")
    return build_response(
        500, {"message": "There was an uncaught exception", "error": str(ex)}
    )


@app.not_found
@tracer.capture_method
def not_found(ex: NotFoundError):
    method = app.current_event.http_method
    path = app.current_event.path
    logger.info(f"Route {method} {path} not found")
    return build_response(
        404,
        {
            "message": f"Route {method} {path} not found",
            "error": str(ex),
        },
    )


@app.get("/health")
def health():
    return build_response(200, {"message": "OK"})


@app.get("/topics")
@tracer.capture_method
def get_topics():

    topic_objects = sns_resource.topics.all()

    topics = []
    for topic in topic_objects:
        attributes = topic.attributes
        item = {
            "name": attributes.DisplayName,
            "arn": topic.arn,
            "subscriptions_confirmed": attributes.SubscriptionsConfirmed,
        }
        topics.append(item)

    return build_response(200, {"topics": topics})


@app.get("/topics/<topic_arn>")
@tracer.capture_method
def get_topic_info(topic_arn):
    return


@app.get("/topics/<topic_arn>/subscribers")
@tracer.capture_method
def get_subcribers_of_topic(topic_arn):
    return


@app.post("/topics")
@tracer.capture_method
def create_topic():
    return


@app.post("/topics/<topic_arn>/subscribe")
@tracer.capture_method
def subscribe(topic_arn):
    return


@app.post("/topics/<topic_arn>/publish")
@tracer.capture_method
def publish_message(topic_arn):
    return


@app.put("/topics/<topic_arn>/unsubscribe")
@tracer.capture_method
def unsubscribe(topic_arn):
    return


@app.delete("/topics/<topic_arn>")
@tracer.capture_method
def delete_topic(topic_arn):
    return


@lambda_handler_decorator
def middleware(handler, event, context: LambdaContext):

    handler_return = handler(event, context)

    return handler_return


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@middleware
def lambda_handler(event, context: LambdaContext):

    ip_address = event.get("headers", {}).get("X-Forwarded-For", "UNK")

    logger.append_keys(ip_address=ip_address)

    return app.resolve(event, context)
