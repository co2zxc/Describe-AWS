import boto3
import describeAWS
from collections.abc import Sequence
import numpy as np
import pandas as pd


# return the boto client of different AWS service
def getBotoClient(*args, **kwargs):
    client = boto3.client(*args, **kwargs)
    return client


# get domain names from ACM with the ssl ARN
def getDomainsFromACM(ssl):
    domain = []
    if isEmpty(ssl):
        return ssl
    # client = boto3.client('acm')
    client = getBotoClient('acm')
    cert = client.describe_certificate(CertificateArn=ssl)['Certificate']
    domain.append(getFromJSON(cert, 'DomainName'))
    cnames = getFromJSON(cert, 'SubjectAlternativeNames')
    if not isEmpty(cnames):
        for cname in cnames:
            domain.append(cname)
    return listToString(domain, None)


# return NaN when get null object from json
def getFromJSON(json, field: str):
    try:
        attr = json[field]
    except:
        attr = np.NaN
    return attr

# check if the result from parsing json is empty


def isEmpty(attr):
    if isinstance(attr, str):
        return False
    if not isinstance(attr, Sequence):
        return np.isnan(attr)
    else:
        return len(attr) == 0

# parse a JSON list into a single string using ";" to seperate each object


def listToString(list, field=None):
    listString = np.NaN
    if isEmpty(list):
        return listString
    if field is None:
        listString = str(list[0])
        for i in list:
            if i == list[0]:
                continue
            else:
                listString = listString + ";" + str(i)
    else:
        # if field is supplied, parse the request field into a list
        listString = str(list[0][field])
        for i in list:
            if i == list[0]:
                continue
            else:
                listString = listString + ";" + str(i[field])
    return listString

# find the name inside the tag of an AWS resource


def findNameinTags(json):
    name = np.NaN
    tags = getFromJSON(json, 'Tags')
    try:
        for tag in tags:
            if tag['Key'] == "Name":
                name = tag['Value']
                break
    except:
        print("No Name")
    return name


def writeToExcel(writer: pd.ExcelWriter, df: pd.DataFrame, name: str):
    if not df.empty:
        df.to_excel(writer, sheet_name=name, index=False)
    else:
        print("!!No " + name + " to write!!")


def bool_list_to_string(bool_list):
    ret = ''
    for item in bool_list:
        if ret == '':
            ret = str(item)
        else:
            ret = ret + ';' + str(item)
    return ret
