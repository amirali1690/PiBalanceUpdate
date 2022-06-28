"""
lambda function to get pi cases balance from sqs and insert them to database.
"""
import os
import logging
import ast
import boto3
import pymysql
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
def lambda_handler(event, context):
    """
    gets pi cases balance from sqs and insert them to database.
    """
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('## EVENT')
    logger.info(event,context)
    connection = pymysql.connect(host=os.getenv('RDS_HOST'),
                                user = os.getenv('RDS_USER'),
                                password = os.getenv('RDS_PASSWORD'),
                                database = os.getenv('RDS_DB'),
                                port = 3306,
                                cursorclass= pymysql.cursors.DictCursor)
    cursor =connection.cursor()
    client = boto3.client('sqs',region_name='us-west-2',
                    endpoint_url='https://sqs.us-west-2.amazonaws.com')
    queueInfo = client.get_queue_url(QueueName='PiBalance')
    response = client.receive_message(
                        QueueUrl = queueInfo['QueueUrl'],
                        AttributeNames=['All'],
                        MaxNumberOfMessages = 10
                    )

    while 'Messages' in response.keys() and (len(response['Messages']))>0:
        for message in response['Messages']:
            print(message['Body'])
            caseInfo = ast.literal_eval(message['Body'])
            caseId = caseInfo['caseId']
            initialvisit = caseInfo['initialvisit']
            lastvisit = caseInfo['lastvisit']
            for clinic in caseInfo['clinics'].keys():
                if caseInfo['clinics'][clinic] is None or caseInfo['clinics'][clinic]=='None':
                    caseInfo['clinics'][clinic]='0.00'
                sql = """UPDATE case_offices CO
                         LEFT JOIN clinics CL ON CL.id=CO.office_id
                         SET CO.balance = %s WHERE CO.case_id=%s AND CL.name=%s"""
                sql2 = 'UPDATE cases SET dateOfLastOfficeVisit=%s, firstDayDate=%s WHERE id=%s'
                cursor.execute(sql,(caseInfo['clinics'][clinic],caseId,clinic))
                cursor.execute(sql2,(lastvisit,initialvisit,caseId))
                connection.commit()
                client.delete_message(
                    QueueUrl = queueInfo['QueueUrl'],
                    ReceiptHandle= message['ReceiptHandle']
                )
        # keep polling messages from SQS till there is no more messages left
        client.receive_message(
                    QueueUrl = queueInfo['QueueUrl'],
                    AttributeNames=['All'],
                    MaxNumberOfMessages = 10
                )
    return True
