import logging
import os
import requests


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
       