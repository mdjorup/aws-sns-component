import json

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler.api_gateway import Response
from aws_lambda_powertools.event_handler import content_types


tracer = Tracer()
logger = Logger()
app = APIGatewayRestResolver()


@app.get("/health")
@tracer.capture_method
def health():
    return Response(
        status_code=200,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps({"message": "ok"}),
    )


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event, context):

    return app.resolve(event, context)
