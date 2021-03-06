import moncashify
import os
import json
import uuid
import boto3
from datetime import datetime
from decimal import Decimal 
from dynamodb_json import json_util as jsonn
import math

client_id=os.environ['CLIENT']
secret_key=os.getenv('SECRET')
order_table=os.getenv('ORDER_TABLE')

moncash = moncashify.API(client_id, secret_key)
dynamodb=boto3.client("dynamodb")

def main(event, context):
    orderline=json.loads(json.loads(json.dumps(event))['body'])
    try:
        orderline['id']=str(uuid.uuid4())
        orderline['paymentCompleted']=False
        orderline['amount']= Total(orderline['items'])
        print(orderline)
        response=createOrder(orderline)
        res=json.dumps({'statusCode': 200,'body': response})
        print(res)
        return res
    except:
        return json.dumps({'statusCode': 500,'body': 'Unable to create payment'})


def createOrder(orderline):
    #write the order to db
    response=dynamodb.put_item(TableName=order_table, Item=json.loads(jsonn.dumps(orderline)))
    print(response)
    #table.put_item(orderline)
    print("inserted")
    res=moncash.payment(orderline['id'],orderline['amount'])
    print(res)
    return res

def Total(a):
    total=0
    for x in a:
        total+=float(x['price'])
    # kalkil TCA a 10 %
    tca=total*0.10
    res=total+tca
    return math.ceil(res)