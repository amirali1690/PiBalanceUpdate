import os
import pymysql
import boto3
import logging
import ast
import json
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)




def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('## EVENT')
    logger.info(event)


    connection = pymysql.connect(host=os.getenv('RDS_HOST'),
                                user = os.getenv('RDS_USER'),
                                password = os.getenv('RDS_PASSWORD'),
                                database = os.getenv('RDS_DB'),
                                port = 3306,
                                cursorclass= pymysql.cursors.DictCursor)

    cursor =connection.cursor()
    client = boto3.client('sqs',region_name='us-west-2',endpoint_url='https://sqs.us-west-2.amazonaws.com')
    response = client.receive_message(
                        QueueUrl = 'https://sqs.us-west-2.amazonaws.com/849779278892/PiBalance',
                        AttributeNames=['All'],
                        MaxNumberOfMessages = 10
                    )

    while 'Messages' in response.keys() and (len(response['Messages']))>0:
        for message in response['Messages']:
            print(message['Body'])
            caseInfo = ast.literal_eval(message['Body'])
            id = caseInfo['caseId']
            initialvisit = caseInfo['initialvisit']
            lastvisit = caseInfo['lastvisit']
            clinics = caseInfo['clinics']
            for clinic in clinics.keys():
                if clinics[clinic] is None or clinics[clinic]=='None':
                    clinics[clinic]='0.00'
                sql = 'UPDATE case_offices CO LEFT JOIN clinics CL ON CL.id=CO.office_id SET CO.balance =' + clinics[clinic] +  ' WHERE CO.case_id='+id+ ' AND CL.name="'+clinic+'"'
                sql2 = 'UPDATE cases SET dateOfLastOfficeVisit="'+lastvisit+'", firstDayDate="'+initialvisit+'" WHERE id='+id
                cursor.execute(sql,)
                cursor.execute(sql2,)
                connection.commit()
                delete = client.delete_message(
                    QueueUrl = 'https://sqs.us-west-2.amazonaws.com/849779278892/PiBalance',
                    ReceiptHandle= message['ReceiptHandle']
                )

        response = client.receive_message(
                    QueueUrl = 'https://sqs.us-west-2.amazonaws.com/849779278892/PiBalance',
                    AttributeNames=['All'],
                    MaxNumberOfMessages = 10
                )
    return True