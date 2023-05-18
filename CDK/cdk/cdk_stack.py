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
from cdk.bastion_nested_stack import BastionLayerStack
class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, env_config: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.env_config = env_config
        network_layer = NetworkLayerStack(self, "NetworkLayerStack")

        sg_layer = SGLayerStack(self, "SGLayerStack", network_layer.application_vpc, network_layer.database_vpc, self.env_config)

        application_layer = ApplicationLayerStack(self, "ApplicationStack", network_layer.application_vpc, network_layer.app_public_subnets, sg_layer.load_balancer_sg, sg_layer.application_sg, self.env_config["App"])

        db_layer = DBLayerStack(self, "DBLayerSteck", sg_layer.db_sg, network_layer.db_vpc, network_layer.db_private_subnets, self.env_config["DB"])

        bastion_layer = BastionLayerStack(self, "BastionStack", network_layer.application_vpc, network_layer.app_public_subnets, sg_layer.bastion_sg, self.env_config["BastionHost"])