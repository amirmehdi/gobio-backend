import os

import boto3

from lib.decorators import json_http_resp

dynamodb = boto3.resource('dynamodb')
sites_table = dynamodb.Table(os.environ['SITES_TABLE'])


@json_http_resp
def get(event, context):
    result = sites_table.get_item(
        Key={
            'id': event['pathParameters']['id']
        }
    )
    if 'Item' in result:
        return {
            "statusCode": 200,
            "body": result['Item']
        }
    return {
        "statusCode": 404,
        "body": {
            "message": "site not found"
        }
    }
