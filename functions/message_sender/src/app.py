import os
import json

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import event_source, SQSEvent


tracer = Tracer()
logger = Logger()


sns_resource = boto3.resource("sns", endpoint_url=os.environ.get("SNS_ENDPOINT_URL"))


@event_source(data_class=SQSEvent)
@tracer.capture_lambda_handler
def lambda_handler(event: SQSEvent, context):

    logger.info(f"Attempting to send a batch of {len(event.records)} messages")

    for record in event.records:
        body = json.loads(record.get(body, {}))

        topic_arn = body.get("topic_arn", "")

        if not topic_arn:
            logger.info("Could not find topic in request body")
            continue

        topic = sns_resource.Topic(topic_arn)

        topic.publish(Message=body.get("message", ""), Subject=body.get("subject", ""))

    return
