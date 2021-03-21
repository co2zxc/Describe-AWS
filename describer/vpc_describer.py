from describer import db_helpers as hp
import pandas as pd
import numpy as np
import boto3

def get_cgw_ip(id):
    client = hp.getBotoClient('ec2')
    response = client.describe_customer_gateways(
        CustomerGatewayIds=[id]
    )
    return response['CustomerGateways'][0]['IpAddress']
    
def get_vgw_vpc(id):
    client = hp.getBotoClient('ec2')
    response = client.describe_vpn_gateways(
        VpnGatewayIds=[id]
    )
    return response['VpnGateways'][0]['VpcAttachments'][0]['VpcId']
    

def describe_VPN():
    # client = boto3.client('ec2')
    client = hp.getBotoClient('ec2')
    vpns = client.describe_vpn_connections()['VpnConnections']
    vpnnames, vpnids, vgwnames, vgwids, cgwnames, cgwids, statics, routeses = [],[],[],[],[],[],[],[]
    vgw_vpcs, cgw_ips = [], []
    for vpn in vpns:
        vgwid = hp.getFromJSON(vpn, 'VpnGatewayId')
        # get vgw name from vgw id
        if not hp.isEmpty(vgwid) :
            vgw = client.describe_vpn_gateways(VpnGatewayIds=[vgwid])['VpnGateways'][0]
            vgwname = hp.findNameinTags(vgw)
        else:
            vgwname = vgwid
        cgwid = hp.getFromJSON(vpn,'CustomerGatewayId')
        # get cgw name from cgw id
        if not hp.isEmpty(cgwid) :
            cgw = client.describe_customer_gateways(CustomerGatewayIds=[cgwid])['CustomerGateways'][0]
            cgwname = hp.findNameinTags(cgw)
        else:
            cgwname = cgwid
        vpnid = hp.getFromJSON(vpn, 'VpnConnectionId')
        vpnname = hp.findNameinTags(vpn)
        static = hp.getFromJSON(hp.getFromJSON(vpn, 'Options'), 'StaticRoutesOnly')
        routes = hp.getFromJSON(vpn, 'Routes')
        routes = hp.listToString(routes, 'DestinationCidrBlock')
        
        if vgwname not in vgwnames:
            vgwnames.append(vgwname)
            vgwids.append(vgwid)
            vgw_vpcs.append(get_vgw_vpc(vgwid))
        
        cgwnames.append(cgwname)
        cgwids.append(cgwid)
        vpnnames.append(vpnname)
        vpnids.append(vpnid)
        statics.append(static)
        routeses.append(routes)
        cgw_ips.append(get_cgw_ip(cgwid))
    cgwdf = pd.DataFrame({"CGW Name": cgwnames, "CGW ID": cgwids, "CGW IP":cgw_ips})
    vgwdf = pd.DataFrame({"VGW Name": vgwnames, "VGW ID": vgwids, "VGW VPC":vgw_vpcs})
    vpndf = pd.DataFrame({"VPN Name": vpnnames, "VPN ID": vpnids, "Routes": routeses})
    return cgwdf, vgwdf, vpndf


def describe_subnet(filters, client):
    subnets = client.describe_subnets(Filters=filters)['Subnets']
    subnetIDs = []
    subnetCIDRs = []
    subnetNames = []
    subnetAZs = []
    subnetVPCs = []
    routeNames = []
    routeIDs = []
    routeAssociates = []
    for subnet in subnets:
        id = hp.getFromJSON(subnet, 'SubnetId')
        cidr = hp.getFromJSON(subnet, 'CidrBlock')
        vpcid = hp.getFromJSON(subnet, 'VpcId')
        name = hp.findNameinTags(subnet)
        az = hp.getFromJSON(subnet, 'AvailabilityZone')
        subnetIDs.append(id)
        subnetCIDRs.append(cidr)
        subnetNames.append(name)
        subnetAZs.append(az)
        subnetVPCs.append(vpcid)
        # RouteTable
        filters = [{'Name': "association.subnet-id", 'Values': [id]}]
        routes = client.describe_route_tables(Filters=filters)['RouteTables']
        if routes:
            route = routes[0]
            name = hp.findNameinTags(route)
            routeNames.append(name)
            routeId = hp.getFromJSON(route, 'RouteTableId')
            routeIDs.append(routeId)
            routeAssociates.append(id)
    subnetdf = pd.DataFrame({"Subnet Name": subnetNames, "Subnet ID": subnetIDs, "AZ": subnetAZs, "CIDR": subnetCIDRs,})
    vpcrtdf = pd.DataFrame({"Route Table Name": routeNames, "Route Table ID": routeIDs, "Subnet Associations": routeAssociates})
    return subnetdf, vpcrtdf


