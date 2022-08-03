from aws_lambda_powertools.utilities.data_classes import event_source, SQSEvent


@event_source(data_class=SQSEvent)
def lambda_handler(event: SQSEvent, context):

    for record in event.records:
        continue

    return
