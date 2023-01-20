import os
from datetime import datetime

import boto3

from lib.decorators import cors_headers, json_http_resp, load_json_body

dynamodb = boto3.resource('dynamodb')
sites_table = dynamodb.Table(os.environ['SITES_TABLE'])
user_sites_table = dynamodb.Table(os.environ['USER_SITES_TABLE'])


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
    site_id = data['id']
    result = sites_table.get_item(
        Key={
            'id': site_id
        }
    )
    if 'Item' in result:
        return {
            "statusCode": 400,
            "body": {
                "message": "site id exists"
            }
        }
    timestamp = str(datetime.utcnow())
    data['createdAt'] = timestamp
    data['updatedAt'] = timestamp
    sites_table.put_item(Item=data)
    user_site = {
        'username': event['requestContext']['authorizer']['jwt']['claims']['username'],
        'siteId': site_id,
        'created_at': timestamp,
        'updated_at': timestamp
    }
    user_sites_table.put_item(Item=user_site)
    return {
        "statusCode": 201,
        "body": data
    }
