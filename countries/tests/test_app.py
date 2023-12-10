from urllib import response
from chalice.test import Client
import pytest
from app import app

from unittest.mock import Mock, patch
from botocore.stub import Stubber
from boto3.dynamodb.conditions import Key, ConditionExpressionBuilder
from freezegun import freeze_time

from chalicelib.sqs import get_sqs_client
from chalicelib.store import DynamoDBStorage, get_dynamodb_resource, PutCountryFailure, PutStatusFailure

from app import CountriesAPI
from chalicelib.external_service import CountriesAPIServiceFailure, requests


COUNTRY_BRA_DATA = {
    "name": {
        "common": "Brazil",
        "official": "Federative Republic of Brazil",
        "nativeName": {
            "por": {
                "official": "Rep\u00fablica Federativa do Brasil",
                "common": "Brasil",
            }
        },
    },
    "tld": [".br"],
    "cca2": "BR",
    "ccn3": "076",
    "cca3": "BRA",
    "cioc": "BRA",
    "independent": True,
    "status": "officially-assigned",
    "unMember": True,
    "currencies": {"BRL": {"name": "Brazilian real", "symbol": "R$"}},
    "idd": {"root": "+5", "suffixes": ["5"]},
    "capital": ["Bras\u00edliaXXX"],
    "altSpellings": [
        "BR",
        "Brasil",
        "Federative Republic of Brazil",
        "Rep\u00fablica Federativa do Brasil",
    ],
    "region": "Americas",
    "subregion": "South America",
    "languages": {"por": "Portuguese"},
    "translations": {
        "ara": {
            "official": "\u062c\u0645\u0647\u0648\u0631\u064a\u0629 \u0627\u0644\u0628\u0631\u0627\u0632\u064a\u0644 \u0627\u0644\u0627\u062a\u062d\u0627\u062f\u064a\u0629",
            "common": "\u0627\u0644\u0628\u0631\u0627\u0632\u064a\u0644",
        },
        "bre": {"official": "Republik Kevreel Brazil", "common": "Brazil"},
        "ces": {
            "official": "Brazilsk\u00e1 federativn\u00ed republika",
            "common": "Braz\u00edlie",
        },
        "cym": {"official": "Gweriniaeth Ffederal Brasil", "common": "Brasil"},
        "deu": {
            "official": "F\u00f6derative Republik Brasilien",
            "common": "Brasilien",
        },
        "est": {"official": "Brasiilia Liitvabariik", "common": "Brasiilia"},
        "fin": {"official": "Brasilian liittotasavalta", "common": "Brasilia"},
        "fra": {
            "official": "R\u00e9publique f\u00e9d\u00e9rative du Br\u00e9sil",
            "common": "Br\u00e9sil",
        },
        "hrv": {"official": "Savezne Republike Brazil", "common": "Brazil"},
        "hun": {
            "official": "Brazil Sz\u00f6vets\u00e9gi K\u00f6zt\u00e1rsas\u00e1g",
            "common": "Braz\u00edlia",
        },
        "ita": {"official": "Repubblica federativa del Brasile", "common": "Brasile"},
        "jpn": {
            "official": "\u30d6\u30e9\u30b8\u30eb\u9023\u90a6\u5171\u548c\u56fd",
            "common": "\u30d6\u30e9\u30b8\u30eb",
        },
        "kor": {
            "official": "\ube0c\ub77c\uc9c8 \uc5f0\ubc29 \uacf5\ud654\uad6d",
            "common": "\ube0c\ub77c\uc9c8",
        },
        "nld": {
            "official": "Federale Republiek Brazili\u00eb",
            "common": "Brazili\u00eb",
        },
        "per": {
            "official": "\u062c\u0645\u0647\u0648\u0631\u06cc \u0641\u062f\u0631\u0627\u062a\u06cc\u0648 \u0628\u0631\u0632\u06cc\u0644",
            "common": "\u0628\u0631\u0632\u06cc\u0644",
        },
        "pol": {"official": "Federacyjna Republika Brazylii", "common": "Brazylia"},
        "por": {"official": "Rep\u00fablica Federativa do Brasil", "common": "Brasil"},
        "rus": {
            "official": "\u0424\u0435\u0434\u0435\u0440\u0430\u0442\u0438\u0432\u043d\u0430\u044f \u0420\u0435\u0441\u043f\u0443\u0431\u043b\u0438\u043a\u0430 \u0411\u0440\u0430\u0437\u0438\u043b\u0438\u044f",
            "common": "\u0411\u0440\u0430\u0437\u0438\u043b\u0438\u044f",
        },
        "slk": {
            "official": "Braz\u00edlska federat\u00edvna republika",
            "common": "Braz\u00edlia",
        },
        "spa": {"official": "Rep\u00fablica Federativa del Brasil", "common": "Brasil"},
        "srp": {
            "official": "\u0421\u0430\u0432\u0435\u0437\u043d\u0430 \u0420\u0435\u043f\u0443\u0431\u043b\u0438\u043a\u0430 \u0411\u0440\u0430\u0437\u0438\u043b",
            "common": "\u0411\u0440\u0430\u0437\u0438\u043b",
        },
        "swe": {"official": "F\u00f6rbundsrepubliken Brasilien", "common": "Brasilien"},
        "tur": {"official": "Brezilya Federal Cumhuriyeti", "common": "Brezilya"},
        "urd": {
            "official": "\u0648\u0641\u0627\u0642\u06cc \u062c\u0645\u06c1\u0648\u0631\u06cc\u06c1 \u0628\u0631\u0627\u0632\u06cc\u0644",
            "common": "\u0628\u0631\u0627\u0632\u06cc\u0644",
        },
        "zho": {
            "official": "\u5df4\u897f\u8054\u90a6\u5171\u548c\u56fd",
            "common": "\u5df4\u897f",
        },
    },
    "latlng": [-10.0, -55.0],
    "landlocked": False,
    "borders": ["ARG", "BOL", "COL", "GUF", "GUY", "PRY", "PER", "SUR", "URY", "VEN"],
    "area": 8515767.0,
    "demonyms": {
        "eng": {"f": "Brazilian", "m": "Brazilian"},
        "fra": {"f": "Br\u00e9silienne", "m": "Br\u00e9silien"},
    },
    "flag": "\ud83c\udde7\ud83c\uddf7",
    "maps": {
        "googleMaps": "https://goo.gl/maps/waCKk21HeeqFzkNC9",
        "openStreetMaps": "https://www.openstreetmap.org/relation/59470",
    },
    "population": 212559409,
    "gini": {"2019": 53.4},
    "fifa": "BRA",
    "car": {"signs": ["BR"], "side": "right"},
    "timezones": ["UTC-05:00", "UTC-04:00", "UTC-03:00", "UTC-02:00"],
    "continents": ["South America"],
    "flags": {
        "png": "https://flagcdn.com/w320/br.png",
        "svg": "https://flagcdn.com/br.svg",
        "alt": "The flag of Brazil has a green field with a large yellow rhombus in the center. Within the rhombus is a dark blue globe with twenty-seven small five-pointed white stars depicting a starry sky and a thin white convex horizontal band inscribed with the national motto 'Ordem e Progresso' across its center.",
    },
    "coatOfArms": {
        "png": "https://mainfacts.com/media/images/coats_of_arms/br.png",
        "svg": "https://mainfacts.com/media/images/coats_of_arms/br.svg",
    },
    "startOfWeek": "monday",
    "capitalInfo": {"latlng": [-15.79, -47.88]},
    "postalCode": {"format": "#####-###", "regex": "^(\\d{8})$"},
}

