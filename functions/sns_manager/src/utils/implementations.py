from functions.sns_manager.src.utils.response_utils import build_response


def get_topics_response(sns_resource):
    topic_objects = sns_resource.topics.all()

    topics = []
    for topic in topic_objects:
        item = {"arn": topic.arn, "attributes": topic.attributes}
        topics.append(item)

    return build_response(200, {"topics": topics})


def get_topic_info_response(sns_resource, topic_arn):
    topic_objects = sns_resource.topics.all()

    my_topic = sns_resource.Topic(topic_arn)

    if not my_topic in topic_objects:
        return build_response(400, {"message": "No topic found with that ARN"})

    return build_response(
        200, {"topic": {"arn": my_topic.arn, "attributes": my_topic.attributes}}
    )


def get_subcribers_of_topic_response(sns_resource, topic_arn):

    topic = sns_resource.Topic(topic_arn)

    if not topic in sns_resource.topics.all():
        return build_response(400, {"message": "No topic found with that ARN"})

    return build_response(
        200, {"arn": topic.arn, "subscriptions": topic.subscriptions.all()}
    )
