from describer import db_helpers as hp
import pandas as pd
import numpy as np

def get_security_group_name(sgs):
    ret = []
    for sg in sgs:
        ret.append(sg['VpcSecurityGroupId'])
    return ','.join(ret)

def describe():
    client = hp.getBotoClient('rds')
    #placeholder
    names, dbNames, endpoints, rendpoints, multiAZs, engines, engineVersions, ports, masterUsers, sgs, instanceClasses = [],[],[],[],[],[],[],[],[],[],[]
    DBids, storage_types, storage_sizes, MaxAllocatedStorages, DBSecurityGroups, DeletionProtections, PerformanceInsightsEnableds, EnabledCloudwatchLogsExports = [],[],[],[],[],[],[],[]

    # Aurora　Cluster
    #TODO: currently only show the first 100
    clusters = client.describe_db_clusters()['DBClusters']
    for cluster in clusters:
        name = hp.getFromJSON(cluster, 'DBClusterIdentifier')
        dbName = hp.getFromJSON(cluster, 'DatabaseName')
        endpoint= hp.getFromJSON(cluster,'Endpoint')
        rendpoint= hp.getFromJSON(cluster,'ReaderEndpoint')
        multiAZ = hp.getFromJSON(cluster,'MultiAZ')
        engine = hp.getFromJSON(cluster,'Engine')
        engineVersion = hp.getFromJSON(cluster, 'EngineVersion')
        port = hp.getFromJSON(cluster, 'Port')
        masterUser = hp.getFromJSON(cluster, 'MasterUsername')
        sg = hp.getFromJSON(cluster, 'VpcSecurityGroups')
        sg = hp.listToString(sg,'VpcSecurityGroupId')
        arn = hp.getFromJSON(cluster, 'DBClusterArn')
        instances = client.describe_db_instances(Filters=[{'Name': "db-cluster-id", "Values":[arn]}])['DBInstances']
        instanceClass = hp.listToString(instances, 'DBInstanceClass')

        names.append(name)
        dbNames.append(dbName)
        endpoints.append(endpoint)
        rendpoints.append(rendpoint)
        multiAZs.append(multiAZ)
        engines.append(engine)
        engineVersions.append(engineVersion)
        ports.append(port)
        masterUsers.append(masterUser)
        sgs.append(sg)
        instanceClasses.append(instanceClass)
        DBids.append('')
        storage_types.append('')
        storage_sizes.append('')
        MaxAllocatedStorages.append('')
        DBSecurityGroups.append(get_security_group_name(cluster['VpcSecurityGroups']))
        DeletionProtections.append(cluster['DeletionProtection'])
        PerformanceInsightsEnableds.append('N/A')
        if 'EnabledCloudwatchLogsExports' in cluster:
            EnabledCloudwatchLogsExports.append(','.join(cluster['EnabledCloudwatchLogsExports']))
        else:
            EnabledCloudwatchLogsExports.append('')
        


    # RDS Instance
    # TODO: currently only showing the first 100
    instances = client.describe_db_instances()['DBInstances']
    for instance in instances:
        engine = hp.getFromJSON(instance,'Engine')
        if engine == "aurora":
            continue
        name = hp.getFromJSON(instance,'DBInstanceIdentifier')
        instanceClass = hp.getFromJSON(instance, 'DBInstanceClass')
        dbName = hp.getFromJSON(instance,'DBName')
        endpoint=hp.getFromJSON(hp.getFromJSON(instance,'Endpoint'), 'Address')
        port = hp.getFromJSON(hp.getFromJSON(instance,'Endpoint'), 'Port')
        multiAZ = hp.getFromJSON(instance,'MultiAZ')
        engineVersion = hp.getFromJSON(instance, 'EngineVersion')
        masterUser = hp.getFromJSON(instance,'MasterUsername')
        sg = hp.getFromJSON(instance, 'VpcSecurityGroups')
        sg = hp.listToString(sg,'VpcSecurityGroupId')

        names.append(name)
        dbNames.append(dbName)
        endpoints.append(endpoint)
        rendpoints.append(np.NaN)
        multiAZs.append(multiAZ)
        engines.append(engine)
        engineVersions.append(engineVersion)
        ports.append(port)
        masterUsers.append(masterUser)
        sgs.append(sg)
        instanceClasses.append(instanceClass)
        DBids.append(instance['DbiResourceId'])
        storage_types.append(instance['StorageType'])
        storage_sizes.append(instance['AllocatedStorage'])
        if 'MaxAllocatedStorage' in instance:
            MaxAllocatedStorages.append(instance['MaxAllocatedStorage'])
        else:
            MaxAllocatedStorages.append('')
        DBSecurityGroups.append(get_security_group_name(instance['VpcSecurityGroups']))
        DeletionProtections.append(instance['DeletionProtection'])
        PerformanceInsightsEnableds.append(instance['PerformanceInsightsEnabled'])
        if 'EnabledCloudwatchLogsExports' in instance:
            EnabledCloudwatchLogsExports.append(','.join(instance['EnabledCloudwatchLogsExports']))
        else:
            EnabledCloudwatchLogsExports.append('')

        

    df = pd.DataFrame({"Identifier": names, "Engine": engines, "Engine Version": engineVersions, "Multi AZ": multiAZs, \
    "Endpoint": endpoints, "Reader Endpoint": rendpoints, "DB Name": dbNames,"Port": ports ,"User Name": masterUsers, \
    "Security Group": sgs, "Instance Class": instanceClasses, "DB instance id": DBids, "Storage type": storage_types, \
        "Storage Size": storage_sizes, "Maximum storage threshold": MaxAllocatedStorages, "Deletion protection" : DeletionProtections, \
        "Performance Insights enabled": PerformanceInsightsEnableds, "CloudWatch Logs": EnabledCloudwatchLogsExports
    })
    return df