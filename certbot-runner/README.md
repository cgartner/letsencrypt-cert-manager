# certbot-runner

This Lambda is invoked by the StepFunction defined in [certbot-ventilator](https://gitlab.pixsystem.net/Lambda/certbot-ventilator). An event is passed
in which contains keys used for the management a single certificate's lifecyle.

If a certificate doesn't exist in ACM, a new one is provisioned. If an existing
certificate is found but expires in less than 30 days, a new one is provisioned
as well. Newly provisioned certificates are placed in both ACM and S3 for use by
internal and external services.

**Note:** This stack must be deployed before the [certbot-ventilator](https://gitlab.pixsystem.net/Lambda/certbot-ventilator) so it can setup an Export.

## Usage

While this Lambda is typically called from [certbot-ventilator](https://gitlab.pixsystem.net/Lambda/certbot-ventilator), you can also invoke
this Lambda with a standalone event to provision a single certificate

### Event
**Note:** The `domains` key can be one or many domains, as this value gets passed
into _Subject Alternative Name (SAN)_ of the certificate. If multiple domains are
supplied, the _first_ domain name is used as the name of the certificate in ACM
and S3.

```json
{
    "certbot_server": "https://acme-staging-v02.api.letsencrypt.org/directory",
    "domains": "test.presidio.pxsys.net",
    "email": "itops@pixsystem.com",
    "s3_bucket": "accountcloudformationconstants-deploymentbucket-1dfa1c7nemvwc"
}
```

| name            | type   | description                                                        |
| ----            | ------ | ---------------------------------------------                      |
| certbot_server  | String | URL of the LetsEncrypt server for certbot to use                   |
| domains         | String | One or more domains to generate a certificate for, comma-separated |
| email           | String | Email address to assign to certificates                            |
| s3_bucket       | String | The S3 bucket to store certificates/keys in                        |

### Output
If a new certificate was provisioned:
```json
{
  "output": {
    "message": "A new certificate has been provisioned and uploaded to both S3 and ACM for: test.presidio.pxsys.net",
    "status": "success"
  }
}
```

If a certificate with more than 30 days left exists:
```json
{
  "output": {
    "message": "A certificate with at least 30 days until expiration already exists in both S3 and ACM for: test.presidio.pxsys.net",
    "status": "success"
  }
}
```

## Dependencies

- LetsEncrypt/Certbot

### AWS

- Lambda
- Route53

## Contributing

### Installing dependencies

```bash
make install-dev
```

### Running AWS SAM Local
AWS SAM Local is a great way to test serverless applicationals locally in a docker container. [Check it out](https://github.com/awslabs/aws-sam-local).

Once AWS SAM Local is installed, prepare your SAM container by running the command below.
(**Note:** Any additional external libraries must be added to _requirements.txt_ to be successfully packaged by the below command.)
```bash
sam build --use-container
```

After this has been done, you can initialize a SAM Local run with the following code:
```bash
sam local invoke "CertbotRunner" -e tests/payloads/success.json
```

### Running tests

To run our unit tests you can run:

```bash
make test
```

This will generate a coverage report in `coverage_html/index.html`

### Running lint

To lint the code run:

```bash
make lint
```

If you don't get any output that means your linting passed.

## Additional Resources

- [Deploying Certbot in AWS Lambda](https://arkadiyt.com/2018/01/26/deploying-effs-certbot-in-aws-lambda/) - Inspiration for the Lambda came from this post
- [Sample Map State](https://docs.aws.amazon.com/step-functions/latest/dg/sample-map-state.html) - Map State Examples

## Authors

- **Chad Gartner** - _Initial work_
