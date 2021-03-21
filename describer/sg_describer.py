from describer import db_helpers as hp
import pandas as pd
import numpy as np
import string

# parse port ranges of a single SG rule
def parsePortRange(rule):
    ip_range = np.NaN
    fromPort = hp.getFromJSON(rule, 'FromPort')
    toPort = hp.getFromJSON(rule, 'ToPort')
    if not np.isnan(fromPort) and not np.isnan(toPort):
        if fromPort == toPort:
            ip_range = str(fromPort)
        else:
            ip_range = str(fromPort)+" - "+str(toPort)
    if ip_range == '-1':
        return 'All'
    return ip_range

# parse the protocol of a single SG rule
def parseProtocol(rule):
    protocol = hp.getFromJSON(rule, 'IpProtocol')
    if protocol == "-1":
        protocol = "All Traffic"
    elif protocol == "tcp" or protocol == 'udp' or protocol == 'icmp':
        protocol = protocol.upper()
    return protocol
    
def checktype(tar):
    if type(tar) == 'float':
        print('yes')
        return ''
    return tar

def parseSourceDest(permission):
    ipRanges = hp.getFromJSON(permission,'IpRanges')
    ipRanges = hp.listToString(ipRanges,'CidrIp')
    groups = hp.getFromJSON(permission, 'UserIdGroupPairs')
    groups = hp.listToString(groups, 'GroupId')
    prefixlist = hp.getFromJSON(permission,'PrefixListIds')
    prefixlist = hp.listToString(prefixlist,'PrefixListId')
    # print(ipRanges, groups, prefixlist)
    if not isinstance(ipRanges, str):
        ipRanges = ''
    if not isinstance(groups, str):
        groups = ''
    if not isinstance(prefixlist, str):
        prefixlist = ''
    ret = checktype(ipRanges) + ';' + checktype(groups) + ';' + checktype(prefixlist)
    # print(ret)
    return ret.strip(';')

def describe():
    #client = boto3.client('ec2')
    client = hp.getBotoClient('ec2')
    securityGroups = client.describe_security_groups()['SecurityGroups']
    #placehodler
    names = []
    ids = []
    boundTypes = []
    protocols = []
    portRanges = []
    sourceDests =[]
    for sg in securityGroups:
        name = hp.getFromJSON(sg, 'GroupName')
        id = hp.getFromJSON(sg, 'GroupId')
        inbounds = hp.getFromJSON(sg, 'IpPermissions')
        outbounds = hp.getFromJSON(sg, 'IpPermissionsEgress')
        for inbound in inbounds:
            names.append(name)
            ids.append(id)
            boundTypes.append("Inbound")
            protocols.append(parseProtocol(inbound))
            portRanges.append(parsePortRange(inbound))
            sourceDests.append(parseSourceDest(inbound))
        # for outbound in outbounds:
        #     names.append(name)
        #     ids.append(id)
        #     protocols.append(parseProtocol(outbound))
        #     boundTypes.append("Outbound")
        #     portRanges.append(parsePortRange(outbound))
        #     sourceDests.append(parseSourceDest(outbound))
    df = pd.DataFrame({"Security Group Name": names, "Security Group ID": ids, "Protocol": protocols, "Ports": portRanges, "Source/Destination": sourceDests})
    return df