from describer import db_helpers as hp
import pandas as pd
import numpy as np


def parseCloudFrontBehaviour(behaviour, default=False):
    if default:
        path = "*"
    else:
        path = hp.getFromJSON(behaviour, 'PathPattern')
    viewer = hp.getFromJSON(behaviour, 'ViewerProtocolPolicy')
    allowed = hp.getFromJSON(behaviour, 'AllowedMethods')
    allowed = hp.listToString(hp.getFromJSON(allowed, 'Items'))
    minTTL = hp.getFromJSON(behaviour, 'MinTTL')
    maxTTL = hp.getFromJSON(behaviour, 'MaxTTL')
    defaultTTL = hp.getFromJSON(behaviour, 'DefaultTTL')
    smooth = hp.getFromJSON(behaviour, 'SmoothStreaming')
    return path, viewer, allowed, minTTL, defaultTTL, maxTTL, smooth


def formatOtherCloudFrontBehaviours(behaviours):
    if hp.isEmpty(behaviours):
        return np.NaN
    behaviourstring = ''
    for behaviour in behaviours:
        path, viewer, allowed, minTTL, defaultTTL, maxTTL, smooth = parseCloudFrontBehaviour(
            behaviour)
        behaviourstring += "Path: " + path + " Viewer Protocol Policy: " + viewer + " Allowed Methods: " + allowed+" Min TTL: " + \
            str(minTTL)+" Default TTL: "+str(defaultTTL) + " Max TTL: " + \
            str(maxTTL)+" Smooth Streaming: "+str(smooth) + "\n\n"
    return behaviourstring

# TODO: manage truncated list
#      Only list web distributions now


def describe():
    #client = boto3.client('cloudfront')
    client = hp.getBotoClient('cloudfront', region_name="us-east-1")
    dists = client.list_distributions()['DistributionList'].get('Items')

    if dists is None:
        # set to emmpty to list if no distribution found
        dists = []
    ids, dnses, cnames, prices, originIDs, originDNSs, defaultPaths, defaultViewers, defaultAlloweds, defaultminTTL, defaultDefaultTTL, defaultMaxTTL, defaultSmooth, others = [
    ], [], [], [], [], [], [], [], [], [], [], [], [], []
    # OriginProtocolPolicys = []
    for dist in dists:
        id = hp.getFromJSON(dist, 'Id')
        dns = hp.getFromJSON(dist, 'DomainName')
        cname = hp.getFromJSON(dist, 'Aliases')
        if hp.getFromJSON(cname, 'Quantity') is not 0:
            cname = hp.listToString(hp.getFromJSON(cname, 'Items '))
        else:
            cname = np.NaN
        price = hp.getFromJSON(dist, 'PriceClass')
        origin = hp.getFromJSON(hp.getFromJSON(dist, 'Origins'), 'Items')
        originID = hp.listToString(origin, 'Id')
        originDNS = hp.listToString(origin, 'DomainName')
        default = hp.getFromJSON(dist, 'DefaultCacheBehavior')
        path, viewer, allowed, minTTL, defaultTTL, maxTTL, smooth = parseCloudFrontBehaviour(
            default, True)
        other = formatOtherCloudFrontBehaviours(hp.getFromJSON(
            hp.getFromJSON(dist, 'CacheBehaviors'), 'Items'))
        ids.append(id)
        dnses.append(dns)
        prices.append(price)
        cnames.append(cname)
        originIDs.append(originID)
        originDNSs.append(originDNS)
        defaultPaths.append(path)
        defaultViewers.append(viewer)
        defaultAlloweds.append(allowed)
        defaultminTTL.append(minTTL)
        defaultDefaultTTL.append(defaultTTL)
        defaultMaxTTL.append(maxTTL)
        defaultSmooth.append(smooth)
        others.append(other)
        # OriginProtocolPolicys.append(dist['Origins']['Items'][0]['CustomOriginConfig']['OriginProtocolPolicy'])
    df = pd.DataFrame({"ID": ids, "DNS": dnses, "Cname": cnames, "Price Class": prices, "Origin ID": originIDs, "Origin DNS": originDNSs, "Default Behaviour: Path": defaultPaths, "Viewer Protocol Policy": defaultViewers,
                       "Allowed Methods": defaultAlloweds, "Min TTL": defaultminTTL, "Default TTL": defaultDefaultTTL, "Max TTL": defaultMaxTTL, "Smooth Streaming": defaultSmooth, "Other Cache Behaviours": others})
    return df
