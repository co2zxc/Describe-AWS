from describer import db_helpers as hp
import pandas as pd
import numpy as np


#TODO: currently returning the first 400 clbs
def describe_CLB():
    #client = boto3.client('elb')
    client = hp.getBotoClient('elb')
    clbs = client.describe_load_balancers()['LoadBalancerDescriptions']

    # placeholder for clb
    names, dnses, schemes, vpcs, listenerProtocols, listenerPorts, instanceProtocols, instancePorts, ssls, azes, subnetIds,securitys, registereds, healthTargets,  healthIntervals, healthTimeouts, unhealthys, healthys= [], [],[],[], [], [], [], [], [], [], [], [], [], [], [], [], [], []
    for clb in clbs:
        name = hp.getFromJSON(clb, 'LoadBalancerName')
        dns = hp.getFromJSON(clb, 'DNSName')
        scheme = hp.getFromJSON(clb, 'Scheme')
        vpc = hp.getFromJSON(clb, 'VPCId')
        azs = hp.listToString(hp.getFromJSON(clb,'AvailabilityZones'), None)
        subnets = hp.listToString(hp.getFromJSON(clb, 'Subnets'), None)
        sgs = hp.listToString(hp.getFromJSON(clb, 'SecurityGroups'), None)
        instances = hp.getFromJSON(clb, 'Instances')
        instances = hp.listToString(instances, 'InstanceId')
        healthCheck = hp.getFromJSON(clb, 'HealthCheck')
        target = hp.getFromJSON(healthCheck, 'Target')
        interval = hp.getFromJSON(healthCheck, 'Interval')
        timeout = hp.getFromJSON(healthCheck, 'Timeout')
        unhealthy = hp.getFromJSON(healthCheck, 'UnhealthyThreshold')
        healthy = hp.getFromJSON(healthCheck, 'HealthyThreshold')
        listeners = hp.getFromJSON(clb, 'ListenerDescriptions')
        for listener in listeners:
            listener = hp.getFromJSON(listener, 'Listener')
            protocol = hp.getFromJSON(listener,'Protocol')
            port = hp.getFromJSON(listener, 'LoadBalancerPort')
            instanceProtocol = hp.getFromJSON(listener,'InstanceProtocol')
            instancePort = hp.getFromJSON(listener,'InstancePort')
            sslid = hp.getFromJSON(listener, 'SSLCertificateId')
            ssl = sslid+" ("+hp.getDomainsFromACM(sslid)+")"
            names.append(name)
            dnses.append(dns)
            schemes.append(scheme)
            vpcs.append(vpc)
            registereds.append(instances)
            azes.append(azs)
            subnetIds.append(subnets)
            securitys.append(sgs)
            listenerProtocols.append(protocol)
            listenerPorts.append(port)
            instanceProtocols.append(instanceProtocol)
            instancePorts.append(instancePort)
            ssls.append(ssl)
            healthTargets.append(target)
            healthIntervals.append(interval)
            healthTimeouts.append(timeout)
            unhealthys.append(unhealthy)
            healthys.append(healthy)
            #TODO: Change security group -> name
            #      Change instance -> instance name
    df = pd.DataFrame({"CLB Name": names, "CLB DNS": dnses, "Internal/Internet Facing": schemes, "VPC": vpcs, "Registered Instances": registereds, "AZ": azes, "Subnet": subnetIds, "Security Group": securitys, "Listener Protocol": listenerProtocols, "Listener Port": listenerPorts, "Instance Protocol": instancePorts, "SSL": ssls, "Health Check": healthTargets, "Health Check Interval": healthIntervals, "Health Check Timeout": healthTimeouts, "Unhealthy Threshold": unhealthys, "Healthy Threshold": healthys})
    return df
