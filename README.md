#Ddescribe-AWS

This is a Python Module that gather various information of different AWS resources and generate an CSV file.

Describe the following AWS service and output to an Excel File: IAM,
CloudTrail, VPC, EC2, RDS, Lambda, ElastiCache, CloudFront, ELB, S3, SNS,
Route53.

## Basic Usage

1. Install Python 3 (check your installation using python --version or python3 --version)
2. Install neccessary package through pip or pip3
    ```=sh
    pip install -r requirements.txt
    ```
3. Setup the AWS Credentials in a AWS CLI Profile
   ```=sh
   aws  configure --profile <profile-name>
   ```
4. Run this script to get the output
   ```=sh
   python describeAWS.py --profile <profile-name>
   ```
5. For more info, you can get help message by running
   ```=sh
   python describeAWS.py --help
   ```