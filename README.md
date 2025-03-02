# SQS Security Guardrail

## Description
This project provides a **security guardrail** for Amazon SQS queues using **AWS CloudFormation** and an **AWS Lambda** function written in **Python**. It ensures that newly created queues comply with security policies.

## Features
- **CloudFormation**: Deploys all necessary AWS resources.
- **Lambda Function**: Triggered on SQS queue creation, checking:
  - **VPC Endpoint** usage.
  - **Encryption at rest** enabled.
  - **Customer-Managed Key (CMK)** instead of AWS-managed key.
  - Required tags (`Name`, `Created By`, `Cost Center`).
- **AWS EventBridge**: Detects new queues and triggers Lambda.
- **SNS Notifications**: Sends alerts if compliance is not met.
- **GitHub Actions**: CI/CD for automatic deployment.
- **Modular Code**: Separated into reusable functions for maintainability.
- **Error Handling**: Captures and logs errors properly.
- **Inline Documentation**: Code includes explanatory comments for clarity.

## Requirements
Before deploying, ensure you have:
- **AWS account** with necessary permissions.
- **Configured credentials** (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`).
- **S3 Bucket** to host Lambda code.
- **OrganizationId** to enable control tower validation

## Deployment Instructions
### Step-by-Step Deployment
#### Using AWS CLI
1. Ensure you have AWS CLI installed and configured.
2. Run the following command to deploy the CloudFormation stack:
```sh
aws iam create-policy \
    --policy-name SQSGuardrailPermissionBoundary \
    --policy-document file://permission_boundary.json

aws cloudformation deploy \
    --stack-name SQSGuardrail \
    --template-file template.yaml \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
        LambdaRuntime=python3.9 \
        MemorySize=128 \
        PermissionBoundaryArn=arn:aws:iam::$(aws sts get-caller-identity --query "Account" --output text):policy/SQSGuardrailPermissionBoundary \
        SNS
        OrganizationUnitId= "xxxxxxx"\
        S3BucketName= "BucketLambdaCode" \
        
```
3. Note: Replace the values of OrganizationUnitId and S3BucketName

#### Using AWS Console
1. Navigate to **AWS CloudFormation**.
2. Click on **Create stack** → **With new resources**.
3. Upload the `template.yaml` file.
4. Specify parameters such as `LambdaRuntime`, `MemorySize`, `PermissionBoundaryArn`, `OrganizationUnitId`, and `S3BucketName`.
5. Click **Next**, review, and deploy.

### Explanation of Parameters
- `LambdaRuntime`: The runtime environment for the Lambda function (default: `python3.9`).
- `MemorySize`: Memory allocated to the Lambda function (default: `128`).
- `PermissionBoundaryArn`: ARN of the IAM permission boundary to restrict permissions.
- `OrganizationUnitId`: ID of Organization Unit
- `S3BucketName`: Name of S3 Bucket

## Design Decisions
### Permission Boundary Implementation
The permission boundary restricts the IAM role of the Lambda function, ensuring it only has the necessary permissions. This enhances security by preventing privilege escalation.

### Multi-Account Extension
The solution is designed to be **easily extendable** for a multi-account environment:
- Can be integrated with **AWS Organizations**.
- **Control Tower guardrails** can enforce security policies across accounts.
- **Centralized logging & monitoring** can be set up using AWS CloudTrail and AWS Security Hub.

## Verify Deployment
Once deployed, verify everything is working correctly:
- **AWS CloudFormation** → Stack `SQSGuardrail`.
- **AWS Lambda** → Function `SQSGuardrailLambda`.
- **AWS SNS** → Notifications in case of security violations.

## GitHub Actions CI/CD
This project includes a GitHub Actions workflow for automating deployments.

### Workflow Setup
1. Ensure you have the following repository secrets configured in GitHub:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `SNS_TOPIC_ARN`
   - `SNS_TOPIC_ARN`
   - `SNS_TOPIC_ARN`
2. The GitHub Actions workflow (`.github/workflows/deploy.yml`) will:
   - Validate the CloudFormation template.
   - Package and upload Lambda code to an S3 bucket.
   - Deploy the CloudFormation stack.

### Running the Workflow
- On every push to the `main` branch, the workflow runs automatically.
- You can manually trigger the workflow in the GitHub Actions tab.

## Contribution
If you'd like to improve this project, fork the repository, create a new branch, and submit a **pull request**.

## Author
Kevin Toledo - 2025

