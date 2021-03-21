from describer import db_helpers as hp
import pandas as pd
import numpy as np

def get_volume_attribute(volume_id):
    client = hp.getBotoClient('ec2')
    response = client.describe_volumes(VolumeIds=[volume_id])
    return {'DeleteOnTermination':response['Volumes'][0]['Attachments'][0]['DeleteOnTermination'],'Encrypted':response['Volumes'][0]['Encrypted']}

#use bool_list_to_string
def get_volumes_attribute(volumes_id):
    volume_list = volumes_id.split(';')
    client = hp.getBotoClient('ec2')
    response = client.describe_volumes(VolumeIds=volume_list)
    l1 = []
    l2 = []
    for vol in response['Volumes']:
        l1.append(vol['Attachments'][0]['DeleteOnTermination'])
        l2.append(vol['Encrypted'])
    
        
    return {'DeleteOnTermination':hp.bool_list_to_string(l1),'Encrypted':hp.bool_list_to_string(l2)}

def describe_EIP():
    client = hp.getBotoClient('ec2')
    eips = client.describe_addresses()['Addresses']
    #placeholder
    names, ips = [], []
    for eip in eips:
        name = hp.findNameinTags(eip)
        ip = hp.getFromJSON(eip, 'PublicIp')
        names.append(name)
        ips.append(ip)
    df = pd.DataFrame({"EIP Name": names, "EIP": ips})
    return df


def describe():
    #client = boto3.client('ec2')
    client = hp.getBotoClient('ec2')
    reservations = client.describe_instances()['Reservations']
    names = []
    instancetypes = []
    azs = []
    amis = []
    publicips = []
    publicDNSes = []
    privateips = []
    privateDNSes = []
    vpcIds = []
    subnets = []
    keys = []
    securitygroups = []
    ebsVolumes = []
    ebsSizes = []
    encrypteds, deletonterminates = [], []
    for reservation in reservations:
        instances = reservation['Instances']
        for instance in instances:
            if instance['State']['Name'] == 'terminated':
                continue
            name = hp.findNameinTags(instance)
            instanceType = hp.getFromJSON(instance,'InstanceType')
            az = hp.getFromJSON(hp.getFromJSON(instance,'Placement'),'AvailabilityZone')
            ami = hp.getFromJSON(instance,'ImageId')
            publicip = hp.getFromJSON(instance, 'PublicIpAddress')
            if not isinstance(publicip, str):
                publicip = 'N/A'
            publicDNS = hp.getFromJSON(instance, 'PublicDnsName')
            if publicDNS == '':
                publicDNS = 'N/A'
            privateip = hp.getFromJSON(instance, 'PrivateIpAddress')
            privateDNS = hp.getFromJSON(instance, 'PrivateDnsName')
            vpcId = hp.getFromJSON(instance, 'VpcId')
            subnetId = hp.getFromJSON(instance, 'SubnetId')
            key = hp.getFromJSON(instance, 'KeyName')
            sgs = hp.getFromJSON(instance, 'SecurityGroups')
            sgs = hp.listToString(sgs, 'GroupName')
            #EBS
            id = hp.getFromJSON(instance, 'InstanceId')
            filters = [{'Name': "attachment.instance-id", 'Values': [id]}]
            volumes = client.describe_volumes(Filters=filters)['Volumes']
            types = hp.listToString(volumes, 'VolumeType')
            sizes = hp.listToString(volumes,'Size')
            size_list = sizes.split(';')
            tmp = []
            for item in size_list:
                tmp.append(item + 'GB')
            sizes = ';'.join(tmp)
            ebs_id = hp.listToString(volumes,'VolumeId')
            names.append(name)
            instancetypes.append(instanceType)
            azs.append(az)
            amis.append(ami)
            publicips.append(publicip)
            publicDNSes.append(publicDNS)
            if privateip == np.NaN:
                privateip = 'N/A'
            privateips.append(privateip)
            privateDNSes.append(privateDNS)
            vpcIds.append(vpcId)
            subnets.append(subnetId)
            keys.append(key)
            securitygroups.append(sgs)
            ebsVolumes.append(types)
            ebsSizes.append(sizes)
            ebs_attr = get_volumes_attribute(ebs_id)
            # ebs_attr = get_volume_attribute(ebs_id)
            encrypteds.append(ebs_attr['Encrypted'])
            deletonterminates.append(ebs_attr['DeleteOnTermination'])
    print(publicDNSes)
    df = pd.DataFrame({"EC2 Name": names, "Instance Type": instancetypes, "AZ": azs, "AMI": amis, "Public IP": publicips, "Public DNS": publicDNSes, "Private IP": privateips, "Private DNS": privateDNSes, "VPC ID": vpcIds, "Subnet ID": subnets, "Key": keys,"Security Groups": securitygroups, "EBS Type": ebsVolumes, "EBS Size": ebsSizes,  "Encrypted": encrypteds})
    return df