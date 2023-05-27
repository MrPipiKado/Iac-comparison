from aws_cdk import Stack  # Duration,; aws_sqs as sqs,
from constructs import Construct

from cdk.application_nested_stack import ApplicationLayerStack
from cdk.bastion_nested_stack import BastionLayerStack
from cdk.db_nested_stack import DBLayerStack
from cdk.sg_nested_stack import SGLayerStack
from cdk.vpc_nested_stack import NetworkLayerStack


class CdkStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, env_config: dict, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.env_config = env_config
        self.network_layer = NetworkLayerStack(self, "NetworkLayerStack", construct_id)

        self.sg_layer = SGLayerStack(
            self,
            "SGLayerStack",
            self.network_layer.application_vpc,
            self.network_layer.database_vpc,
            construct_id,
            self.env_config,
        )

        self.application_layer = ApplicationLayerStack(
            self,
            "ApplicationStack",
            self.network_layer.application_vpc,
            self.network_layer.app_public_subnets,
            self.sg_layer.load_balancer_sg,
            self.sg_layer.application_sg,
            construct_id,
            self.env_config["App"],
        )

        self.db_layer = DBLayerStack(
            self,
            "DBLayerSteck",
            self.sg_layer.db_sg,
            self.network_layer.db_vpc,
            self.network_layer.db_private_subnets,
            construct_id,
            self.env_config["DB"],
        )
        self.application_layer.add_dependency(self.db_layer)

        self.bastion_layer = BastionLayerStack(
            self,
            "BastionStack",
            self.network_layer.application_vpc,
            self.network_layer.app_public_subnets,
            self.sg_layer.bastion_sg,
            self.env_config["BastionHost"],
        )
