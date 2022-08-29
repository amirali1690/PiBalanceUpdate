[![CircleCI](https://dl.circleci.com/status-badge/img/gh/amirali1690/PiBalanceUpdate/tree/master.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/amirali1690/PiBalanceUpdate/tree/master)

# PiBalanceUpdate

## Description
The project is a complete CI/CD pipelines of a system that reads data from an AWS RDS MySQL database via an AWS Lambda function on a daily basis, and upload the data to an AWS SQS queue. The SQS queue is polled by a local script and gather data related to the message, upload it to another SQS queue. The queue is polled by another AWS Lambda function and upload the data to the database.

## Tools

* aws-cli
* AWS Lambda
* AWS CloudFormation
* AWS RDS
* AWS SQS
* CircleCI
* Python packages:
  * pymysql
  * boto3


## Prerequisites

* AWS Account
* CircleCI Account


## Installation
Once you have your AWS and CircleCI account setup, fork the project to your own Github account and connect it to your CircleCI account. 
You need add your AWS credentials(keys) to your CircleCI environment.
Once everything is set, just need to push the code, and it will deploy all services on the AWS via CloudFormation template.


## Contact
If you have any questions or suggestions please contact me on Amirali1690@gmail.com
