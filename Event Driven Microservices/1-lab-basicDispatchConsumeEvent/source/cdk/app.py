#!/usr/bin/env python3

from aws_cdk import aws_events as _eb
from aws_cdk import aws_events_targets as _ebt
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import core


class CdkStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Model all required resources
        
        ## IAM Roles
        lambda_role = _iam.Role(
            self,
            id='lab1-bdc-lambda-role',
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com'))


        ## EventBridge
        eb = _eb.EventBus(
            self, id="lab1-bdc-eventbus", event_bus_name="lab1-bdc-eventbus")
        eb_pattern = _eb.EventPattern(
            detail_type=["message-received"],
        )

        ## AWS Lambda Functions
        fnLambda_dispatch = _lambda.Function(
            self, 
            "lab1-bdc-function-dispatch",
            code=_lambda.AssetCode("../lambda-functions/dispatch-function"),
            handler="app.handler",
            timeout=core.Duration.seconds(60),
            role=lambda_role,
            runtime=_lambda.Runtime.PYTHON_3_8)
        fnLambda_dispatch.add_environment("EVENT_BUS_NAME", eb.event_bus_name)


        fnLambda_consume = _lambda.Function(
            self, 
            "lab1-bdc-function-consume",
            code=_lambda.AssetCode("../lambda-functions/consume-function"),
            handler="app.handler",
            role=lambda_role,
            timeout=core.Duration.seconds(60),
            runtime=_lambda.Runtime.PYTHON_3_8)

        cw_policy_statement = _iam.PolicyStatement(effect=_iam.Effect.ALLOW)
        cw_policy_statement.add_actions("logs:CreateLogGroup")
        cw_policy_statement.add_actions("logs:CreateLogStream")
        cw_policy_statement.add_actions("logs:PutLogEvents")
        cw_policy_statement.add_actions("logs:DescribeLogStreams")
        cw_policy_statement.add_resources("*")
        lambda_role.add_to_policy(cw_policy_statement)
        
        eb_policy_statement = _iam.PolicyStatement(effect=_iam.Effect.ALLOW)
        eb_policy_statement.add_actions("events:PutEvents")
        eb_policy_statement.add_resources(eb.event_bus_arn)
        lambda_role.add_to_policy(eb_policy_statement)

        _eb.Rule(
            self,
            id="lab1-bdc-eventRule",
            description="A basic rule sample",
            enabled=True,
            event_bus=eb,
            event_pattern=eb_pattern,
            rule_name="BDC-BasicDispatchConsume",
            targets=[_ebt.LambdaFunction(handler=fnLambda_consume)])

app = core.App()
stack = CdkStack(app, "Lab1-BasicDispatchConsume")
core.Tags.of(stack).add('Name','Lab1-BasicDispatchConsume')

app.synth()
