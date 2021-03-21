from describer import db_helpers as hp
import pandas as pd

# TODO: handle the case if return truncated list


def describe():
    #print("Start describing IAM")
    iam = hp.getBotoClient('iam', region_name="us-east-1")
    users = iam.list_users()['Users']
    usernames = []
    inlines = []
    attacheds = []
    for user in users:
        username = hp.getFromJSON(user, 'UserName')
        usernames.append(username)
        inline = iam.list_user_policies(UserName=username)['PolicyNames']
        attached = iam.list_attached_user_policies(UserName=username)[
            'AttachedPolicies']
        # find inline policies
        inline = hp.listToString(inline, None)
        inlines.append(inline)
        # find attached policy
        attached = hp.listToString(attached, 'PolicyName')
        attacheds.append(attached)
    df = pd.DataFrame(
        {"Username": usernames, "Inline policy": inlines, "Attached policy": attacheds})
    return df
