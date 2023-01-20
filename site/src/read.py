import os

import boto3
from boto3.dynamodb.conditions import Key

from lib.decorators import cors_headers, json_http_resp

dynamodb = boto3.resource('dynamodb')
user_sites_table = dynamodb.Table(os.environ['USER_SITES_TABLE'])

@cors_headers
@json_http_resp
def read(event, context):
    username = event['requestContext']['authorizer']['jwt']['claims']['username']
    result = user_sites_table.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    return result['Items']
