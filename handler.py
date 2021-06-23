import json
import logging
import os
import requests
import json


from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

URL = os.getenv('CONSUMER_API')


def producer(event, context):

    logger.info(f'Message: {event}')

    res = requests.get(url=URL, headers={
        "Content-Type": "application/json"
    })

    return {'statusCode': res.status_code}


def consumer(event, context):

    logger.info(f'Message: {event}')

    return {'statusCode': 200}
       