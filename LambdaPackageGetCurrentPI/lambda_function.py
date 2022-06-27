import os
import pymysql
import boto3
import logging
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

    
    caseList=[]
    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT C.id,CL.name,P.firstName,P.lastName,C.dateOfLastOfficeVisit FROM cases C LEFT JOIN case_offices CO ON CO.case_id=C.id LEFT JOIN clinics CL ON CL.id=CO.office_id LEFT JOIN patients P ON P.id=C.patient_id WHERE C.status='CurrentPatient';"
            cursor.execute(sql,)
            cases = cursor.fetchall()
            for case in cases:
                if case['name']=='South Chandler':
                    case['name']='Ocotillo'
                caseList.append('{"caseId":"'+str(case['id'])+'","firstname":"'+case['firstName']+'", "lastname":"' +case['lastName']+'","clinic":"'+case['name']+'"}')
    client = boto3.client('sqs',region_name='us-west-2',endpoint_url='https://sqs.us-west-2.amazonaws.com')
    for case in caseList:
        response = client.send_message(
                            QueueUrl = 'https://sqs.us-west-2.amazonaws.com/849779278892/PiCurrent',
                            MessageBody=case
                        )
    return True