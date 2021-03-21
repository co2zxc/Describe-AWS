from describer import db_helpers as hp
import pandas as pd


# TODO: currently only find the first 100 clusters
def describe():
    #client = boto3.client('elasticache')
    client = hp.getBotoClient('elasticache')

    # For Memcached
    clusters = client.describe_cache_clusters(ShowCacheClustersNotInReplicationGroups=True)['CacheClusters']
    names, endpoints, ports, engines, engineversions, subnetgroups, nodeTypes, azs, sgs, maintenances, backups = [],[],[],[],[],[],[],[],[], [], []
    for cluster in clusters:
        name = hp.getFromJSON(cluster, 'CacheClusterId')
        engine = hp.getFromJSON(cluster, 'Engine')
        engineversion = hp.getFromJSON(cluster, 'EngineVersion')
        endpoint = hp.getFromJSON(hp.getFromJSON(cluster, 'ConfigurationEndpoint'), 'Address')
        port = hp.getFromJSON(hp.getFromJSON(cluster, 'ConfigurationEndpoint'), 'Port')
        subnetgroup = hp.getFromJSON(cluster, 'CacheSubnetGroupName')
        nodeType = hp.getFromJSON(cluster,'CacheNodeType')
        az = hp.getFromJSON(cluster, 'PreferredAvailabilityZone')
        sg = hp.getFromJSON(cluster, 'SecurityGroups')
        sg = hp.listToString(sg, 'SecurityGroupId')
        maintenance = hp.getFromJSON(cluster, 'PreferredMaintenanceWindow')
        backup = hp.getFromJSON(cluster, 'SnapshotWindow')
        names.append(name)
        endpoints.append(endpoint)
        ports.append(port)
        engines.append(engine)
        engineversions.append(engineversion)
        subnetgroups.append(subnetgroup)
        nodeTypes.append(nodeType)
        azs.append(az)
        sgs.append(sg)
        maintenances.append(maintenance)
        backups.append(backup)

    # For Redis
    replications = client.describe_replication_groups()['ReplicationGroups']
    for replication in replications:
        name = hp.getFromJSON(replication, 'ReplicationGroupId')
        if hp.getFromJSON(replication, 'ClusterEnabled'):
            endpoint = hp.getFromJSON(hp.getFromJSON(replication, 'ConfigurationEndpoint'), 'Address')
            port = hp.getFromJSON(hp.getFromJSON(replication, 'ConfigurationEndpoint'), 'Port')
        else:
            endpoint = hp.getFromJSON(hp.getFromJSON(hp.getFromJSON(replication, 'NodeGroups')[0], 'PrimaryEndpoint'), 'Address')
            port = hp.getFromJSON(hp.getFromJSON(hp.getFromJSON(replication, 'NodeGroups')[0], 'PrimaryEndpoint'), 'Port')

        backup = hp.getFromJSON(replication, 'SnapshotWindow')

        # Get Info from one of the cluster under the replication group
        cluster = hp.getFromJSON(replication, 'MemberClusters')[0]
        cluster = client.describe_cache_clusters(CacheClusterId=cluster)['CacheClusters'][0]
        engineversion = hp.getFromJSON(cluster,'EngineVersion')
        subnetgroup = hp.getFromJSON(cluster, 'CacheSubnetGroupName')
        sg = hp.getFromJSON(cluster, 'SecurityGroups')
        sg = hp.listToString(sg, 'SecurityGroupId')
        maintenance = hp.getFromJSON(cluster, 'PreferredMaintenanceWindow')

        names.append(name)
        endpoints.append(endpoint)
        ports.append(port)
        engines.append("redis")
        nodeType = hp.getFromJSON(replication, 'CacheNodeType')
        engineversions.append(engineversion)
        subnetgroups.append(subnetgroup)
        nodeTypes.append(nodeType)
        azs.append("Multiple")
        sgs.append(sg)
        maintenances.append(maintenance)
        backups.append(backup)

    df= pd.DataFrame({"Name": names, "Endpoint":endpoints, "Port": ports, "Engine": engines, "Engine Version": engineversions, "Subnet Group": subnetgroups, "Node Type": nodeTypes, "AZ": azs, "Security Group": sgs, "Maintenance Window": maintenances, "Back Up Window": backups})
    return df