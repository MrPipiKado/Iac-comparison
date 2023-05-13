from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct
from cdk.vpc_nested_stack import NetworkLayerStack
from cdk.sg_nested_stack import SGLayerStack
from cdk.application_nested_stack import ApplicationLayerStack
from cdk.db_nested_stack import DBLayerStack
class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        network_layer = NetworkLayerStack(self, "NetworkLayerStack")

        sg_layer = SGLayerStack(self, "SGLayerStack", network_layer.application_vpc, network_layer.database_vpc)

        application_layer = ApplicationLayerStack(self, "ApplicationStack", network_layer.application_vpc, network_layer.app_public_subnets, sg_layer.load_balancer_sg, sg_layer.application_sg)

        db_layer = DBLayerStack(self, "DBLayerSteck", sg_layer.db_sg, network_layer.db_vpc, network_layer.db_private_subnets)
