# Serverless Framework Python API-GW Producer-Consumer on AWS

This template demonstrates how to develop and deploy a simple API-GW-based producer-consumer service running on AWS Lambda using the traditional Serverless Framework. It allows to accept messages, for which computation might be time or resource intensive, and offload their processing to an asynchronous background process for a faster and more resilient system.

## Tracing is implemented using X-Ray

## Anatomy of the template

This template defines two functions, `producer` and `consumer`. First of them, `producer`, is triggered by `http` event type, accepts JSON payload and sends it to another lambda listening on the API-GW for further processing. 

## Usage

### Deployment

This example requires `git`, `serverless` framework and `npm` to be installed.

Clone the repo, install npm dependencies
```
git clone https://github.com/michaelhyatt/serverless-aws-python-sqs-worker-otel
cd serverless-aws-python-sqs-worker-otel
npm install
npm install --save-dev serverless-plugin-lambda-insights
npm install --save-dev serverless-pseudo-parameters
```

Copy `env.json.template` into `env.json` and update the right region and APM server credentials:
```json
{
    "aws-region": "ap-southeast-1",
    "apm-server-url": "YOURCLUSTER.apm.australia-southeast1.gcp.elastic-cloud.com:443",
    "apm-server-token": "YOURTOKEN"
}

```

Deploy the lambdas
```
serverless deploy
```

To remove lambdas
```
serverless remove
```


After running deploy, you should see output similar to:

```bash
Serverless: Packaging service...
Serverless: Excluding development dependencies...
Serverless: Creating Stack...
Serverless: Checking Stack create progress...
........
Serverless: Stack create finished...
Serverless: Uploading CloudFormation file to S3...
Serverless: Uploading artifacts...
Serverless: Uploading service aws-python-sqs-worker.zip file to S3 (1.04 KB)...
Serverless: Validating template...
Serverless: Updating Stack...
Serverless: Checking Stack update progress...
................................................
Serverless: Stack update finished...
Service Information
service: aws-python-sqs-worker
stage: dev
region: us-east-1
stack: aws-python-sqs-worker-dev
resources: 17
api keys:
  None
endpoints:
  POST - https://xxxxxxx.execute-api.us-east-1.amazonaws.com/dev/produce
functions:
  producer: aws-python-sqs-worker-dev-producer
  consumer: aws-python-sqs-worker-dev-consumer
layers:
  None
```

_Note_: In current form, after deployment, your API is public and can be invoked by anyone. For production deployments, you might want to configure an authorizer. For details on how to do that, refer to [http event docs](https://www.serverless.com/framework/docs/providers/aws/events/apigateway/).

### Invocation

After successful deployment, you can now call the created API endpoint with `POST` request to invoke `producer` function:

```bash
curl --request POST 'https://xxxxxx.execute-api.us-east-1.amazonaws.com/dev/produce' --header 'Content-Type: application/json' --data-raw '{"name": "John"}'
```