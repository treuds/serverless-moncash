import json
import moncashify
import os
import boto3
from botocore.exceptions import ClientError


client_id=os.getenv('CLIENT')
secret_key=os.getenv('SECRET')
order_table=os.getenv('ORDER_TABLE')

moncash = moncashify.API(client_id, secret_key)
dynamodb = boto3.resource('dynamodb')


def main(event, context):
    #body=json.loads(json.loads(json.dumps(event))['body'])
    #transaction_id=json.loads(body['payment']['transaction_id'])
    transaction_id=(event['queryStringParameters']['transactionId'])
    print("ID TRANSACTION", transaction_id)
    data=moncash.transaction_details_by_transaction_id(transaction_id)
    if data['payment']['message']=='successful':
        #update the order on our db
        idRef= data['payment']['reference']
        updateOrderById(idRef,True)
        response={'statusCode': 200,'body': "payment completed"}
    else:
        response={'statusCode': 500,'body': 'Unable to process payment'}
  
    return response





def updateOrderById(id, completed=False):

    table = dynamodb.Table(order_table)

    try:
        response = table.update_item(Key={'id':id,
        },
        UpdateExpression="set paymentCompleted=:c",
        ExpressionAttributeValues={
            ':c': completed ,
        },
        ReturnValues="UPDATED_NEW")
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response