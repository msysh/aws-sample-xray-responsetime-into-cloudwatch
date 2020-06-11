import os
import logging
import time
import boto3
import botocore

XRAY_GROUP_NAME = os.getenv('XRAY_GROUP_NAME', 'default')
CW_METRICS_NAMESPACE = os.getenv('CW_METRICS_NAMESPACE', 'X-Ray/Custome Metrics')
SAMPLIG_INTERVAL = int(os.getenv('SAMPLING_INTERVAL', '60'))

level = logging.getLevelName(os.getenv('LOG_LEVEL', 'INFO'))
if not isinstance(level, int):
    level = logging.INFO

logger = logging.getLogger(__name__)
logger.setLevel(level)

cloudwatch = boto3.client('cloudwatch')
xray = boto3.client('xray')

def get_response_time(executed_time):
    try:
        response = xray.get_service_graph(
            StartTime = executed_time - SAMPLIG_INTERVAL,
            EndTime = executed_time,
            GroupName = XRAY_GROUP_NAME
        )
        logger.debug(f"Response : {response}")
    except botocore.exceptions.ClientError as error:
        logger.error(f"Error : {error}")
        raise error

    return response

def put_metrics(executed_time, values, counts):
    try:
        response = cloudwatch.put_metric_data(
            Namespace = CW_METRICS_NAMESPACE,
            MetricData = [
                {
                    'MetricName': 'Response Time',
                    'Dimensions': [
                        { 'Name': 'GroupName', 'Value': XRAY_GROUP_NAME }
                    ],
                    'Timestamp': executed_time,
                    'Values': values,
                    'Counts': counts,
                    'Unit': 'Seconds'
                }
            ]
        )
        logger.debug(f"Response: {response}")
    except botocore.exceptions.ClientError as error:
        logger.error(f"Error : {error}")

    return response

def execute(executed_time):
    response_time = get_response_time(executed_time)

    service_client = [s for s in response_time['Services'] if s['Type'] == 'client'][0]
    edge = [e for e in service_client['Edges'] if 'ResponseTimeHistogram' in e][0]
    end_time = edge['EndTime']
    # TODO : if len(ResponseTimeHistogram) > 150
    values = [v['Value'] for v in edge['ResponseTimeHistogram']]
    counts = [v['Count'] for v in edge['ResponseTimeHistogram']]

    put_metrics(end_time, values, counts)


def lambda_handler(event, context):
    executed_time = int(time.time())
    logger.info(f"Current time : {executed_time}")
    logger.debug(event)
    execute(executed_time)
