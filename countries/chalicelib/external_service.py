import logging
import requests
from chalicelib.exceptions import BaseFailure
from chalicelib.circuit_breaker import CircuitBreakerDynamoDB

logger = logging.getLogger()
EXTERNAL_API_URL = 'https://restcountries.com/v3.1/alpha/'


class CountriesAPIServiceFailure(BaseFailure):
    default_message = "The Countries API service failed, check its status."


class CountriesAPI:
    def get_country_data(self, code: str) -> dict:
        logger.info(f'Requesting country data ({code}) from external service')
        
        logger.info(f'Checking circuit breaker...')
        circuit_breaker = CircuitBreakerDynamoDB('countries-api-service')
        if not circuit_breaker.is_armed():
            raise CountriesAPIServiceFailure(
                'Countries API aborted, circuit breaker disarmed.')
        try:
            response = requests.get(EXTERNAL_API_URL+code.lower())
        except Exception as e:
            circuit_breaker.register_failure()
            raise e
        else:
            if response.status_code != 200:
                circuit_breaker.register_failure()
                raise CountriesAPIServiceFailure(
                    f'Countries API returned a response with status {response.status_code}')
            
        response_json = response.json()[0]
        return response_json