COUNTRY_COL_DATA_RESPONSE = {
    "Item": {
        "fifa": "COL",
        "currencies": {"COP": {"name": "Colombian peso", "symbol": "$"}},
        "borders": ["BRA", "ECU", "PAN", "PER", "VEN"],
        "cioc": "COL",
        "status": "officially-assigned",
        "subregion": "South America",
        "tld": [".co"],
        "population": 50882884.0,
        "demonyms": {
            "fra": {"m": "Colombien", "f": "Colombienne"},
            "eng": {"m": "Colombian", "f": "Colombian"},
        },
        "idd": {"suffixes": ["7"], "root": "+5"},
        "timezones": ["UTC-05:00"],
        "capital": ["Bogot\u00e1"],
        "name": {
            "common": "Colombia",
            "official": "Republic of Colombia",
            "nativeName": {
                "spa": {"common": "Colombia", "official": "Rep\u00fablica de Colombia"}
            },
        },
        "flag": "\ud83c\udde8\ud83c\uddf4",
        "translations": {
            "hun": {
                "common": "Kolumbia",
                "official": "Kolumbiai K\u00f6zt\u00e1rsas\u00e1g",
            },
            "swe": {"common": "Colombia", "official": "Republiken Colombia"},
            "zho": {
                "common": "\u54e5\u4f26\u6bd4\u4e9a",
                "official": "\u54e5\u4f26\u6bd4\u4e9a\u5171\u548c\u56fd",
            },
            "est": {"common": "Colombia", "official": "Colombia Vabariik"},
            "fin": {"common": "Kolumbia", "official": "Kolumbian tasavalta"},
            "pol": {"common": "Kolumbia", "official": "Republika Kolumbii"},
            "kor": {
                "common": "\ucf5c\ub86c\ube44\uc544",
                "official": "\ucf5c\ub86c\ube44\uc544 \uacf5\ud654\uad6d",
            },
            "ces": {"common": "Kolumbie", "official": "Kolumbijsk\u00e1 republika"},
            "tur": {"common": "Kolombiya", "official": "Kolombiya Cumhuriyeti"},
            "ara": {
                "common": "\u0643\u0648\u0644\u0648\u0645\u0628\u064a\u0627",
                "official": "\u062c\u0645\u0647\u0648\u0631\u064a\u0629 \u0643\u0648\u0644\u0648\u0645\u0628\u064a\u0627",
            },
            "rus": {
                "common": "\u041a\u043e\u043b\u0443\u043c\u0431\u0438\u044f",
                "official": "\u0420\u0435\u0441\u043f\u0443\u0431\u043b\u0438\u043a\u0430 \u041a\u043e\u043b\u0443\u043c\u0431\u0438\u044f",
            },
            "por": {
                "common": "Col\u00f4mbia",
                "official": "Rep\u00fablica da Col\u00f4mbia",
            },
            "bre": {"common": "Kolombia", "official": "Republik Kolombia"},
            "fra": {"common": "Colombie", "official": "R\u00e9publique de Colombie"},
            "deu": {"common": "Kolumbien", "official": "Republik Kolumbien"},
            "ita": {"common": "Colombia", "official": "Repubblica di Colombia"},
            "per": {
                "common": "\u06a9\u0644\u0645\u0628\u06cc\u0627",
                "official": "\u062c\u0645\u0647\u0648\u0631\u06cc \u06a9\u0644\u0645\u0628\u06cc\u0627",
            },
            "spa": {"common": "Colombia", "official": "Rep\u00fablica de Colombia"},
            "urd": {
                "common": "\u06a9\u0648\u0644\u0645\u0628\u06cc\u0627",
                "official": "\u062c\u0645\u06c1\u0648\u0631\u06cc\u06c1 \u06a9\u0648\u0644\u0645\u0628\u06cc\u0627",
            },
            "nld": {"common": "Colombia", "official": "Republiek Colombia"},
            "jpn": {
                "common": "\u30b3\u30ed\u30f3\u30d3\u30a2",
                "official": "\u30b3\u30ed\u30f3\u30d3\u30a2\u5171\u548c\u56fd",
            },
            "hrv": {"common": "Kolumbija", "official": "Republika Kolumbija"},
            "srp": {
                "common": "\u041a\u043e\u043b\u0443\u043c\u0431\u0438\u0458\u0430",
                "official": "\u0420\u0435\u043f\u0443\u0431\u043b\u0438\u043a\u0430 \u041a\u043e\u043b\u0443\u043c\u0431\u0438\u0458\u0430",
            },
            "slk": {"common": "Kolumbia", "official": "Kolumbijsk\u00e1 republika"},
            "cym": {"common": "Colombia", "official": "Gweriniaeth Colombia"},
        },
        "unMember": True,
        "maps": {
            "googleMaps": "https://goo.gl/maps/zix9qNFX69E9yZ2M6",
            "openStreetMaps": "https://www.openstreetmap.org/relation/120027",
        },
        "latlng": [4.0, -72.0],
        "ccn3": "170",
        "region": "Americas",
        "altSpellings": ["CO", "Republic of Colombia", "Rep\u00fablica de Colombia"],
        "startOfWeek": "monday",
        "gini": {"2019": 51.3},
        "flags": {
            "png": "https://flagcdn.com/w320/co.png",
            "alt": "The flag of Colombia is composed of three horizontal bands of yellow, blue and red, with the yellow band twice the height of the other two bands.",
            "svg": "https://flagcdn.com/co.svg",
        },
        "landlocked": False,
        "capitalInfo": {"latlng": [4.71, -74.07]},
        "independent": True,
        "coatOfArms": {
            "png": "https://mainfacts.com/media/images/coats_of_arms/co.png",
            "svg": "https://mainfacts.com/media/images/coats_of_arms/co.svg",
        },
        "cca2": "CO",
        "cca3": "COL",
        "car": {"side": "right", "signs": ["CO"]},
        "languages": {"spa": "Spanish"},
        "area": 1141748.0,
        "continents": ["South America"],
    },
    "ResponseMetadata": {
        "RequestId": "76GAOG4390073QNH6N0MF15QENVV4KQNSO5AEMVJF66Q9ASUAAJG",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "server": "Server",
            "date": "Fri, 08 Dec 2023 19:07:19 GMT",
            "content-type": "application/x-amz-json-1.0",
            "content-length": "4129",
            "connection": "keep-alive",
            "x-amzn-requestid": "76GAOG4390073QNH6N0MF15QENVV4KQNSO5AEMVJF66Q9ASUAAJG",
            "x-amz-crc32": "2083670520",
        },
        "RetryAttempts": 0,
    },
}


