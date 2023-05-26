from typing import Dict, List

from aws_cdk import (
    NestedStack,
    aws_ec2 as ec2,
)
from constructs import Construct


class NetworkLayerStack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, env_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        self.application_vpc = ec2.Vpc(self, "APP_VPC",
                                       vpc_name=f"{env_name}_APP_VPC",
                                       cidr="10.0.0.0/16",
                                       max_azs=2,
                                       enable_dns_hostnames=True,
                                       enable_dns_support=True,
                                       subnet_configuration=[
                                           ec2.SubnetConfiguration(
                                               subnet_type=ec2.SubnetType.PUBLIC,
                                               name=f"{env_name}_APP_VPC_Public",
                                               cidr_mask=24
                                           ),
                                           ec2.SubnetConfiguration(
                                               subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                                               name=f"{env_name}_APP_VPC_Private",
                                               cidr_mask=24
                                           )
                                       ]
                                       )

        self.database_vpc = ec2.Vpc(self, 'DB_VPC',
                                    vpc_name=f"{env_name}_DB_VPC",
                                    cidr='192.168.0.0/16',
                                    max_azs=2,
                                    enable_dns_hostnames=True,
                                    enable_dns_support=True,
                                    subnet_configuration=[
                                        ec2.SubnetConfiguration(
                                            subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                                            name=f"{env_name}_DB_VPC_Isolated",
                                            cidr_mask=24
                                        ),
                                    ],
                                    )
        self.peering_connection = ec2.CfnVPCPeeringConnection(
            self, "AppDbVpcPeeringConn",
            vpc_id=self.application_vpc.vpc_id,
            peer_vpc_id=self.database_vpc.vpc_id
        )

        self.application_public_subnets = self.application_vpc.public_subnets
        self.application_private_subnets = self.application_vpc.private_subnets

        self.database_private_subnets = self.database_vpc.isolated_subnets

        for count, _ in enumerate(self.application_private_subnets):
            _.add_route(id=f"AppPrivateRoute{count}", router_id=self.peering_connection.attr_id,
                        router_type=ec2.RouterType.VPC_PEERING_CONNECTION,
                        destination_cidr_block=self.database_vpc.vpc_cidr_block)

        for count, _ in enumerate(self.database_private_subnets):
            _.add_route(id=f"DBPrivateRoute{count}", router_id=self.peering_connection.attr_id,
                        router_type=ec2.RouterType.VPC_PEERING_CONNECTION,
                        destination_cidr_block=self.application_vpc.vpc_cidr_block)

    @property
    def app_vpc(self) -> ec2.IVpc:
        return self.application_vpc

    @property
    def db_vpc(self) -> ec2.IVpc:
        return self.database_vpc

    @property
    def app_public_subnets(self) -> List[ec2.ISubnet]:
        return self.application_public_subnets

    @property
    def app_public_subnets_ids(self) -> List[str]:
        subnet_ids = [subnet.subnet_id for subnet in self.application_public_subnets]
        return subnet_ids

    @property
    def app_private_subnets(self) -> List[ec2.ISubnet]:
        return self.application_private_subnets

    @property
    def app_private_subnets_ids(self) -> List[str]:
        subnet_ids = [subnet.subnet_id for subnet in self.application_private_subnets]
        return subnet_ids

    @property
    def db_private_subnets(self) -> List[ec2.ISubnet]:
        return self.database_private_subnets

    @property
    def db_private_subnets_ids(self) -> List[str]:
        subnet_ids = [subnet.subnet_id for subnet in self.application_private_subnets]
        return subnet_ids
