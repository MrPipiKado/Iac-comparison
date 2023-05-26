import aws_cdk as core
import aws_cdk.assertions as assertions
from aws_cdk import Stack

from cdk.cdk_stack import CdkStack
from cdk.config_reader import ConfigReader

configs = ConfigReader("./config")
from cdk.vpc_nested_stack import NetworkLayerStack
from cdk.sg_nested_stack import SGLayerStack
from cdk.application_nested_stack import ApplicationLayerStack
from cdk.db_nested_stack import DBLayerStack
from cdk.bastion_nested_stack import BastionLayerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk/cdk_stack.py
def test_nested_stack_count():
    app = core.App()
    for env in configs.config_names:

        stack = CdkStack(app, env, configs.configs_with_names[env])
        template = assertions.Template.from_stack(stack)

        template.resource_count_is("AWS::CloudFormation::Stack", 5)

def test_vpc_count():
    app = core.App()
    for env in configs.config_names:

        stack = Stack(app, 'TestStack')
        network_layer_stack = NetworkLayerStack(stack, "NetworkLayerStack", env)
        template = assertions.Template.from_stack(network_layer_stack)

        template.resource_count_is("AWS::EC2::VPC", 2)

def test_subnet_count():
    app = core.App()
    for env in configs.config_names:

        stack = Stack(app, 'TestStack')
        network_layer_stack = NetworkLayerStack(stack, "NetworkLayerStack", env)
        template = assertions.Template.from_stack(network_layer_stack)

        template.resource_count_is("AWS::EC2::Subnet", 6)

def test_sg_count():
    app = core.App()
    for env in configs.config_names:

        stack = Stack(app, 'TestStack')
        network_layer_stack = NetworkLayerStack(stack, "NetworkLayerStack", env)
        sg_layer_stack = SGLayerStack(stack, "SGLayerStack", network_layer_stack.application_vpc, network_layer_stack.database_vpc, env, configs.configs_with_names[env])
        template = assertions.Template.from_stack(sg_layer_stack)

        template.resource_count_is("AWS::EC2::SecurityGroup", 4)

def test_sg_count():
    app = core.App()
    for env in configs.config_names:

        stack = Stack(app, 'TestStack')
        network_layer_stack = NetworkLayerStack(stack, "NetworkLayerStack", env)
        sg_layer_stack = SGLayerStack(stack, "SGLayerStack", network_layer_stack.application_vpc, network_layer_stack.database_vpc, env, configs.configs_with_names[env])
        template = assertions.Template.from_stack(sg_layer_stack)

        template.resource_count_is("AWS::EC2::SecurityGroup", 4)

def test_alb_creation():
    app = core.App()
    for env in configs.config_names:

        stack = Stack(app, 'TestStack')
        network_layer_stack = NetworkLayerStack(stack, "NetworkLayerStack", env)
        sg_layer_stack = SGLayerStack(stack, "SGLayerStack", network_layer_stack.application_vpc, network_layer_stack.database_vpc, env, configs.configs_with_names[env])
        application_layer = ApplicationLayerStack(stack, "ApplicationStack", network_layer_stack.application_vpc,
                                                  network_layer_stack.app_public_subnets, sg_layer_stack.load_balancer_sg,
                                                  sg_layer_stack.application_sg, env, configs.configs_with_names[env]["App"])
        template = assertions.Template.from_stack(application_layer)

        template.resource_count_is("AWS::ElasticLoadBalancingV2::LoadBalancer", 1)

def test_db_creation():
    app = core.App()
    for env in configs.config_names:
        stack = Stack(app, 'TestStack')
        network_layer_stack = NetworkLayerStack(stack, "NetworkLayerStack", env)
        sg_layer_stack = SGLayerStack(stack, "SGLayerStack", network_layer_stack.application_vpc,
                                      network_layer_stack.database_vpc, env, configs.configs_with_names[env])
        db_layer = DBLayerStack(stack, "DBLayerSteck", sg_layer_stack.db_sg, network_layer_stack.db_vpc, network_layer_stack.db_private_subnets, configs.configs_with_names[env]["DB"])
        template = assertions.Template.from_stack(db_layer)

        template.resource_count_is("AWS::RDS::DBInstance", 1)

def test_bastion_creation():
    app = core.App()
    for env in configs.config_names:
        stack = Stack(app, 'TestStack')
        network_layer_stack = NetworkLayerStack(stack, "NetworkLayerStack", env)
        sg_layer_stack = SGLayerStack(stack, "SGLayerStack", network_layer_stack.application_vpc,
                                      network_layer_stack.database_vpc, env, configs.configs_with_names[env])
        bastion_layer = BastionLayerStack(stack, "BastionStack", network_layer_stack.application_vpc, network_layer_stack.app_public_subnets, sg_layer_stack.bastion_sg, configs.configs_with_names[env]["BastionHost"])
        template = assertions.Template.from_stack(bastion_layer)

        template.resource_count_is("AWS::EC2::Instance", 1)