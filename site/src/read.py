import os

import boto3
from boto3.dynamodb.conditions import Key

from utils.decorators import cors_headers, json_http_resp

dynamodb = boto3.resource('dynamodb')
sites_table = dynamodb.Table(os.environ['SITES_TABLE'])


@cors_headers
@json_http_resp
def read(event, context):
    username = event['requestContext']['authorizer']['jwt']['claims']['username']
    result = sites_table.query(
        IndexName='UsernameIndex',
        KeyConditionExpression=Key('username').eq(username)
    )
    return result['Items']