def test_index_function():
    with Client(app) as client:
        response = client.http.get("/")
        assert response.json_body == {"welcome": "countries api demo"}


def test_fetch_data_happy_path():
    sqs_client = get_sqs_client()
    stub = Stubber(sqs_client)

    # get_queue_url response
    stub.add_response(
        "get_queue_url",
        expected_params={"QueueName": "fetch-requests-dev"},
        service_response={
            "QueueUrl": "https://sqs-endpoint.aws.com",
            "ResponseMetadata": {"HTTPStatusCode": 200}
        },
    )

    # send_message response
    stub.add_response(
        "send_message",
        expected_params={
            "QueueUrl": "https://sqs-endpoint.aws.com",
            "MessageBody": "CO",
        },
        service_response={
            "MessageId": "111-222-333",
            "ResponseMetadata": {"HTTPStatusCode": 200}
        },
    )

    with stub:
        with Client(app) as client:
            response = client.http.get("/fetch-data/CO")
            assert response.status_code == 200
        stub.assert_no_pending_responses()

def test_fetch_data_raises_error_if_country_code_is_not_alpha_only():
    with Client(app) as client:
        response = client.http.get("/fetch-data/C2")
        assert response.status_code == 400
        assert response.json_body == {
                'Code': 'BadRequestError',
                'Message': "Provided country code [C2] contain characters that are not alphabetical."
            }

