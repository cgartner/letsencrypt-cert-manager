"""Test lambda function."""

import boto3
import lambda_function

def test_function(event, context):
    """Test the positive use case."""
    response = lambda_function.lambda_handler(event, context)
    assert "test-domain.pxsys.net" in response['domains']