# For ALB/NLB
def describe_ELB():
    #TODO: Change sg -> name
    #             instance -> name

    # client = boto3.client('elbv2')
    client = hp.getBotoClient('elbv2')
    elbs = client.describe_load_balancers()['LoadBalancers']

    #place holder for elb
    elbname, elbdns, elbscheme, elbVpc, elbType, elbAZ, elbSubnet, elbSG = [],[],[], [], [], [], [], []
    #place holder for listener
    listenerProtocol,listenerPort,listenerDefaultSSL,listenerOtherSSL,listenerElb = [],[],[], [], []
    #place holder for tg
    targetELB, targetNames, protocols, ports, unhealthys, healthys, healthpaths, healthports, healthprotocols, healthTimeouts, healthIntervals, registereds = [],[],[], [], [], [], [], [], [], [], [], []
    targettypes = []
    for elb in elbs:
        name = hp.getFromJSON(elb, 'LoadBalancerName')
        dns = hp.getFromJSON(elb, 'DNSName')
        scheme = hp.getFromJSON(elb, 'Scheme')
        vpc = hp.getFromJSON(elb, 'VpcId')
        type = hp.getFromJSON(elb, 'Type')
        azs = hp.listToString(hp.getFromJSON(elb, 'AvailabilityZones'),'ZoneName')
        subnets = hp.listToString(hp.getFromJSON(elb, 'AvailabilityZones'),'SubnetId')
        sgs = hp.listToString(hp.getFromJSON(elb, 'SecurityGroups'), None)
        arn = hp.getFromJSON(elb,'LoadBalancerArn')
        elbname.append(name)
        elbdns.append(dns)
        elbscheme.append(scheme)
        elbType.append(type)
        elbVpc.append(vpc)
        elbAZ.append(azs)
        elbSubnet.append(subnets)
        elbSG.append(sgs)
        # Listeners
        listeners = client.describe_listeners(LoadBalancerArn=arn)['Listeners']
        for listener in listeners:
            protocol = hp.getFromJSON(listener, 'Protocol')
            port = hp.getFromJSON(listener, 'Port')
            sslids = hp.getFromJSON(listener, 'Certificates')
            default_ssl = np.NaN
            other_ssls = []
            if not hp.isEmpty(sslids):
                for sslid in sslids:
                    ssl = hp.getFromJSON(sslid, 'CertificateArn')
                    ssl = ssl+ " ("+hp.getDomainsFromACM(ssl)+")"
                    if hp.getFromJSON(sslid, 'IsDefault'):
                        default_ssl = ssl
                    else:
                        other_ssls.append(ssl)
            other_ssls = hp.listToString(other_ssls, None)
            listenerElb.append(name)
            listenerProtocol.append(protocol)
            listenerPort.append(port)
            listenerDefaultSSL.append(default_ssl)
            listenerOtherSSL.append(other_ssls)
        # Target Group
        targets = client.describe_target_groups(LoadBalancerArn=arn)['TargetGroups']
        for target in targets:
            targetName = hp.getFromJSON(target,'TargetGroupName')
            protocol = hp.getFromJSON(target, 'Protocol')
            port = hp.getFromJSON(target, 'Port')
            arn = hp.getFromJSON(target, 'TargetGroupArn')
            targetType = hp.getFromJSON(target, 'TargetType')
            #Health Check
            unhealthy = hp.getFromJSON(target, 'UnhealthyThresholdCount')
            healthy = hp.getFromJSON(target, 'HealthyThresholdCount')
            healthpath = hp.getFromJSON(target, 'HealthCheckPath')
            healthport = hp.getFromJSON(target, 'HealthCheckPort')
            healthprotocol = hp.getFromJSON(target, 'HealthCheckProtocol')
            healthTimeout = hp.getFromJSON(target,'HealthCheckTimeoutSeconds')
            healthInterval = hp.getFromJSON(target,'HealthCheckIntervalSeconds')

            #Instances
            healths = client.describe_target_health(TargetGroupArn=arn)['TargetHealthDescriptions']
            instances = []
            for health in healths:
                instance = hp.getFromJSON(health, 'Target')
                instanceId = hp.getFromJSON(instance, 'Id')
                instances.append(instanceId)
            instances = hp.listToString(instances, None)
            targetELB.append(name)
            targetNames.append(targetName)
            protocols.append(protocol)
            ports.append(port)
            unhealthys.append(unhealthy)
            healthys.append(healthy)
            healthpaths.append(healthpath)
            healthports.append(healthport)
            healthprotocols.append(healthprotocol)
            healthTimeouts.append(healthTimeout)
            healthIntervals.append(healthInterval)
            registereds.append(instances)
            targettypes.append(target['TargetType'])

    elbdf = pd.DataFrame({"ELB Name": elbname, "Type": elbType, "DNS": elbdns, "Internal/Internet Facing": elbscheme, "VPC": elbVpc, "AZ": elbAZ, "Subnet": elbSubnet, "SG":elbSG})
    listenerdf = pd.DataFrame({"ELB Name": listenerElb, "Protocol": listenerProtocol, "Port": listenerPort, "Default Cert": listenerDefaultSSL, "Other Certs": listenerOtherSSL})
    tgdf = pd.DataFrame({"ELB Name": targetELB, "Target Group Name": targetNames, "Protocol": protocols, "Port": ports, "Registered Instances": registereds,"Healthy Threshold": healthys,"Unhealthy Threshold": unhealthys, "Health Check Path": healthpaths, "Health Check Protocol": healthprotocols, "Health Check Port": healthports, "Health Check Timeout": healthTimeouts, "Health Check Interval": healthIntervals, 'Target Type':targettypes})
    return elbdf, listenerdf,tgdf