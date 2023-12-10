
import os
import logging
from chalice import Chalice
from chalice import BadRequestError
from requests import Response

from chalicelib.external_service import CountriesAPI
from chalicelib.store import DynamoDBStorage
from chalicelib.sqs import Queue


SQS_QUEUE_NAME = 'fetch-requests-' + os.environ.get('environment', "dev")

logger = logging.getLogger()


app = Chalice(app_name='countries')

def validate_country_code(code):
    if not code.isalpha():
        raise BadRequestError(f"Provided country code [{code}] contain characters that are not alphabetical.")
    
    if len(code) > 2:
        raise BadRequestError(f"Provided country code [{code}] should be only two digits long.")


@app.route('/')
def index():
    return {'welcome': 'countries api demo'}

@app.route('/fetch-data/{code}')
def fetch_data(code):
    validate_country_code(code)
    fetch_data_queue = Queue(SQS_QUEUE_NAME)
    fetch_data_queue.send_message(code)

@app.on_sqs_message(queue=SQS_QUEUE_NAME)
def fetch_data_handler(event):
    logger.info(f"Starting fetch data handler: {event}")
    for record in event:
        code = record.body

        countries_api = CountriesAPI()
        country_data = countries_api.get_country_data(code)
        
        store = DynamoDBStorage()
        store.put_country(country_data)
        # return {'success': success}

@app.route('/view-data/{code}')
def view_data(code):
    validate_country_code(code)
    return DynamoDBStorage().get_country(code)

@app.route('/status/{code}')
def status(code):
    validate_country_code(code)
    return DynamoDBStorage().get_status(code)
