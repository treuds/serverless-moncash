import json
import moncashify
import os
import uuid
import boto3
from decimal import Decimal

client_id=os.getenv('CLIENT')
secret_key=os.getenv('SECRET')
order_table=os.getenv('ORDER_TABLE')

moncash = moncashify.API(client_id, secret_key)
dynamodb=boto3.resource("dynamodb")

def main(event, context):
    try: 
        orderline=json.loads(event)['body']
        orderline['id']=str(uuid.uuid4())
        orderline['paymentCompleted']=False
        orderline['amount']= Total(orderline['items'])
        response=createOrder(orderline)
        res=json.dumps({'statusCode': 200,'body': response})
    except:
        res=json.dumps({'statusCode': 500,'body': 'Unable to create payment'})

    return res

def createOrder(orderline):
    #write the order to db
    table = dynamodb.Table(order_table)
    table.put_item(orderline)
    res=moncash.payment(orderline['id'],orderline['amount'])
    return res

def Total(a):
    total=0
    for x in a:
        total+=float(x['price'])
    # kalkil TCA a 10 %
    tca=total*0.10
    res=total+tca
    return res