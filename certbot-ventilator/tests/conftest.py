"""Fixtures for tests."""
import json

import boto3
from moto import mock_dynamodb2
import pytest

from fixtures import LambdaContextMock
import payloads


@pytest.fixture
def event():
    """Return parsed event."""
    with open('tests/payloads/success.json') as json_data:
        return json.load(json_data)


@pytest.fixture
def context():
    """Return mock lambda context."""
    return LambdaContextMock()


@pytest.fixture
def expected_table():
    """Return dynamodb table name fixture."""
    return "test-certbot-ventilator-certificates"


@pytest.fixture
def region():
    """Return AWS region fixture."""
    return "us-west-2"


@pytest.fixture
def setup_aws_creds(monkeypatch, region):
    """Set up AWS credential environment vars to make boto3 happy."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", region)


@pytest.fixture(autouse=True)
def install_mock_dynamodb(setup_aws_creds):
    """Mock out boto3 S3 with moto."""
    with mock_dynamodb2():
        yield

@pytest.fixture(autouse=True)
def setup_table(install_mock_dynamodb, expected_table):
    """Create a table and populate it with a column value."""
    dynamodb = boto3.client("dynamodb")
    dynamodb.create_table(
        TableName=expected_table,
        KeySchema=[
            {
                'AttributeName': 'subject_alternative_name',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'subject_alternative_name',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    item = {
        "subject_alternative_name": {"S": "test-domain.pxsys.net"}
    }

    dynamodb.put_item(TableName=expected_table, Item=item)