def describe_nat(filters, client):
    nats = client.describe_nat_gateways(Filters=filters)['NatGateways']
    natNames = []
    natIDs = []
    publicIPs = []
    privateIPs = []
    for nat in nats:
        name = hp.findNameinTags(nat)
        id = hp.getFromJSON(nat, 'NatGatewayId')
        public = hp.getFromJSON(nat, 'NatGatewayAddresses')[0]['PublicIp']
        private = hp.getFromJSON(nat, 'NatGatewayAddresses')[0]['PrivateIp']
        natNames.append(name)
        natIDs.append(id)
        publicIPs.append(public)
        privateIPs.append(private)
    natdf = pd.DataFrame({"NAT Name": natNames, "NAT ID": natIDs, "Public IP": publicIPs, "Private IP": privateIPs})
    return natdf

def describe_flow(filters, client):
    flows = client.describe_flow_logs(Filters=filters)['FlowLogs']
    flowIds = []
    destTypes = []
    dests = []
    traffics = []
    statuses = []
    for flow in flows:
        id = hp.getFromJSON(flow, 'FlowLogId')
        destType = hp.getFromJSON(flow, 'LogDestinationType')
        dest = hp.getFromJSON(flow, 'LogDestination')
        traffic = hp.getFromJSON(flow, 'TrafficType')
        status = hp.getFromJSON(flow, 'DeliverLogsStatus')
        flowIds.append(id)
        destTypes.append(destType)
        dests.append(dest)
        traffics.append(traffic)
        statuses.append(status)
    flowdf = pd.DataFrame(
        {"Flow ID": flowIds, "Traffic Type": traffics, "Destination Type": destTypes, "Destination Name": dests,
         "Status": statuses})
    return flowdf

def describe():
    # client = boto3.client('ec2')
    client = hp.getBotoClient('ec2')
    #VPC
    vpcs = client.describe_vpcs()['Vpcs']
    vpcIDs = []
    vpcCIDRs = []
    vpcNames = []
    igwNames = []
    igwIDs = []
    regions = []
    #Region
    region_dict = {'us-east-1': 'N. Virginia', 'us-east-2': 'Ohio', 'N. California': 'us-west-1', 'us-west-2': 'Oregon', 'af-south-1': 'Cape Town', 'ap-east-1': 'Hong Kong', 'ap-south-1': 'Mumbai', 'ap-northeast-2': 'Seoul', 'ap-southeast-1': 'Singapore', 'ap-southeast-2': 'Sydney', 'ap-northeast-1': 'Tokyo', 'ca-central-1': 'Central', 'eu-central-1': 'Frankfurt', 'eu-west-1': 'Ireland', 'eu-west-2': 'London', 'eu-south-1': 'Milan', 'eu-west-3': 'Paris', 'eu-north-1': 'Stockholm', 'me-south-1': 'Bahrain', 'sa-east-1': 'Sao Paulo'}
    region = boto3._get_default_session().region_name

    for vpc in vpcs:
        if vpc['IsDefault'] == True:
            continue
        id = hp.getFromJSON(vpc,'VpcId')
        cidr = hp.getFromJSON(vpc,'CidrBlock')
        vpcIDs.append(id)
        vpcCIDRs.append(cidr)
        name = hp.findNameinTags(vpc)
        vpcNames.append(name)
        regions.append(region_dict[region])
        # IGW
        filters = [{'Name': "attachment.vpc-id", 'Values': [id]}]
        igws = client.describe_internet_gateways(Filters=filters)['InternetGateways']
        if igws:
            igw = igws[0]
            name = hp.findNameinTags(igw)
            igwNames.append(name)
            igwId = igw['InternetGatewayId']
            igwIDs.append(igwId)

    vpcdf = pd.DataFrame({"Region": regions, "VPC Name": vpcNames, "VPC ID": vpcIDs, "CIDR": vpcCIDRs})
    igwdf = pd.DataFrame({"IGW Name": igwNames, "IGW ID": igwIDs})

    #Subnet
    filters = [{'Name': "vpc-id", 'Values': vpcIDs}]
    subnetdf, vpcrtdf = describe_subnet(filters, client)

    #NAT
    filters = [{'Name': "vpc-id", 'Values': vpcIDs}]
    natdf = describe_nat(filters, client)

    #VPC Flow Log
    filters = [{'Name': "resource-id", 'Values': vpcIDs}]
    flowdf = describe_flow(filters, client)

    return vpcdf, subnetdf, vpcrtdf, igwdf, natdf, flowdf
