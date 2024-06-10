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
    date_int = int(date.timestamp())
    created_at_str = str(date_int)
    # put item in table
    dynamodb.put_item(
        TableName='PapersIdp', 
        Item={
            'PaperClass':{'S': result_item['class']},    # primary key
            'CreatedAt':{'N': created_at_str},                     # sort key
            'Title':{'S': result_item['title']},         # attribute 1
            'Author':{'S': result_item['author']},       # attribute 2
            'Summary':{'S': result_item['summary']},     # attribute 3
            'S3Object': {'S':result_item['s3Url']}
        }
            )
    return {
        'statusCode': 200
    }