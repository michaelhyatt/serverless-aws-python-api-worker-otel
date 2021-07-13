# Distributed tracing example with Elastic APM JS client, 2 Python lambdas and OpenTelemetry agents.

This example demonstrates how to setup a pair of Python lambdas calling each other using HTTP/API-GW and invoke them using a locally running nodejs service instrumented with [Elastic APM JS agent](https://www.elastic.co/guide/en/apm/agent/nodejs/current/index.html). The provided setup works with [AWS Distro for OpenTelemetry for Lambda (ADOT)](https://aws-otel.github.io/docs/getting-started/lambda/lambda-python) by using the provided auto-instrumentation combined with manual instrumentation to trace the lambda code in `handler.py`. ADOT configuration is captured in `collector.yaml` file.

## Known limitations
The provided lambdas require custom handler script to be configured with `AWS_LAMBDA_EXEC_WRAPPER` environment variable due to the bug with supporting the `traceparent` header propagation captured [here](https://github.com/aws-observability/aws-otel-lambda/issues/109).

## Prerequisites
* Installed [npm and nodejs](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
* [Serverless](https://www.serverless.com/) framework.
* Python 3.8 and pip3
* Git.

## Setup
### Step 1 - get the code and install dependencies.
Before running the example, clone the repo, install the required nodejs modules.
```
git clone https://github.com/michaelhyatt/serverless-aws-python-api-worker-otel
cd serverless-aws-python-api-worker-otel
npm install --save-dev
pip3 install -r requirements.txt
```

### Step 2 - create AWS access key with the following permissions
Follow the [Access key setup instructions](https://www.serverless.com/framework/docs/providers/aws/guide/credentials/#create-an-iam-user-and-access-key).
The key needs to have the following policies attached. Since this is a test environment, the policies are somewhat excessive, so feel free to narrow it down by experimenting with a more contained set:
* AmazonS3FullAccess
* CloudWatchLogsFullAccess
* AmazonAPIGatewayAdministrator
* AWSCloudFormationFullAccess
* AWSLambda_FullAccess

### Step 3 - create `env.json` file
`env.json` file contains the connection details for Elastic APM server (Elastic Cloud is a good option here) and AWS region where the lambdas need to be deployed. Copy it from the provided template and update with correct details.
```
cp env.json.template env.json
# Edit `env.json` to update the correct values
```

## Deployment
Deploy the lambdas and note the full URL of the provide API (consumer lambda) to be used to invoke it.
```
serverless deploy
```

## Usage
Invoke the deployed lambdas using the provided client.js using the URL from the previous step:
```
NODE_DEBUG=request node client.js https://XXXXXXXXX.execute-api.ap-southeast-2.amazonaws.com/dev/produce
```
It should produce something similar in the output with `traceparent` headers being sent from the `client.js` side:
```
> NODE_DEBUG=request node client.js https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com/dev/produce
REQUEST {
  url: 'https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com/dev/produce',
  headers: {
    traceparent: '00-9a6c8a973e20d2e902a4ab877538cda2-0a338cb257d3e1d7-01',
    'Content-Type': 'application/json'
  },
  body: '{"name":"John"}',
  callback: [Function (anonymous)],
  method: 'POST'
}
REQUEST make request https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com/dev/produce
REQUEST onRequestResponse https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com/dev/produce 200 {
  'content-type': 'application/json',
  'content-length': '141',
  connection: 'close',
  date: 'Sun, 11 Jul 2021 03:25:52 GMT',
}
REQUEST reading response's body
REQUEST finish init function https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com/dev/produce
REQUEST response end https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com/dev/produce 200 {
  'content-type': 'application/json',
  'content-length': '141',
  connection: 'close',
  date: 'Sun, 11 Jul 2021 03:25:52 GMT',
}
REQUEST end event https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com/dev/produce
REQUEST has body https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com/dev/produce 141
REQUEST emitting complete https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com/dev/produce
Status: 200
{"message":"The response from the producer is {\"message\":\"Hello, the current time is 03:25:52 GMT+0000 (Coordinated Universal Time).\"}."}

```

## Kibana APM should start showing traces.

