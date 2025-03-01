# SecretCode: Kgtoledoc-2025-JpSYN
import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client('sqs')
kms = boto3.client('kms')
ec2 = boto3.client('ec2')
sns = boto3.client('sns')

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    sns_topic_arn = os.getenv('SNS_TOPIC_ARN')
    
    for record in event.get('Records', []):
        message = json.loads(record['body'])
        queue_url = message.get('queueUrl')
        
        if not queue_url:
            logger.error("No queue URL found in event.")
            continue
        
        queue_attributes = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['All'])
        attributes = queue_attributes.get('Attributes', {})
        
        errors = []
        
        # Check for encryption-at-rest
        if 'KmsMasterKeyId' not in attributes:
            errors.append("Queue does not use a customer-managed CMK.")
        
        # Check VPC endpoint for SQS
        vpc_endpoints = ec2.describe_vpc_endpoints(Filters=[{'Name': 'service-name', 'Values': ['com.amazonaws.sqs']}])
        if not vpc_endpoints['VpcEndpoints']:
            errors.append("No VPC endpoint found for SQS.")
        
        # Check required tags
        required_tags = ['Name', 'Created By', 'Cost Center']
        tag_response = sqs.list_queue_tags(QueueUrl=queue_url)
        tags = tag_response.get('Tags', {})
        for tag in required_tags:
            if tag not in tags:
                errors.append(f"Missing required tag: {tag}")
        
        # Alerting if there are issues
        if errors:
            error_message = f"SQS Security Compliance Issues for {queue_url}: " + ", ".join(errors)
            logger.error(error_message)
            
            if sns_topic_arn:
                sns.publish(TopicArn=sns_topic_arn, Message=error_message, Subject="SQS Security Compliance Alert")
    
    return {"statusCode": 200, "body": json.dumps("Execution completed.") }
