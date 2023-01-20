import os
from datetime import datetime

import boto3

from utils.decorators import cors_headers, json_http_resp, load_json_body

dynamodb = boto3.resource('dynamodb')
sites_table = dynamodb.Table(os.environ['SITES_TABLE'])
user_sites_table = dynamodb.Table(os.environ['USER_SITES_TABLE'])


@cors_headers
@json_http_resp
@load_json_body
def update(event, context):
    site_id = event['pathParameters']['id']
    username = event['requestContext']['authorizer']['jwt']['claims']['username']
    result = user_sites_table.get_item(
        Key={
            'username': username,
            'siteId': site_id
        }
    )
    if 'Item' not in result:
        return {
            "statusCode": 403,
            "body": {"message": "forbidden"}
        }
    data = event['body']
    timestamp = str(datetime.utcnow())
    data['createdAt'] = timestamp
    data['updatedAt'] = timestamp
    sites_table.put_item(Item=data)
    return "site updated"
