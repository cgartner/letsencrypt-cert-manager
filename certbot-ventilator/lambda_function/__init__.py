"""Builds a list of certificates to create and fans out via step functions to certbot-runner."""
import logging
import os

from ._version import __version__  # noqa: F401
import boto3

# To silence the linter about the unused __version__
(__version__)

LAMBDANAME = 'certbot-ventilator'


def lambda_handler(event, context):
    """Entrypoint for lambda."""
    logging.root.setLevel(logging.CRITICAL)
    env = 'test'
    domains = []

    # Error out if we're missing any keys
    try:
        certbot_server = event['certbot_server']
        email = event['email']
        s3_bucket = event['s3_bucket']
    except KeyError as error:
        logging.error(error)
        raise

    try:
        if 'PIXSVC_ENV' in os.environ:
            env = os.environ['PIXSVC_ENV']
        else:
            logging.info('Unable to find PIXSVC_ENV environment variable.')

        dynamodb = boto3.resource('dynamodb')

        table = dynamodb.Table(f'{env}-{LAMBDANAME}-certificates')
        # Scanning is an expensive operation, but at the current scale of our certs this won't be an issue
        scan_results = table.scan()
        for i in scan_results["Items"]:
            domains.append(i['subject_alternative_name'])

        if len(domains) == 0:
            raise Exception('No domains returned from DynamoDB table scan.')
        return {
            'certbot_server': certbot_server,
            'domains': domains,
            'email': email,
            's3_bucket': s3_bucket
        }
    except RuntimeError:
        return {
            'error': 'Unable to determine domains to manage.'
        }
