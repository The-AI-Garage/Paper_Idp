from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_ecs_patterns as ecs_patterns,
    Stack,
    Duration,
    aws_ecr_assets,
    aws_lambda
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
        dockerfileDir = 'lambda'
        lambda_function = aws_lambda.DockerImageFunction(self, 'LambdaDockerImage',
                                       code= aws_lambda.DockerImageCode.from_image_asset(dockerfileDir, 
                                                                        platform= aws_ecr_assets.Platform.LINUX_AMD64),
                                       function_name='LangchainOrquestrator',
                                       timeout=Duration.minutes(15),
                                       vpc= vpc,
                                       role= lambda_role
                                       )
        
        # Add policies to task role
        fargate_service.task_definition.add_to_task_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions = ["lambda:InvokeFunction"],
            resources = [lambda_function.function_arn],
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