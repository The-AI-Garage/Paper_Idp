import boto3
import datetime


def main(event, context):
    # init client
    dynamodb = boto3.client('dynamodb')
    # get results
    print('event: ',event)
    # get document
    result_item = event['item']
    # add date
    date = datetime.datetime.now()
    # put item in table
    dynamodb.put_item(
        TableName='PapersIdp', 
        Item={
            'PaperClass':result_item['class'],    # primary key
            'CreatedAt':date,                     # sort key
            'Title':result_item['title'],         # attribute 1
            'Author':result_item['author'],       # attribute 2
            'Summary':result_item['summary'],     # attribute 3
            'S3Object': result_item['s3Url']
        }
            )
    return {
        'statusCode': 200
    }