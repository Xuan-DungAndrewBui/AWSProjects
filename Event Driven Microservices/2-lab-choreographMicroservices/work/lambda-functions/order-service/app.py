import boto3
import os
import json
import uuid
from datetime import datetime 
import logging

'''
Lambda func for order service
'''
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def save_to_db(id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.getenv("TABLE_NAME"))
    '''
    [TASK] Save the data into database ONLY by passing the ID
    Create a field called time_order_service and passing the current timestamp with format "MONTH-DAY-YEAR HOUR:MINUTES:SECONDS"
    '''
    table.update_item(
        Key = { 'ID': id },
        UpdateExpression = "set time_order_service=:tos",
        ExpressionAttributeValues = {
            ':tos': datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        }
    )


def lambda_handler(event, context):
    logger.info(event)
    try:
        id = str(uuid.uuid4())
        '''
        [TASK] Create a dictionary object to hold all data to pass to Amazon EventBridge
        Make sure that you pass the id variable into the data
        '''
        data = {}
        data['metadata'] = {"service": "demo-eventbridge"}
        data['data'] = {}          
        data['data']['ID'] = id	

        '''
        [TASK] Send event to Amazon EventBridge
        Also include the data into Detail by dumping into JSON format
        '''
        client = boto3.client('events')
        response = client.put_events(
            Entries = [
                {
                    'Source': 'order_service',
                    'DetailType': 'order_created',
                    'Detail': json.dumps(data),
                    'EventBusName': os.getenv("EVENT_BUS_NAME")
                }
            ]
        )
        logger.info(response)
        '''
        [TASK] Save the data into database ONLY by passing the ID
        '''
        save_to_db(id)
        response = {'statusCode': 200, 'body': json.dumps({"status":"order_created"})}
        return response
    except Exception as e:
        logger.info(e)
        response = {'statusCode': 500, 'body': json.dumps({"status":"order_creation_failed"})} 
        return response

