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
            'author':result_item['author'],       # attribute 2
            'summary':result_item['summary'],     # attribute 3
        }
            )
    return {
        'statusCode': 200
    }