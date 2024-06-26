from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_ecs_patterns as ecs_patterns,
    Stack,
    Duration,
    aws_ecr_assets,
    aws_lambda,
    aws_dynamodb,
    RemovalPolicy
)
from constructs import Construct
import os

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc(
            self, "StreamlitVPC", 
            max_azs = 2,
            )     # default is all AZs in region, 
                  # but you can limit to avoid reaching resource quota

        # Create ECS cluster
        cluster = ecs.Cluster(self, "StreamlitCluster", vpc=vpc)

        # Add an AutoScalingGroup with spot instances to the existing cluster
        cluster.add_capacity("AsgSpot",
            max_capacity=2,
            min_capacity=1,
            desired_capacity=2,
            instance_type=ec2.InstanceType("c5.xlarge"),
            spot_price="0.0735",
            # Enable the Automated Spot Draining support for Amazon ECS
            spot_instance_draining=True
        )

        # Build Dockerfile from local folder and push to ECR
        image = ecs.ContainerImage.from_asset(
            'streamlit_app',
            platform= aws_ecr_assets.Platform.LINUX_AMD64)

        # Create Fargate service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "StreamlitTicketClassifier",
            cluster=cluster,            # Required
            cpu=2048,                    # Default is 256 (512 is 0.5 vCPU, 2048 is 2 vCPU)
            desired_count=1,            # Default is 1
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image, 
                container_port=8501,
                ),
            memory_limit_mib=4096,      # Default is 512
            public_load_balancer=True)  # Default is True

        # Setup task auto-scaling
        scaling = fargate_service.service.auto_scale_task_count(
            max_capacity=10
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=80,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )
        
        # Policy for lambda function
        lambda_policy_doc = iam.PolicyDocument(
            statements=[
                # bedrock policy
                iam.PolicyStatement(
                    actions=[
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream"
                        ],
                    effect=iam.Effect.ALLOW,
                    resources=['*']
                ),
                # ec2 network policy
                iam.PolicyStatement(
                    actions=[
                        "ec2:DescribeInstances",
                        "ec2:CreateNetworkInterface",
                        "ec2:AttachNetworkInterface",
                        "ec2:DescribeNetworkInterfaces",
                        "autoscaling:CompleteLifecycleAction",
                        "ec2:DeleteNetworkInterface"
                        ],
                    effect=iam.Effect.ALLOW,
                    resources=['*']
                ),
                # textract policy
                iam.PolicyStatement(
                    actions=[
                        "textract:StartDocumentTextDetection",
                        "textract:StartDocumentAnalysis",
                        "textract:GetDocumentTextDetection",
                        "textract:GetDocumentAnalysis"
                        ],
                    effect=iam.Effect.ALLOW,
                    resources=['*']
                ),
                # s3 policy
                iam.PolicyStatement(
                    actions=[
                        "s3:GetObject",
                        "s3:GetBucketLocation",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                        "s3:ListMultipartUploadParts",
                        "s3:PutObject"
                        ],
                    effect=iam.Effect.ALLOW,
                    resources=["arn:aws:s3:::llm-showcase", "arn:aws:s3:::llm-showcase/*"]
                )
            ]
        )
        lambda_policy = iam.Policy(self,
                                   'lambda-permissions',
                                   document=lambda_policy_doc,
                                   policy_name='policy-for-langchain-lambda')
        lambda_role = iam.Role(self,
                               'lambda-role',
                               assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
                               role_name='role-for-langchain-lambda')
        
        lambda_role.attach_inline_policy(lambda_policy)

        # create a lambda function with docker
        #dockerfileDir = os.path.join('/', 'lambda')
        dockerfileDir_1 = 'lambda/classifier/'
        dockerfileDir_2 = 'lambda/keyinfo/'
        dockerfileDir_3 = 'lambda/summary/'
        dockerfileDir_4 = 'lambda/converter/'
        dockerfileDir_5 = 'lambda/store/'
        lambda_classifier = aws_lambda.DockerImageFunction(self, 'Lambdaclassifierdocker',
                                       code= aws_lambda.DockerImageCode.from_image_asset(dockerfileDir_1, 
                                                                        platform= aws_ecr_assets.Platform.LINUX_AMD64),
                                       function_name='LangchainClassifier',
                                       timeout=Duration.minutes(15),
                                       memory_size= 1024,
                                       vpc= vpc,
                                       role= lambda_role
                                       )
        
        lambda_keyinfo = aws_lambda.DockerImageFunction(self, 'Lambdakeyinfodocker',
                                       code= aws_lambda.DockerImageCode.from_image_asset(dockerfileDir_2, 
                                                                        platform= aws_ecr_assets.Platform.LINUX_AMD64),
                                       function_name='LangchainKeyinfo',
                                       timeout=Duration.minutes(15),
                                       memory_size= 1024,
                                       vpc= vpc,
                                       role= lambda_role
                                       )
        
        lambda_summary = aws_lambda.DockerImageFunction(self, 'Lambdasummarydocker',
                                       code= aws_lambda.DockerImageCode.from_image_asset(dockerfileDir_3, 
                                                                        platform= aws_ecr_assets.Platform.LINUX_AMD64),
                                       function_name='LangchainSummary',
                                       timeout=Duration.minutes(15),
                                       memory_size= 1024,
                                       vpc= vpc,
                                       role= lambda_role
                                       )
        lambda_converter = aws_lambda.DockerImageFunction(self, 'Lambdaconverterdocker',
                                       code= aws_lambda.DockerImageCode.from_image_asset(dockerfileDir_4, 
                                                                        platform= aws_ecr_assets.Platform.LINUX_AMD64),
                                       function_name='ConvertToPkl',
                                       timeout=Duration.minutes(15),
                                       memory_size= 1024,
                                       vpc= vpc,
                                       role= lambda_role
                                       )
        
        # Adding DynamoDB table to save paper metadata
        dynamodb_table = aws_dynamodb.Table(self, 
                                            "DynamoDBMeta",
                                            table_name='PapersIdp',
                                            partition_key= aws_dynamodb.Attribute(
                                                name='PaperClass',
                                                type=aws_dynamodb.AttributeType.STRING
                                            ),
                                            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
                                            removal_policy=RemovalPolicy.DESTROY,
                                            sort_key= aws_dynamodb.Attribute(
                                                name='CreatedAt',
                                                type=aws_dynamodb.AttributeType.NUMBER
                                            )
                                            ) 

        # Policy for lambda function storing metadata
        lambda_policy_doc_2 = iam.PolicyDocument(
            statements=[
                # ec2 network policy
                iam.PolicyStatement(
                    actions=[
                        "ec2:DescribeInstances",
                        "ec2:CreateNetworkInterface",
                        "ec2:AttachNetworkInterface",
                        "ec2:DescribeNetworkInterfaces",
                        "autoscaling:CompleteLifecycleAction",
                        "ec2:DeleteNetworkInterface"
                        ],
                    effect=iam.Effect.ALLOW,
                    resources=['*']
                ),
                # s3 policy
                iam.PolicyStatement(
                    actions=[
                        "s3:GetObject",
                        "s3:GetBucketLocation",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                        "s3:ListMultipartUploadParts",
                        "s3:PutObject"
                        ],
                    effect=iam.Effect.ALLOW,
                    resources=["arn:aws:s3:::llm-showcase", "arn:aws:s3:::llm-showcase/*"]
                ),
                # DynamoDB policy
                iam.PolicyStatement(
                    actions=[
                        "dynamodb:BatchGet*",
                        "dynamodb:DescribeStream",
                        "dynamodb:DescribeTable",
                        "dynamodb:Get*",
                        "dynamodb:Query",
                        "dynamodb:Scan",
                        "dynamodb:BatchWrite*",
                        "dynamodb:CreateTable",
                        "dynamodb:Update*",
                        "dynamodb:PutItem"
                        ],
                    effect=iam.Effect.ALLOW,
                    resources=[dynamodb_table.table_arn]
                )
            ]
        )
        lambda_policy_2 = iam.Policy(self,
                                   'lambda-permissions-storeMet',
                                   document=lambda_policy_doc_2,
                                   policy_name='policy-for-lambda-storeMet')
        lambda_role_2 = iam.Role(self,
                               'lambda-role-storeMet',
                               assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
                               role_name='role-for-lambda-storeMet')
        
        lambda_role_2.attach_inline_policy(lambda_policy_2)

        # lambda for storing metadata
        lambda_storing = aws_lambda.DockerImageFunction(self, 'Lambdastoringdocker',
                                       code= aws_lambda.DockerImageCode.from_image_asset(dockerfileDir_5, 
                                                                        platform= aws_ecr_assets.Platform.LINUX_AMD64),
                                       function_name='StoreInfo',
                                       timeout=Duration.minutes(15),
                                       memory_size= 1024,
                                       vpc= vpc,
                                       role= lambda_role_2
                                       )

        # Add policies to task role
        fargate_service.task_definition.add_to_task_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions = ["lambda:InvokeFunction"],
            resources = [lambda_classifier.function_arn,
                         lambda_keyinfo.function_arn,
                         lambda_summary.function_arn,
                         lambda_converter.function_arn,
                         lambda_storing.function_arn],
            )
        )
        fargate_service.task_definition.add_to_task_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions = ["s3:GetObject",
                    "s3:GetBucketLocation",
                    "s3:ListBucket",
                    "s3:ListBucketMultipartUploads",
                    "s3:ListMultipartUploadParts",
                    "s3:PutObject"],
            resources = ["arn:aws:s3:::llm-showcase", "arn:aws:s3:::llm-showcase/*"],
            )
        )
        fargate_service.task_definition.add_to_task_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions = [
                    "textract:StartDocumentTextDetection",
                    "textract:StartDocumentAnalysis",
                    "textract:GetDocumentTextDetection",
                    "textract:GetDocumentAnalysis"],
            resources = ["*"],
            )
        )