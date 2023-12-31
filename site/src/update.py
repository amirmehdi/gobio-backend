import os
from datetime import datetime

import boto3

from utils.decorators import cors_headers, json_http_resp, load_json_body

dynamodb = boto3.resource('dynamodb')
sites_table = dynamodb.Table(os.environ['SITES_TABLE'])


@cors_headers
@json_http_resp
@load_json_body
def update(event, context):
    site_id = event['pathParameters']['id']
    username = event['requestContext']['authorizer']['jwt']['claims']['username']
    data = event['body']
    timestamp = str(datetime.utcnow())
    data['id'] = site_id
    data['username'] = username
    data['updatedAt'] = timestamp
    try:
        sites_table.put_item(Item=data,
                             ConditionExpression='attribute_exists(id) and id = :id and username = :username',
                             ExpressionAttributeValues={":id": site_id, ":username": username}
                             )
    except Exception:
        return {
            "statusCode": 403,
            "body": {"message": "forbidden"}
        }
    return "site updated"
