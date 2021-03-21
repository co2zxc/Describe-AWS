from describer import db_helpers as hp
import pandas as pd


def get_target_group_name(arns):
    client = hp.getBotoClient('elbv2')
    response = client.describe_target_groups(TargetGroupArns=arns)
    tg_names = []
    for tg in response['TargetGroups']:
        tg_names.append(tg['TargetGroupName'])
    return ','.join(tg_names)


# TODO: currently only find the first 100 clusters
def describe():
    #client = boto3.client('elasticache')
    client = hp.getBotoClient('autoscaling')

    # For Memcached
    asgs = client.describe_auto_scaling_groups()['AutoScalingGroups']
    LaunchConfigurations, TargetGroups, Mins, Maxs = [], [], [], []
    for asg in asgs:
        if 'LaunchConfigurationName' in asg:
            LaunchConfigurations.append(asg['LaunchConfigurationName'])
        else:
            LaunchConfigurations.append('')
        TargetGroups.append(get_target_group_name(asg['TargetGroupARNs']))
        Mins.append(asg['MinSize'])
        Maxs.append(asg['MaxSize'])
    

    df= pd.DataFrame({'Launch Configuration':LaunchConfigurations, 'Min':Mins, 'Max':Maxs, 'Target Groups':TargetGroups})
    return df