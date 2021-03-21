from describer import db_helpers as hp
import pandas as pd

def describe():
    # client = boto3.client('cloudtrail')
    client = hp.getBotoClient('cloudtrail')
    trails = client.describe_trails()['trailList']
    trailNames = []
    s3BucketNames = []
    arns = []
    regions = []
    multi = []
    for trail in trails:
        trailNames.append(hp.getFromJSON(trail, 'Name'))
        s3BucketNames.append(hp.getFromJSON(trail,'S3BucketName'))
        arns.append(hp.getFromJSON(trail,'TrailARN'))
        regions.append(hp.getFromJSON(trail,'HomeRegion'))
        multi.append(hp.getFromJSON(trail,'IsMultiRegionTrail'))

    df = pd.DataFrame({"Name": trailNames, "S3 Bucket": s3BucketNames, "ARN": arns, "Region": regions, "Multi Region Enabled": multi})
    return df