def test_fetch_data_raises_error_if_country_code_is_longer_than_2_digits():
    with Client(app) as client:
        response = client.http.get("/fetch-data/COL")
        assert response.status_code == 400
        assert response.json_body == {
                'Code': 'BadRequestError',
                'Message': "Provided country code [COL] should be only two digits long."
            }

def test_fetch_data_handles_queue_url_retrieval_server_side_inexistent_queue():
    sqs_client = get_sqs_client()
    stub = Stubber(sqs_client)

    # get_queue_url response
    stub.add_client_error(
        "get_queue_url",
        expected_params={"QueueName": "fetch-requests-dev"},
        service_error_code='QueueDoesNotExist',
        http_status_code=400,
        service_message="The specified queue doesn't exist."
    )

    with stub:
        with Client(app) as client:
            response = client.http.get("/fetch-data/CO")
            assert response.status_code == 500
            assert response.json_body == {
                'Code': 'QueueUrlRetrievalFailure',
                'Message': "An error occurred (QueueDoesNotExist) when calling the GetQueueUrl operation: The specified queue doesn't exist."
            }
        stub.assert_no_pending_responses()

def test_fetch_data_handles_queue_url_retrieval_server_side_internal_failure():
    sqs_client = get_sqs_client()
    stub = Stubber(sqs_client)

    # get_queue_url response
    stub.add_client_error(
        "get_queue_url",
        expected_params={"QueueName": "fetch-requests-dev"},
        service_error_code='InternalFailure',
        http_status_code=500,
        service_message="The request processing has failed because of an unknown error, exception or failure."
    )

    with stub:
        with Client(app) as client:
            response = client.http.get("/fetch-data/CO")
            assert response.status_code == 500
            assert response.json_body == {
                'Code': 'QueueUrlRetrievalFailure',
                'Message': "An error occurred (InternalFailure) when calling the GetQueueUrl operation: The request processing has failed because of an unknown error, exception or failure."
            }
        stub.assert_no_pending_responses()

