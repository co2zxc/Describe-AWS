from describer import db_helpers as hp
import pandas as pd

def describe(nextToken=None):
    #client = boto3.client('sns')
    client = hp.getBotoClient('sns')
    if nextToken is not None:
        topics = client.list_topics(NextToken=nextToken)['Topics']
    else:
        topics = client.list_topics()['Topics']
    topicnames, protocols, endpoints = [],[],[]
    shownames = []
    # print(topics)
    for topic in topics:
        arn = hp.getFromJSON(topic, 'TopicArn')
        attr = client.get_topic_attributes(TopicArn=arn)['Attributes']
        displayname = hp.getFromJSON(attr, 'DisplayName')
        # response = client.get_topic_attributes(TopicArn=arn)
        # print(arn)
        # print(response)
        showname = arn.split(':')[-1]
        subs = client.list_subscriptions_by_topic(TopicArn=arn)['Subscriptions']
        for sub in subs:
            protocol = hp.getFromJSON(sub,'Protocol')
            endpoint = hp.getFromJSON(sub,'Endpoint')
            topicnames.append(displayname)
            protocols.append(protocol)
            endpoints.append(endpoint)
            shownames.append(showname)
    df = pd.DataFrame({"Topic Display Name": topicnames, "Subscription Protocol": protocols, "Subscription Endpoint": endpoints, "Topic Name": shownames})
    return df