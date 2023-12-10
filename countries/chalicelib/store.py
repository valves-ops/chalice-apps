import os
from typing import Any

import logging

import boto3
import amazondax
from boto3.dynamodb.conditions import Key, ConditionExpressionBuilder

from decimal import Decimal
from datetime import datetime

from chalicelib.exceptions import BaseFailure


_DYNAMODB_RESOURCE = None

logger = logging.getLogger()


def get_dynamodb_resource():
    global _DYNAMODB_RESOURCE
    if _DYNAMODB_RESOURCE is None:
        use_dax = os.environ.get('use_dax', "False")
        if use_dax == "True":
            dax_endpoint = os.environ.get('dax_endpoint')
            region = os.environ.get('region')
            _DYNAMODB_RESOURCE = amazondax.AmazonDaxClient.resource(
                endpoint_url=dax_endpoint, 
                region_name=region
            )
        else:
            _DYNAMODB_RESOURCE = boto3.resource('dynamodb')
    return _DYNAMODB_RESOURCE


class PutCountryFailure(BaseFailure):
    default_message = "Failed to save country data. Check DynamoDB status."


class PutStatusFailure(BaseFailure):
    default_message = "Failed to save status data. Check DynamoDB status."


class GetCountryFailure(BaseFailure):
    default_message = "Failed to get country data. Check DynamoDB status."


class GetStatusFailure(BaseFailure):
    default_message = "Failed to get status data. Check DynamoDB status."

class GetCircuitBreakerStateFailure(BaseFailure):
    default_message = "Failed to get circuit breaker state. Check DynamoDB status."

class PutCircuitBreakerStateFailure(BaseFailure):
    default_message = "Failed to put circuit breaker state. Check DynamoDB status."

class DeleteCircuitBreakerStateFailure(BaseFailure):
    default_message = "Failed to delete circuit breaker state. Check DynamoDB status."


class DynamoDBStorage:
    def __init__(self) -> None:
        logger.info('Setting up DynamoDB handler')
        self._dynamodb = get_dynamodb_resource()
        environment = os.environ.get('environment', 'dev')
        self._countries_table = self._dynamodb.Table(
            'countries-' + environment
        )
        self._status_table = self._dynamodb.Table(
            'status-' + environment
        )
        self._circuit_breaker_table = self._dynamodb.Table(
            'circuit-breaker-state-' + environment
        )

    @staticmethod
    def convert_floats_to_decimal(obj: Any) -> Any:
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {key: DynamoDBStorage.convert_floats_to_decimal(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [DynamoDBStorage.convert_floats_to_decimal(item) for item in obj]
        else:
            return obj
        
    def put_country(self, country_data: dict) -> bool:
        logger.info(f'Saving country data: {country_data.get("cca2")}')
        try:
            self._countries_table.put_item(
                Item=self.convert_floats_to_decimal(country_data)
            )
        except Exception as e:
            self.put_status(country_data, False, str(e))
            raise PutCountryFailure(str(e))
        else:
            self.put_status(country_data, True, '')
    
    def put_status(self, country_data: dict, success: bool, error: str):
        print("Country Data: ", country_data)
        logger.info(f'Saving status data: {country_data.get("cca2")}')
        status_item = {
            'fetched_country': country_data.get('cca2'),
            # TODO: make ts tz aware
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'success': success,
            'error': error
        }
        try:
            self._status_table.put_item(Item=status_item)
        except Exception as e:
            raise PutStatusFailure(str(e))        
        
    def get_country(self, code):
        logger.info(f'Getting country data: {code}')
        
        try:
            response = self._countries_table.get_item(Key={'cca2': code.upper()})
        except Exception as e:
            raise GetCountryFailure(str(e))
        
        return response.get('Item')
    
    def get_status(self, code):
        condition = Key('fetched_country').eq(code.upper())
        builder = ConditionExpressionBuilder()
        expression = builder.build_expression(condition, is_key_condition=True)
        expression_string = expression.condition_expression
        expression_attribute_names = expression.attribute_name_placeholders
        expression_attribute_values = expression.attribute_value_placeholders

        try:
            response = self._status_table.query(
                KeyConditionExpression=expression_string,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ScanIndexForward=False,
                Limit=1
            )
        except Exception as e:
            raise GetStatusFailure(str(e))
        
        
        return response.get('Items')

    def get_current_state(self, service_name: str):
        try:
            response = self._circuit_breaker_table.get_item(
                Key={'service_name': service_name}
            )
        except Exception as e:
            raise GetCircuitBreakerStateFailure(str(e))
        
        return response.get('Item')

    def set_new_state(self, new_state: dict):
        try:
            self._circuit_breaker_table.put_item(
                Item=new_state
            )
        except Exception as e:
            raise PutCircuitBreakerStateFailure(str(e))
    
    def delete_current_state(self, service_name):
        try:
            self._circuit_breaker_table.delete_item(
                Key={'service_name': service_name}
            )
        except Exception as e:
            raise DeleteCircuitBreakerStateFailure(str(e))