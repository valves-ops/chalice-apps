import logging
import os
import boto3
from chalicelib.exceptions import BaseFailure


_SQS_CLIENT = None

logger = logging.getLogger()


def get_sqs_client():
    global _SQS_CLIENT
    if _SQS_CLIENT is None:
        sqs_endpoint = os.environ.get('sqs_endpoint', "https://sqs.amazonaws.com/")
        _SQS_CLIENT = boto3.client('sqs', endpoint_url=sqs_endpoint)
    return _SQS_CLIENT


class QueueUrlRetrievalFailure(BaseFailure):
    default_message = "Queue Retrieval URL has failed. Check AWS SQS status."


class QueueSendMessageFailure(BaseFailure):
    default_message = "Failed to send message to queue. Check AWS SQS status."


class Queue:
    def __init__(self, queue_name):
        logger.info('Setting up Queue handler')
        self._sqs = get_sqs_client()

        response = None
        try:
            logger.info('Retrieving queue URL')
            response = self._sqs.get_queue_url(QueueName=queue_name)
        except Exception as e:
            raise QueueUrlRetrievalFailure(str(e))
        
        self._queue_url = response['QueueUrl']
        logger.info(f'Retrieved queue URL: {self._queue_url}')

    def send_message(self, message: str):
        logger.info(
            f'Preparing to send message [{message}] to queue [{self._queue_url}]')
        
        try:
            response = self._sqs.send_message(
                QueueUrl=self._queue_url,
                MessageBody=message
            )
        except Exception as e:
            raise QueueSendMessageFailure(str(e))
        
        message_id = response.get('MessageId')
        logger.info(f'Message sent succesfully, returned MessageId [{message_id}]')

        
        
        