def test_fetch_data_handles_request_queueing_failure():
    sqs_client = get_sqs_client()
    stub = Stubber(sqs_client)

    # get_queue_url response
    stub.add_response(
        "get_queue_url",
        expected_params={"QueueName": "fetch-requests-dev"},
        service_response={
            "QueueUrl": "https://sqs-endpoint.aws.com",
            "ResponseMetadata": {"HTTPStatusCode": 200}
        },
    )

    # send_message response
    stub.add_client_error(
        "send_message",
        expected_params={
            "QueueUrl": "https://sqs-endpoint.aws.com",
            "MessageBody": "CO",
        },
        service_error_code='InternalFailure',
        http_status_code=500,
        service_message="The request processing has failed because of an unknown error, exception or failure."
    )

    with stub:
        with Client(app) as client:
            response = client.http.get("/fetch-data/CO")
            assert response.status_code == 500
            assert response.json_body == {
                'Code': 'QueueSendMessageFailure',
                'Message': "An error occurred (InternalFailure) when calling the SendMessage operation: The request processing has failed because of an unknown error, exception or failure."
            }
        stub.assert_no_pending_responses()


def mock_get_country_data(data):
    return COUNTRY_BRA_DATA

@freeze_time("2012-01-14 03:21:34")
@patch.object(CountriesAPI, "get_country_data", wraps=mock_get_country_data)
def test_fetch_data_handler_happy_path(mock_countries_api):
    dynamodb = get_dynamodb_resource()
    stub = Stubber(dynamodb.meta.client)

    # put_item (country)
    stub.add_response(
        "put_item",
        expected_params={
            "Item": DynamoDBStorage.convert_floats_to_decimal(COUNTRY_BRA_DATA),
            "TableName": "countries-dev",
        },
        service_response={"ResponseMetadata": {"HTTPStatusCode": 200}},
    )
    # put_item (status)
    stub.add_response(
        "put_item",
        expected_params={
            "Item": {
                "fetched_country": "BR",
                "timestamp": "2012-01-14 03:21:34",
                "success": True,
                "error": '',
            },
            "TableName": "status-dev",
        },
        service_response={"ResponseMetadata": {"HTTPStatusCode": 200}},
    )

    with stub:
        with Client(app) as client:
            response = client.lambda_.invoke(
                "fetch_data_handler",
                client.events.generate_sqs_event(["BR"], "fetch-requests-dev"),
            )
            # assert response.payload == {}
            # TODO add more assertions
        stub.assert_no_pending_responses()

@freeze_time("2012-01-14 03:21:34")
@patch.object(CountriesAPI, "get_country_data", wraps=mock_get_country_data)
def test_fetch_data_handler_handles_put_country_failure(mock_countries_api):
    dynamodb = get_dynamodb_resource()
    stub = Stubber(dynamodb.meta.client)

    # put_item (country)
    stub.add_client_error(
        "put_item",
        expected_params={
            "Item": DynamoDBStorage.convert_floats_to_decimal(COUNTRY_BRA_DATA),
            "TableName": "countries-dev",
        },
        service_error_code='InternalFailure',
        http_status_code=500,
        service_message="The request processing has failed because of an unknown error, exception or failure."
    )

    # put_item (status)
    stub.add_response(
        "put_item",
        expected_params={
            "Item": {
                "fetched_country": "BR",
                "timestamp": "2012-01-14 03:21:34",
                "success": False,
                "error": 'An error occurred (InternalFailure) when calling the '
                         'PutItem operation: The request processing has failed '
                         'because of an unknown error, exception or failure.',
            },
            "TableName": "status-dev",
        },
        service_response={"ResponseMetadata": {"HTTPStatusCode": 200}},
    )

    with stub:
        with Client(app) as client:
            with pytest.raises(PutCountryFailure): 
                client.lambda_.invoke(
                    "fetch_data_handler",
                    client.events.generate_sqs_event(["BR"], "fetch-requests-dev"),
                )
        stub.assert_no_pending_responses()

