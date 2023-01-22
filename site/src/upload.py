import os

import boto3
from boto3.dynamodb.conditions import Key

from utils.decorators import cors_headers, json_http_resp

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sites_table = dynamodb.Table(os.environ['SITES_TABLE'])
bucket = os.environ['SITES_BUCKET']


@cors_headers
@json_http_resp
def generate_url(event, context):
    site_id = event['pathParameters']['id']
    username = event['requestContext']['authorizer']['jwt']['claims']['username']
    result = sites_table.query(
        IndexName='UsernameIndex',
        KeyConditionExpression=Key('username').eq(username) & Key('id').eq(site_id)
    )
    if len(result["Items"]) == 0:
        return {
            "statusCode": 403,
            "body": {"message": "forbidden"}
        }
    res = s3.generate_presigned_post(Bucket=bucket,
                                     Key=site_id + '/${filename}',
                                     Conditions=[
                                         ["starts-with", "$Content-Type", "image/"],
                                         ["starts-with", "$key", f"{site_id}/"],
                                         ["content-length-range", 1, 1048576]
                                     ],
                                     ExpiresIn=60 * 60)
    return {
        "statusCode": 200,
        "body": res
    }
