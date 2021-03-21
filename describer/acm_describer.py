from describer import db_helpers as hp
import pandas as pd


# TODO: currently only find the first 100 clusters
def describe():

    DomainNames = []
    Regions = []

    client = hp.getBotoClient('acm')
    region = client.meta.region_name
    certs = client.list_certificates()['CertificateSummaryList']
    for cert in certs:
        DomainNames.append(cert['DomainName'])
        Regions.append(region)
    if region != "us-east-1":
        client = hp.getBotoClient('acm', region_name="us-east-1")
        region = "us-east-1"
        certs = client.list_certificates()['CertificateSummaryList']
        for cert in certs:
            DomainNames.append(cert['DomainName'])
            Regions.append(region)

    df = pd.DataFrame({'DomainName': DomainNames, 'Region': Regions})
    return df
