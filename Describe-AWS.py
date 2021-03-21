import boto3
import argparse
import pandas as pd
from describer import elb_describer as elb_db, cloudfront_describer as cf_db, ec2_describer as ec2_db, db_helpers as hp, \
    vpc_describer as vpc_db, cloudtrail_describer as cloudtrail_db, iam_describer as iam_db, sg_describer as sg_db, rds_describer as rds_db, \
    lambda_describer as lb_db, cache_describer as ecahe_db, s3_describer as s3_db, sns_describer as sns_db, route53_describer as route53_db, \
    acm_describer as acm_db, asg_describer as asg_db

from botocore.exceptions import ClientError
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session

# List of Services:
# IAM, CloudTrail, VPC, EC2, RDS, Lambda, ElastiCache, CloudFront, ELB, S3, SNS, Route53
##########################################################################################################################################


class AutoRefreshRole():
    '''A role that can auto-refresh'''

    def __init__(self, target_role_arn: str, region: str):
        sts_client = boto3.client('sts', region_name=region,
                                  endpoint_url="https://sts.{}.amazonaws.com".format(region))
        self.sts_client = sts_client
        session_name = sts_client.get_caller_identity()['Arn'].split(":")[
            5].split("/")[1]
        self.role_arn = target_role_arn
        self.session_name = session_name
        # Create Refrehable Credentials
        refreshable = RefreshableCredentials.create_from_metadata(
            metadata=self._refresh(),
            refresh_using=self._refresh,
            method="sts-assume-role"
        )
        self.refreshable_cred = refreshable
        pass

    def _refresh(self):
        response = self.sts_client.assume_role(
            RoleArn=self.role_arn, RoleSessionName=self.session_name, DurationSeconds=3600).get("Credentials")
        credentials = {
            "access_key": response.get("AccessKeyId"),
            "secret_key": response.get("SecretAccessKey"),
            "token": response.get("SessionToken"),
            "expiry_time": response.get("Expiration").isoformat(),
        }
        return credentials

    def getCredentials(self):
        return self.refreshable_cred


def mfaLogin():
    region = boto3.DEFAULT_SESSION.region_name
    if not region:
        region = "us-east-1"
    client = boto3.client('sts', region_name=region,
                          endpoint_url="https://sts.{}.amazonaws.com".format(region))
    mfa = client.get_caller_identity()['Arn'].replace('user', 'mfa')
    print(mfa)
    mfa_TOTP = input("Enter the MFA code: ")
    response = client.get_session_token(
        DurationSeconds=3600*3,
        SerialNumber=mfa,
        TokenCode=mfa_TOTP,
    )
    return response["Credentials"]


def swtichRole(target_role_arn):
    region = boto3.DEFAULT_SESSION.region_name
    if not region:
        region = "us-east-1"
    autorefreshrole = AutoRefreshRole(
        target_role_arn=target_role_arn, region=region)
    cred = autorefreshrole.getCredentials()
    session = get_session()
    session._credentials = cred
    session.set_config_variable("region", region)
    return session


