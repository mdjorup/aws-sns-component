import json

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler.api_gateway import Response
from aws_lambda_powertools.event_handler import content_types
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator


tracer = Tracer()
logger = Logger()
app = APIGatewayRestResolver()


@app.exception_handler
@tracer.capture_method
def exception_handler():
    return


@app.not_found
@tracer.capture_method
def not_found():
    return


@app.get("/health")
@tracer.capture_method
def health():
    return Response(
        status_code=200,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps({"message": "ok"}),
    )


@app.get("/topics")
@tracer.capture_method
def get_topics():
    return


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

    return app.resolve(event, context)
