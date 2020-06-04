"""Test lambda function."""

import boto3

import lambda_function


def test_acm_population(expected_common_name):
    acm = boto3.client("acm")
    response = acm.list_certificates()
    print(response)
    assert response["CertificateSummaryList"][0]["DomainName"] == expected_common_name

def test_find_existing_cert(expected_common_name):
    result = lambda_function.find_existing_cert(expected_common_name)
    assert result['Certificate']['SubjectAlternativeNames'][0] == expected_common_name

def test_should_provision(expected_common_name):
    result = lambda_function.should_provision(expected_common_name)
    assert result == False