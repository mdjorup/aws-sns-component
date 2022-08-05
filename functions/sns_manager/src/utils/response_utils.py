import json

from aws_lambda_powertools.event_handler.api_gateway import Response
from aws_lambda_powertools.event_handler import content_types


def build_response(status_code, body):

    if not isinstance(status_code, int):
        raise TypeError

    return Response(
        status_code=status_code,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps(body),
    )


def build_json_message(message, *args, **kwargs):

    json_message = {"message": message, **kwargs}

    return json_message