def main(argv):

    # parse argument
    if args.output == "outputs":
        print("No Excel Name Provided. Use Default Value: outputs")
    excelname = args.output + ".xlsx"

    # Crendentials: (AK, SK) or Profile or Switch Role ARN
    # Option: MFA, Region
    if args.access is not None and args.secret is not None and args.profile is not None:
        print("AK, SK, and profile name all detected. Will use AK/SK pair")

    if args.access is not None and args.secret is not None:
        print("AWS Credential provided")
        boto3.setup_default_session(
            aws_access_key_id=args.access, aws_secret_access_key=args.secret, region_name=args.region)
    elif args.profile is not None:
        print("AWS Credential profile provided")
        boto3.setup_default_session(
            profile_name=args.profile, region_name=args.region)

    else:
        print("No complete AWS Credential provided, will default profile set with AWS CLI")

    if args.mfa:
        print("Require MFA")
        cred = mfaLogin()
        boto3.setup_default_session(
            aws_access_key_id=cred["AccessKeyId"], aws_secret_access_key=cred["SecretAccessKey"], aws_session_token=cred["SessionToken"], region_name=args.region)
    if args.role:
        print("Switching Role")
        session = swtichRole(args.role)
        boto3.setup_default_session(botocore_session=session)

    print("Start VPC...")
    vpc, subnet, vpcrt, igw, nat, flow = vpc_db.describe()
    cgw, vgw, vpn = vpc_db.describe_VPN()
    print("Finish VPC")

    print("Start IAM...")
    iam = iam_db.describe()
    print("Finish IAM")

    print("Start CloudTrail...")
    trail = cloudtrail_db.describe()
    print("Finish CloudTrail")

    print("Start EC2...")
    ec2 = ec2_db.describe()
    sg = sg_db.describe()
    eip = ec2_db.describe_EIP()
    print("Finish EC2")

    print("Start Load Balancer...")
    clb = elb_db.describe_CLB()
    elb, listener, tg = elb_db.describe_ELB()
    print("Finish Load Balancer")

    print("Start Route 53...")
    route = route53_db.describe()
    route['Expiry Date'] = route['Expiry Date'].apply(
        lambda a: pd.to_datetime(a).date())
    print("Finish Route 53")

    print("Start S3...")
    s3 = s3_db.describe()
    print("Finish S3")

    print("Start SNS...")
    sns = sns_db.describe()
    print("Finish SNS")

    print("Start RDS...")
    rds = rds_db.describe()
    print("Finish RDS")

    print("Start Lambda...")
    lambdas = lb_db.describe()
    print("Finish Lambda")

    print("Start ElastiCache...")
    cache = ecahe_db.describe()
    print("Finish ElastiCache")

    print("Start CloudFront...")
    cf = cf_db.describe()
    print("Finish CloudFront")
    print("Start ACM...")
    acm = acm_db.describe()
    print("Finish ACM")

    print("Start ASG...")
    asg = asg_db.describe()
    print("Finish ASG")

    if not args.dry:
        with pd.ExcelWriter(excelname) as writer:
            hp.writeToExcel(writer, vpc, 'VPC')
            hp.writeToExcel(writer, subnet, 'Subnet')
            hp.writeToExcel(writer, vpcrt, 'RouteTable')
            hp.writeToExcel(writer, igw, 'IGW')
            hp.writeToExcel(writer, nat, 'NAT Gateway')
            hp.writeToExcel(writer, flow, 'VPC Flow Log')
            hp.writeToExcel(writer, cgw, 'CGW')
            hp.writeToExcel(writer, vgw, 'VGW')
            hp.writeToExcel(writer, vpn, 'VPN')
            hp.writeToExcel(writer, iam, 'IAM')
            hp.writeToExcel(writer, trail, 'CloudTrail')
            hp.writeToExcel(writer, ec2, 'EC2')
            hp.writeToExcel(writer, sg, 'Security Group')
            hp.writeToExcel(writer, eip, 'EIP')
            hp.writeToExcel(writer, clb, 'CLB')
            hp.writeToExcel(writer, elb, 'ELB')
            hp.writeToExcel(writer, listener, 'ELB Listener')
            hp.writeToExcel(writer, tg, 'ELB Target Group')
            hp.writeToExcel(writer, route, 'Route 53')
            hp.writeToExcel(writer, s3, 'S3')
            hp.writeToExcel(writer, sns, 'SNS')
            hp.writeToExcel(writer, rds, 'RDS')
            hp.writeToExcel(writer, lambdas, 'Lambda')
            hp.writeToExcel(writer, cache, 'ElastiCache')
            hp.writeToExcel(writer, cf, 'CloudFront')
            hp.writeToExcel(writer, acm, 'ACM')
            hp.writeToExcel(writer, asg, 'ASG')
        print("Finish saving excel")
    else:
        print(vpc.to_string())
        print(subnet.to_string())
        print(vpcrt.to_string())
        print(igw.to_string())
        print(nat.to_string())
        print(flow.to_string())
        print(cgw.to_string())
        print(vgw.to_string())
        print(vpn.to_string())
        print(iam.to_string())
        print(trail.to_string())
        print(ec2.to_string())
        print(sg.to_string())
        print(eip.to_string())
        print(clb.to_string())
        print(elb.to_string())
        print(listener.to_string())
        print(tg.to_string())
        print(route.to_string())
        print(s3.to_string())
        print(sns.to_string())
        print(rds.to_string())
        print(lambdas.to_string())
        print(cache.to_string())
        print(cf.to_string())
        print(acm.to_string())
        print("Finish Dry Run")
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Describe the following AWS service and output to an Excel File: IAM, CloudTrail, VPC, EC2, RDS, Lambda, ElastiCache, CloudFront, ELB, S3, SNS, Route53.")
    parser.add_argument(
        "output", help="The Desired Excel Output Filename. Default = outputs.xlsx",
        type=str, default="outputs", nargs='?'
    )
    parser.add_argument(
        "-k", "--access-key", help="The AWS Account Access Key", dest="access", default=None
    )
    parser.add_argument(
        "-s", "--secret-access-key",
        help="The AWS Account Secret Access Key", dest="secret", default=None
    )
    parser.add_argument(
        "--profile", help="The AWS Credential Profile Name", dest="profile", default=None
    )
    parser.add_argument(
        "--mfa", help="Use this flag if need MFA", action="store_true", dest="mfa"
    )
    parser.add_argument(
        "--role-arn", help="Enter the Role ARN to switch to if needed", dest="role", default=None
    )
    parser.add_argument(
        "--region", help="Set the Region to Parse", dest="region", default=None
    )
    parser.add_argument(
        "--dry-run", help="Use this flag for test run", action='store_true', dest="dry")
    args = parser.parse_args()
    main(args)