@freeze_time("2012-01-14 03:21:34")
@patch.object(CountriesAPI, "get_country_data", wraps=mock_get_country_data)
def test_fetch_data_handler_handles_put_status_failure(mock_countries_api):
    dynamodb = get_dynamodb_resource()
    stub = Stubber(dynamodb.meta.client)

    # put_item (country)
    stub.add_response(
        "put_item",
        expected_params={
            "Item": DynamoDBStorage.convert_floats_to_decimal(COUNTRY_BRA_DATA),
            "TableName": "countries-dev",
        },
        service_response={"ResponseMetadata": {"HTTPStatusCode": 200}},
    )

    # put_item (status)
    stub.add_client_error(
        "put_item",
        expected_params={
            "Item": {
                "fetched_country": "BR",
                "timestamp": "2012-01-14 03:21:34",
                "success": True,
                "error": '',
            },
            "TableName": "status-dev",
        },
        service_error_code='InternalFailure',
        http_status_code=500,
        service_message="The request processing has failed because of an unknown error, exception or failure."
    )

    with stub:
        with Client(app) as client:
            with pytest.raises(PutStatusFailure): 
                client.lambda_.invoke(
                    "fetch_data_handler",
                    client.events.generate_sqs_event(["BR"], "fetch-requests-dev"),
                )
        stub.assert_no_pending_responses()

def mock_requests_get(data):
    mock_response = Mock()
    mock_response.status_code = 500
    return mock_response

@freeze_time("2012-01-14 03:21:34")
@patch.object(requests, "get", wraps=mock_requests_get)
def test_fetch_data_handler_handles_external_service_failure(mocked_requests_get):
    dynamodb = get_dynamodb_resource()
    stub = Stubber(dynamodb.meta.client)
    stub.add_response(
        "get_item",
        expected_params={
            'Key': {"service_name": "countries-api-service"},
            'TableName': 'circuit-breaker-state-dev'
        },
        service_response={
            'Item': {},
            "ResponseMetadata": {
                "HTTPStatusCode": 200
            }
        }
    )
    stub.add_response(
        "put_item",
        expected_params={
            "Item": {
                "service_name": "countries-api-service",
                "timestamp": "2012-01-14 03:21:34",
                "counter": 1,
            },
            "TableName": "circuit-breaker-state-dev",
        },
        service_response={"ResponseMetadata": {"HTTPStatusCode": 200}},
    )

    with stub:
        with Client(app) as client:
            with pytest.raises(CountriesAPIServiceFailure): 
                client.lambda_.invoke(
                    "fetch_data_handler",
                    client.events.generate_sqs_event(["BR"], "fetch-requests-dev"),
                )


def test_view_data_happy_path():
    dynamodb = get_dynamodb_resource()
    stub = Stubber(dynamodb.meta.client)
    stub.add_response(
        "get_item",
        expected_params={
            'Key': {"cca2": "CO"},
            'TableName': 'countries-dev'
        },
        service_response={
            'Item': {
                "cca2": {
                    "S": "CO"
                },
            },
            "ResponseMetadata": {
                "HTTPStatusCode": 200
            }
        }
    )

    with stub:
        with Client(app) as client:
            response = client.http.get("/view-data/CO")
            response_json = response.json_body
            assert response.status_code == 200
            assert response_json.get("cca2") == 'CO'
        stub.assert_no_pending_responses()

def test_view_data_handles_storage_failure():
    dynamodb = get_dynamodb_resource()
    stub = Stubber(dynamodb.meta.client)
    stub.add_client_error(
        "get_item",
        expected_params={
            'Key': {"cca2": "CO"},
            'TableName': 'countries-dev'
        },
        service_error_code='InternalFailure',
        http_status_code=500,
        service_message="The request processing has failed because of an unknown error, exception or failure."
    )

    with stub:
        with Client(app) as client:
            response = client.http.get("/view-data/CO")
            assert response.status_code == 500
            assert response.json_body == {
                'Code': 'GetCountryFailure',
                'Message': "An error occurred (InternalFailure) when calling the GetItem operation: The request processing has failed because of an unknown error, exception or failure."
            }
        stub.assert_no_pending_responses()

