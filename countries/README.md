# Chalice Apps Demonstration
This repository contains implementations of sample applications in a serverless environment using the AWS Chalice framework and following best practices for optimal cost-efficiency.

## Summary
- Overview
- Local Setup
- Cloud Bootstrapping
- API
- Stack
- Architecture
- Trade-offs
- Future Improvements

## Overview
Currently, the project has only the countries application, which implments a simple information retrieval and storage for the countries data that is extracted from the [REST Countries API](https://restcountries.com).
The application has three endpoints:

#### 1.  Fetch Data 
Sends a requests to the application in order to fetch data from the external (REST Countries) API. This requests is queued and awaits processing.
> GET /fetch-data/\<country-code\>/


#### 2.  View Data 
Once fetch data requests are processed, the data retrieved is stored in DynamoDB and the View Data endpoints allows users to retrieve the stored data.
> GET /view-data/\<country-code\>/

#### 3.  Status 
The status endpoint is auxiliary to the data flow endpoints and retrieves data regarding the last data fetching request, when it was made, the status of its completion and errors, if there were any.
> GET /status/\<country-code\>/


## Local Setup
DISCLAIMER: This local setup was tested on MacOS, it should work on most Unix systems as well.
### Requirements
- Python v3.9.x or any other version compatible with Lambdas runtime
- AWSCLI v2.4.29 or higher configured locally 

### Instructions
1. Clone repository
```console
$ git clone https://github.com/valves-ops/chalice-apps.git
$ cd chalice-apps
```

2. Setup a virtualenv of your choice, I've used pyenv's venv:

```console
$ pyenv virtualenv 3.9.5 chalice
$ pyenv local chalice
```

3. Install requirements for development
```console
$ cd countries
$ pip install -r requirements-dev.txt
```

<!-- 4. Set AWS_PROFILE environment variable in case you have multiple defined on your AWS credentials file:
```console
$ export AWS_PROFILE=<your-chosen-profile>
```

5. If your profile doesn't have a region defined, specify it as well:

```console
$ export AWS_DEFAULT_REGION=<sa-east-1>
``` -->

4. Run test suite to check everything worked fine
```console
$ py.test tests
```


## Cloud Bootstrapping
### Requirements
- AWS Account
- AWS connection to the Github repository with `github-connection` as name (self-guided process started on [Developer Tools > Settings](https://sa-east-1.console.aws.amazon.com/codesuite/settings/connections?region=sa-east-1))
- Terraform v1.3.7
- Terraform AWS provider v5.30.0
- S3 bucket and DynamoDB Table configured for terraform remote state (change to local?)

### Instructions
1. Setup Terraform Project
```console
$ cd infrastructure
$ terraform init
```

2. Provision Infrastructure (DynamoDB tables, SQS queues, pipeline etc)
```console
$ make plan-dev
$ make apply-dev
```

Note that the pipeline is triggered automatically after its creation and it should fail, because the config.json contains invalid values for the recently deployed infrastructre.


3. Edit the `.chalice/config.json` with the information outputed by Terraform
- Set dax_endpoint environment variable
- Set subnet_ids with only the private subnet
- Set the correct region on the SQS endpoint variable (in case you're using one different from the sa-east-1)
- Set the security_group_ids with only the default vpc security group
- Set the iam_role ARN

<!-- 4. Deploy chalice application
```console
$ chalice deploy
``` -->
<!-- 
5. Access the application through the address returned by the chalice deploy command -->

4. Commit and push `.chalice/config.json` changes to make its correct version available to the pipeline
5. Wait for the pipeline to run and get the application endpoints from the resulting logs 


## API
### Fetch Data
```
GET /fetch-data/<country-code>/
```

Successful Response example
```json
{
    "message": "fetch data request for country (PY) successfully queued."
}
```

### View Data
```
GET /view-data/<country-code>/
```

Successful Response example
```json
{
    "cca2": "PY",
    "altSpellings": [
        "PY",
        "Republic of Paraguay",
        "Rep\u00fablica del Paraguay",
        "Tet\u00e3 Paragu\u00e1i"
    ],
    "area": 406752.0,
    "borders": [
        "ARG",
        "BOL",
        "BRA"
    ],
    "capital": [
        "Asunci\u00f3n"
    ],
    "capitalInfo": {
        "latlng": [
            -25.28,
            -57.57
        ]
    },
    "car": {
        "side": "right",
        "signs": [
            "PY"
        ]
    },
    "cca3": "PRY",
    "ccn3": "600",
    "cioc": "PAR",
    "coatOfArms": {
        "png": "https://mainfacts.com/media/images/coats_of_arms/py.png",
        "svg": "https://mainfacts.com/media/images/coats_of_arms/py.svg"
    },
    "continents": [
        "South America"
    ],
    "currencies": {
        "PYG": {
            "name": "Paraguayan guaran\u00ed",
            "symbol": "\u20b2"
        }
    },
    "demonyms": {
        "fra": {
            "m": "Paraguayen",
            "f": "Paraguayenne"
        },
        "eng": {
            "m": "Paraguayan",
            "f": "Paraguayan"
        }
    },
    "fifa": "PAR",
    "flag": "\ud83c\uddf5\ud83c\uddfe",
    "flags": {
        "alt": "The flag of Paraguay features three equal horizontal bands of red, white and blue, with an emblem centered in the white band. On the obverse side of the flag depicted, this emblem is the national coat of arms.",
        "png": "https://flagcdn.com/w320/py.png",
        "svg": "https://flagcdn.com/py.svg"
    },
    "gini": {
        "2019": 45.7
    },
    "idd": {
        "suffixes": [
            "95"
        ],
        "root": "+5"
    },
    "independent": true,
    "landlocked": true,
    "languages": {
        "spa": "Spanish",
        "grn": "Guaran\u00ed"
    },
    "latlng": [
        -23.0,
        -58.0
    ],
    "maps": {
        "googleMaps": "https://goo.gl/maps/JtnqG73WJn1Gx6mz6",
        "openStreetMaps": "https://www.openstreetmap.org/relation/287077"
    },
    "name": {
        "common": "Paraguay",
        "nativeName": {
            "spa": {
                "common": "Paraguay",
                "official": "Rep\u00fablica de Paraguay"
            },
            "grn": {
                "common": "Paragu\u00e1i",
                "official": "Tet\u00e3 Paragu\u00e1i"
            }
        },
        "official": "Republic of Paraguay"
    },
    "population": 7132530.0,
    "postalCode": {
        "format": "####",
        "regex": "^(\\d{4})$"
    },
    "region": "Americas",
    "startOfWeek": "monday",
    "status": "officially-assigned",
    "subregion": "South America",
    "timezones": [
        "UTC-04:00"
    ],
    "tld": [
        ".py"
    ],
    "translations": {
        "hun": {
            "common": "Paraguay",
            "official": "Paraguayi K\u00f6zt\u00e1rsas\u00e1g"
        },
        "swe": {
            "common": "Paraguay",
            "official": "Republiken Paraguay"
        },
        "zho": {
            "common": "\u5df4\u62c9\u572d",
            "official": "\u5df4\u62c9\u572d\u5171\u548c\u56fd"
        },
        "est": {
            "common": "Paraguay",
            "official": "Paraguay Vabariik"
        },
        "fin": {
            "common": "Paraguay",
            "official": "Paraguayn tasavalta"
        },
        "pol": {
            "common": "Paragwaj",
            "official": "Republika Paragwaju"
        },
        "kor": {
            "common": "\ud30c\ub77c\uacfc\uc774",
            "official": "\ud30c\ub77c\uacfc\uc774 \uacf5\ud654\uad6d"
        },
        "ces": {
            "common": "Paraguay",
            "official": "Paraguaysk\u00e1 republika"
        },
        "tur": {
            "common": "Paraguay",
            "official": "Paraguay Cumhuriyeti"
        },
        "ara": {
            "common": "\u0628\u0627\u0631\u0627\u063a\u0648\u0627\u064a",
            "official": "\u062c\u0645\u0647\u0648\u0631\u064a\u0629 \u0628\u0627\u0631\u0627\u063a\u0648\u0627\u064a"
        },
        "rus": {
            "common": "\u041f\u0430\u0440\u0430\u0433\u0432\u0430\u0439",
            "official": "\u0420\u0435\u0441\u043f\u0443\u0431\u043b\u0438\u043a\u0430 \u041f\u0430\u0440\u0430\u0433\u0432\u0430\u0439"
        },
        "por": {
            "common": "Paraguai",
            "official": "Rep\u00fablica do Paraguai"
        },
        "bre": {
            "common": "Paraguay",
            "official": "Republik Paraguay"
        },
        "fra": {
            "common": "Paraguay",
            "official": "R\u00e9publique du Paraguay"
        },
        "deu": {
            "common": "Paraguay",
            "official": "Republik Paraguay"
        },
        "ita": {
            "common": "Paraguay",
            "official": "Repubblica del Paraguay"
        },
        "per": {
            "common": "\u067e\u0627\u0631\u0627\u06af\u0648\u0626\u0647",
            "official": "\u062c\u0645\u0647\u0648\u0631\u06cc \u067e\u0627\u0631\u0627\u06af\u0648\u0626\u0647"
        },
        "spa": {
            "common": "Paraguay",
            "official": "Rep\u00fablica de Paraguay"
        },
        "urd": {
            "common": "\u067e\u06cc\u0631\u0627\u06af\u0648\u0626\u06d2",
            "official": "\u062c\u0645\u06c1\u0648\u0631\u06cc\u06c1 \u067e\u06cc\u0631\u0627\u06af\u0648\u0626\u06d2"
        },
        "nld": {
            "common": "Paraguay",
            "official": "Republiek Paraguay"
        },
        "jpn": {
            "common": "\u30d1\u30e9\u30b0\u30a2\u30a4",
            "official": "\u30d1\u30e9\u30b0\u30a2\u30a4\u5171\u548c\u56fd"
        },
        "hrv": {
            "common": "Paragvaj",
            "official": "Republika Paragvaj"
        },
        "srp": {
            "common": "\u041f\u0430\u0440\u0430\u0433\u0432\u0430\u0458",
            "official": "\u0420\u0435\u043f\u0443\u0431\u043b\u0438\u043a\u0430 \u041f\u0430\u0440\u0430\u0433\u0432\u0430\u0458"
        },
        "slk": {
            "common": "Paraguaj",
            "official": "Paraguajsk\u00e1 republika"
        },
        "cym": {
            "common": "Paraguay",
            "official": "Republic of Paraguay"
        }
    },
    "unMember": true
}
```

### Status
```
GET /status/<country-code>/
```

Successful Response example
```json
[
    {
        "fetched_country":"PY",
        "timestamp":"2023-12-10 04:45:20",
        "error":"",
        "success":true
    }
]
```

### Error Responses
All error responses follow the schema below
```json
{
    "Code": "ErrorType",
    "Message": "A detailed error message"
}
```

Example
```json
{
    "Code": "GetStatusFailure",
    "Message": "An error occurred (InternalFailure) when calling the Query operation: The request processing has failed because of an unknown error, exception or failure."
}
```

## Stack

- __Terraform__ for infrastructure provisioning
- __Chalice Framework__ for application development
- __AWS CodePipeline__ for CI/CD
- __DynamoDB__ as storage backend
- __DAX__ for caching
- Logging and Monitoring on __AWS CloudWatch__ (standard lambda monitoring)
  

#### Why Terraform?
Terraform is the market standard for infrastructure-as-code (IaC), which is a key practice for creating reproducible, auditable and self-discriptive infrastructures. On top of that, Chalice offers a way of packaging its output for deployment through Terraform scripts, which enables opeartions to rely entirely on Terraform to manage the whole infrastructure declaratively. This means that the current implementation of the pipeline could be extend to not only deploy the chalice app but also the whole infrastructure, providing the closest emulation of a GitOps workflow outside of a cloud native environment.

#### Why AWS Codepipeline?
Provided that the Chalice application ties the operation to AWS, it reduces the scope of maintenance to build the pipeline in AWS as well further facilitating the integration and permission setting of runner over the managed application and infrastructure.

#### Why DAX?
Standard and efficient solution for a stack that has already adopted DynamoDB as a storage backend.

## Architecture 

### Fetch Data Request Decoupling
The project follows a pretty standard architecture given the Chalice Framework capabilities but it is worth bringing attention to the Fetch Data endpoint.

The Fetch Data endpoint, instead of requesting data directly from a third-party application and storing the results on the storage backend, merely saves the fetch data requests into a queue, which off-loads the actual data fetching and storing to an assynchronous lambda function that attends to queue events.
This extra architectural complexity is motivated by reducing the users' request cycle, ie by not making users to wait for a third-party data retrieval and an data storage transaction, as well as decoupling the the fetch data requests from the actual data fetching process, enhancing the scalability and resilience of the system.



## Trade-offs
### DAX and Cold Start times
DAX, even though managed, is not a serverless component of the presented infrastructure, which means it forces the Lambda function to connect to a VPC in order to be capable to connect to the DAX cluster. This hard-requirement imposes the lambda function to provision a ENI at launch, which further increases the lambda cold start time.
A counter for this would be the introduction of provisioned concurrency for the lambda functions, that was not included as part of the project because it would increase the idle costs of the infrastructure.

## Future Improvements
- Integration tests for `CircuitBreakerDynamoDB`
- Create script to autogenerate config.json from template, through the interpolation of terraform output values
- The pipeline only deploys the application to a development environment, but with Chalice stages it would easy to extend it to multi-step multi-environment deployment.
- Migrate deployment mechanism for direct Chalice deployment to deployment through Terraform, enablig a full infrastructure and application delivery.