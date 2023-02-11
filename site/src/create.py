import os
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Key

from utils.decorators import cors_headers, json_http_resp, load_json_body

dynamodb = boto3.resource('dynamodb')
sites_table = dynamodb.Table(os.environ['SITES_TABLE'])


@cors_headers
@json_http_resp
@load_json_body
def create(event, context):
    data = event['body']
    if 'id' not in data:
        return {
            "statusCode": 400,
            "body": {
                "message": "id is required"
            }
        }
    timestamp = str(datetime.utcnow())
    data['createdAt'] = timestamp
    data['updatedAt'] = timestamp
    data['username'] = event['requestContext']['authorizer']['jwt']['claims']['username']
    try:
        sites_table.put_item(Item=data,
                             ConditionExpression='attribute_not_exists(id)')
    except Exception:
        return {
            "statusCode": 400,
            "body": {"message": "site exists"}
        }
    return {
        "statusCode": 201,
        "body": data
    }
