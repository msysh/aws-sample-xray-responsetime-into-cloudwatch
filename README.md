# AWS X-Ray response time into Amazon CloudWatch Metrics

This is a sample AWS SAM template that registers client response times traced by a specific group of AWS X-Ray as custom metrics in Amazon CloudWatch.

## Build

```
sam build --parameter-overrides "ParameterKey=XRayGroupName,ParameterValue=XRayGroupName"
```

## Deploy

```
sam deploy --guided
```