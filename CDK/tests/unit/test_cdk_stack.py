import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk.cdk_stack import CdkStack
from cdk.vpc_nested_stack import NetworkLayerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk/cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkStack(app, "cdk")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::CloudFormation::Stack", 1)
