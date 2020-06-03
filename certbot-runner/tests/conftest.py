"""Fixtures for tests."""
import json

import boto3
from moto import mock_acm
import pytest
import uuid

from fixtures import LambdaContextMock
import payloads


def _import_cert(client):
    response = client.import_certificate(
        Certificate=SERVER_CRT, PrivateKey=SERVER_KEY, CertificateChain=CA_CRT
    )
    return response["CertificateArn"]


@pytest.fixture
def event():
    """Return parsed event."""
    with open('tests/payloads/moto.json') as json_data:
        return json.load(json_data)


@pytest.fixture
def context():
    """Return mock lambda context."""
    return LambdaContextMock()


@pytest.fixture
def region():
    """Return AWS region fixture."""
    return "us-west-2"


@pytest.fixture
def expected_common_name():
    """Return environment name fixture."""
    return "certbot-runner-test.presidio.pxsys.net"


@pytest.fixture
def setup_aws_creds(monkeypatch, region):
    """Set up AWS credential environment vars to make boto3 happy."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", region)


@pytest.fixture(autouse=True)
def install_mock_acm(setup_aws_creds):
    """Mock out boto3 ACM with moto."""
    with mock_acm():
        yield


@pytest.fixture(autouse=True)
def setup_acm(install_mock_acm, expected_common_name):
    """Create populate ACM with a test certificate."""
    # acm = boto3.client("acm")
    # _import_cert(acm)
    client = boto3.client("acm")

    token = str(uuid.uuid4())

    client.request_certificate(
        DomainName=expected_common_name,
        IdempotencyToken=token,
        SubjectAlternativeNames=[expected_common_name],
    )