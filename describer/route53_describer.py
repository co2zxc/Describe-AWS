from describer import db_helpers as hp
import pandas as pd

def describe(nextPageMarker=None):
    #client = boto3.client('route53domains', region_name='us-east-1')
    client = hp.getBotoClient('route53domains', region_name='us-east-1')
    if nextPageMarker is not None:
        domains=client.list_domains(NextPageMarker=nextPageMarker)['Domains']
    else:
        domains = client.list_domains()['Domains']
    names, renews, expiries = [], [], []
    for domain in domains:
        names.append(hp.getFromJSON(domain, 'DomainName'))
        renews.append(hp.getFromJSON(domain, 'AutoRenew'))
        expiries.append(hp.getFromJSON(domain, 'Expiry'))
    df = pd.DataFrame({"Domain": names, "Auto Renew": renews, "Expiry Date": expiries})
    return df

