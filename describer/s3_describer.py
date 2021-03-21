from describer import db_helpers as hp
import pandas as pd

def describe():
    #client = boto3.client('')
    client = hp.getBotoClient('s3')
    buckets = client.list_buckets()['Buckets']
    names = []
    for bucket in buckets:
        name = hp.getFromJSON(bucket, 'Name')
        names.append(name)
    return pd.DataFrame({"S3 Bucket": names})