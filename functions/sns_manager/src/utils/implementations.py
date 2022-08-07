from functions.sns_manager.src.utils.response_utils import (
    build_response,
    build_json_message,
)


def get_topics_response(sns_resource, logger):
    topic_objects = sns_resource.topics.all()

    topics = []
    for topic in topic_objects:
        item = {"arn": topic.arn, "attributes": topic.attributes}
        topics.append(item)

    return build_response(200, build_json_message("Success", topcis=topics))


def get_topic_info_response(sns_resource, topic_arn, logger):
    topic_objects = sns_resource.topics.all()

    my_topic = sns_resource.Topic(topic_arn)

    if not my_topic in topic_objects:
        logger.info(f"No topic found with arn {topic_arn}")
        return build_response(
            400, build_json_message(f"No topic found with arn {topic_arn}")
        )

    topic_info = {"arn": my_topic.arn, "attributes": my_topic.attributes}

    return build_response(200, build_json_message("Success", topic=topic_info))


def get_subcribers_of_topic_response(sns_resource, topic_arn, logger):

    topic = sns_resource.Topic(topic_arn)

    if not topic:
        return build_response(400, build_json_message("No topic found with that ARN"))

    subscription_arns = []

    for subscription in topic.subscriptions.all():
        subscription_arns.append(subscription.arn)

    return build_response(
        200,
        build_json_message(
            "Success", topic_arn=topic.arn, subscription_arns=subscription_arns
        ),
    )


def create_topic_response(sns_resource, request_body, logger):

    topic_name = request_body.get("name")

    if not request_body or not topic_name:
        return build_response(
            400,
            build_json_message("Please provide a name", error="Invalid request body"),
        )

    try:
        logger.info(build_json_message(f"Creating topic {topic_name}"))
        topic = sns_resource.create_topic(Name=topic_name)
    except Exception as ex:
        return build_response(
            500,
            build_json_message("There was an error creating the topic", error=str(ex)),
        )

    if not topic:
        return build_response(
            500, build_json_message("There was an error creating the topic")
        )

    topic_info = {"arn": topic.arn, "attributes": topic.attributes}
    return build_response(
        200,
        build_json_message("Successfully created topic", topic=topic_info),
    )


def subscribe_response(sns_resource, topic_arn, request_body, logger):

    protocol = request_body.get("protocol")
    endpoint = request_body.get("endpoint")

    if not protocol or not endpoint:
        logger.debug("Invalid request body")
        return build_response(
            400,
            build_json_message(
                "Please provide a protocol and an endpoint",
                error="Invalid request body",
            ),
        )
    if not isinstance(protocol, str) or not isinstance(endpoint, str):
        logger.debug("Invalid request body")
        return build_response(
            400,
            build_json_message(
                "Please ensure that protocol and endpoint are strings",
                error="Invalid request body",
            ),
        )

    topic = sns_resource.Topic(topic_arn)

    if not topic:
        logger.debug("Invalid topic arn provided")
        return build_response(
            400,
            build_json_message(
                "Please provide a valid topic arn",
                error="Invalid topic arn in query parameters",
            ),
        )

    subscription = topic.subscribe(Protocol=protocol, Endpoint=endpoint)

    logger.info("Subscription Pending")

    return build_response(
        200,
        build_json_message("Subscripton created, not yet confirmed"),
    )
