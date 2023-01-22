import os

import boto3

from utils.decorators import cors_headers, json_http_resp

dynamodb = boto3.resource('dynamodb')
sites_table = dynamodb.Table(os.environ['SITES_TABLE'])


@cors_headers
@json_http_resp
def delete(event, context):
    site_id = event['pathParameters']['id']
    username = event['requestContext']['authorizer']['jwt']['claims']['username']
    sites_table.delete_item(
        Key={
            'id': site_id
        },
        ConditionExpression='attribute_exists(id) and username = #username',
        ExpressionAttributeNames={"#username": username}
    )
    return "site deleted successfully"