def test_view_data_raises_error_if_country_code_is_not_alpha_only():
    with Client(app) as client:
        response = client.http.get("/view-data/C2")
        assert response.status_code == 400
        assert response.json_body == {
                'Code': 'BadRequestError',
                'Message': "Provided country code [C2] contain characters that are not alphabetical."
            }

def test_view_data_raises_error_if_country_code_is_longer_than_2_digits():
    with Client(app) as client:
        response = client.http.get("/view-data/COL")
        assert response.status_code == 400
        assert response.json_body == {
                'Code': 'BadRequestError',
                'Message': "Provided country code [COL] should be only two digits long."
            }


def test_status_happy_path():
    dynamodb = get_dynamodb_resource()
    stub = Stubber(dynamodb.meta.client)

    condition = Key('fetched_country').eq("CO")
    builder = ConditionExpressionBuilder()
    expression = builder.build_expression(condition, is_key_condition=True)
    expression_string = expression.condition_expression
    expression_attribute_names = expression.attribute_name_placeholders
    expression_attribute_values = expression.attribute_value_placeholders

    stub.add_response(
        "query",
        expected_params={
            'KeyConditionExpression': expression_string,
            'ExpressionAttributeNames': expression_attribute_names,
            'ExpressionAttributeValues': expression_attribute_values,
            'ScanIndexForward': False,
            'Limit': 1,
            'TableName': 'status-dev'
        },
        service_response={
            'Items': [{
                "fetched_country": {'S': "CO"},
                "success": {"BOOL": True},
                "errors": {'L': []},
                "timestamp": {'S': "2023-12-08 15:20:31"}
            }],
            "ResponseMetadata": {
                "HTTPStatusCode": 200
            }
        }
    )
    with stub:
        with Client(app) as client:
            response = client.http.get("/status/CO")
            response_json = response.json_body[0]
            assert response.status_code == 200
            assert response_json.get("fetched_country") == 'CO'
        stub.assert_no_pending_responses()

def test_status_handles_storage_failure():
    dynamodb = get_dynamodb_resource()
    stub = Stubber(dynamodb.meta.client)

    condition = Key('fetched_country').eq("CO")
    builder = ConditionExpressionBuilder()
    expression = builder.build_expression(condition, is_key_condition=True)
    expression_string = expression.condition_expression
    expression_attribute_names = expression.attribute_name_placeholders
    expression_attribute_values = expression.attribute_value_placeholders

    stub.add_client_error(
        "query",
        expected_params={
            'KeyConditionExpression': expression_string,
            'ExpressionAttributeNames': expression_attribute_names,
            'ExpressionAttributeValues': expression_attribute_values,
            'ScanIndexForward': False,
            'Limit': 1,
            'TableName': 'status-dev'
        },
        service_error_code='InternalFailure',
        http_status_code=500,
        service_message="The request processing has failed because of an unknown error, exception or failure."
    )
    
    with stub:
        with Client(app) as client:
            response = client.http.get("/status/CO")
            assert response.status_code == 500
            assert response.json_body == {
                'Code': 'GetStatusFailure',
                'Message': "An error occurred (InternalFailure) when calling the Query operation: The request processing has failed because of an unknown error, exception or failure."
            }
        stub.assert_no_pending_responses()

def test_status_data_raises_error_if_country_code_is_not_alpha_only():
    with Client(app) as client:
        response = client.http.get("/status/C2")
        assert response.status_code == 400
        assert response.json_body == {
                'Code': 'BadRequestError',
                'Message': "Provided country code [C2] contain characters that are not alphabetical."
            }

def test_status_data_raises_error_if_country_code_is_longer_than_2_digits():
    with Client(app) as client:
        response = client.http.get("/status/COL")
        assert response.status_code == 400
        assert response.json_body == {
                'Code': 'BadRequestError',
                'Message': "Provided country code [COL] should be only two digits long."
            }
