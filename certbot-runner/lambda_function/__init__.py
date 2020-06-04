"""Creates a certificate if it doesn't exist or is about to expire and uploads
the files to S3.."""
import boto3
import certbot.main
import datetime
import os
import logging

from ._version import __version__  # noqa: F401


# To silence the linter about the unused __version__
(__version__)

# We need to go through extra effort to silence numerous loggers so we don't leak the certificate
logging.getLogger().setLevel(logging.INFO)
loggers_to_quiet = ['acme', 'boto', 'certbot', 'nose', 'requests', 'urllib3']
for name in logging.Logger.manager.loggerDict.keys():
    if any(word in name for word in loggers_to_quiet):
        logging.getLogger(name).setLevel(logging.CRITICAL)
# s3 transfer doesn't appear in logging.Logger.manager.loggerDict.keys(), so we manually set it
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    """Entrypoint for lambda."""
    # Error out if we're missing any keys
    try:
        certbot_server = event['certbot_server']
        domains = event['domains']
        email = event['email']
        s3_bucket = event['s3_bucket']
    except KeyError as error:
        logger.error(error)
        raise

    # Error out if we're missing any values within our keys
    for key, value in event.items():
        if not value:
            error = f"Key has an empty value: {key}"
            logger.error(error)
            raise TypeError(error)

    try:
        if should_provision(domains):
            cert = provision_cert(email, domains, certbot_server)
            upload_to_s3(s3_bucket)
            upload_to_acm(cert, domains)
            return {
                "message": f"A new certificate has been provisioned and uploaded to both S3 and ACM for: {domains}",
                "status": "success"
            }
        else:
            return {
                "message": f"A certificate with at least 30 days until expiration already exists in both S3 and ACM for: {domains}",
                "status": "success"
            }
    except RuntimeError as error:
        logger.error(error)
        raise


def should_provision(domains):
    """Determine whether a new certificate should be provisioned."""
    existing_cert = find_existing_cert(domains)
    if existing_cert:
        logger.info("Checking if certificate expires within 30 days.")
        now = datetime.datetime.now(datetime.timezone.utc)
        not_after = existing_cert['Certificate']['NotAfter']
        days_until_expired = (not_after - now).days
        if days_until_expired <= 30:
            logger.info(f"A new certificate will be provisioned. Days until current certificate expires: {days_until_expired}")
            return True
        else:
            logger.info(f"A new certificate is not needed. Days remaining on current certificate: {days_until_expired}")
            return False
    else:
        logger.info(f"No existing certificate found, a new one will be provisioned for: {domains}")
        return True


def find_existing_cert(domains):
    """Check to see if the certificate already exists."""
    logger.info(f"Checking to see if a certificate already exists for: {domains}")
    domains = frozenset(domains.split(','))

    client = boto3.client('acm')
    paginator = client.get_paginator('list_certificates')
    iterator = paginator.paginate(PaginationConfig={'MaxItems': 1000})

    for page in iterator:
        for cert in page['CertificateSummaryList']:
            cert = client.describe_certificate(CertificateArn=cert['CertificateArn'])
            sans = frozenset(cert['Certificate']['SubjectAlternativeNames'])
            if sans.issubset(domains):
                # Convert the frozenset back into a comma separated string
                logger.info(f"Found an existing certificate for: {','.join(list(domains))}")
                return cert

    return None


def provision_cert(email, domains, server):
    """Provision a new certificate using certbot."""
    logger.info(f"Calling certbot to provision a certificate for: {domains}")
    certbot.main.main([
        '--server', server,                # Letsencrypt server to use
        'certonly',                        # Obtain a cert but don't install it
        '-n',                              # Run in non-interactive mode
        '--agree-tos',                     # Agree to the terms of service,
        '--email', email,                  # Email
        '--dns-route53',                   # Use dns challenge with route53
        '-d', domains,                     # Domains to provision certs for
        # Override directory paths so script doesn't have to be run as root
        '--config-dir', '/tmp/config-dir/',
        '--work-dir', '/tmp/work-dir/',
        '--logs-dir', '/tmp/logs-dir/',
    ])

    first_domain = domains.split(',')[0]
    path = '/tmp/config-dir/live/' + first_domain + '/'
    logger.info(f"Done provisioning certificate for: {domains}")
    return {
        'certificate': read_file(path + 'cert.pem'),
        'private_key': read_file(path + 'privkey.pem'),
        'certificate_chain': read_file(path + 'chain.pem')
    }


# /tmp/config-dir
# ├── live
# │   └── [domain]
# │       ├── README
# │       ├── cert.pem
# │       ├── chain.pem
# │       ├── fullchain.pem
# │       └── privkey.pem
def upload_to_s3(s3_bucket):
    s3_prefix = 'certs'
    logger.info(f"Uploading certificate files to {s3_bucket}/{s3_prefix}.")
    client = boto3.client('s3')
    cert_dir = os.path.join('/tmp/config-dir', 'live')
    for dirpath, _dirnames, filenames in os.walk(cert_dir):
        for filename in filenames:
            local_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(local_path, cert_dir)
            s3_key = os.path.join(s3_prefix, relative_path)
            client.upload_file(local_path, s3_bucket, s3_key)
            delete_file(local_path)
    logger.info(f"Finished uploading certificate files to {s3_bucket}/{s3_prefix}.")


def upload_to_acm(cert, domains):
    """Upload a certificaste to ACM for AWS use and expiration tracking."""
    logger.info(f"Uploading certificate to ACM for: {domains}")
    existing_cert = find_existing_cert(domains)
    certificate_arn = existing_cert['Certificate']['CertificateArn'] if existing_cert else None

    client = boto3.client('acm')
    if certificate_arn:
        acm_response = client.import_certificate(
            CertificateArn=certificate_arn,
            Certificate=cert['certificate'],
            PrivateKey=cert['private_key'],
            CertificateChain=cert['certificate_chain']
        )
    else:
        acm_response = client.import_certificate(
            Certificate=cert['certificate'],
            PrivateKey=cert['private_key'],
            CertificateChain=cert['certificate_chain']
        )
    logger.info(f"Finished uploading certificate to ACM for: {domains}")
    return None if certificate_arn else acm_response['CertificateArn']


def read_file(path):
    with open(path, 'r') as file:
        contents = file.read()
    return contents


def delete_file(path):
    os.remove(path)
