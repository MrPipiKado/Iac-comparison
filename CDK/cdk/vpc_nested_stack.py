from typing import Dict, List

from aws_cdk import (
    NestedStack,
    aws_ec2 as ec2
)
from constructs import Construct


class NetworkLayerStack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.application_vpc = ec2.Vpc(
            scope=self,
            id="ApplicationVPC",
            cidr="10.0.0.0/16",
            enable_dns_hostnames=True,
            enable_dns_support=True
        )
        self.internet_gateway = ec2.CfnInternetGateway(self, "InternetGateway")

        self.database_vpc = ec2.Vpc(
            scope=self,
            id="DatabaseVPC",
            cidr="192.168.0.0/16",
            enable_dns_hostnames=True,
            enable_dns_support=True
        )
        self.peering_connection = ec2.CfnVPCPeeringConnection(self, "VPCPeeringConnection",
                                                              peer_vpc_id=self.application_vpc.vpc_id,
                                                              vpc_id=self.database_vpc.vpc_id,
                                                              )

        self.application_public_subnets = [ec2.Subnet(self, f"AppPublicSubnet{_}",
                                                            availability_zone=self.availability_zones[_],
                                                            cidr_block=f"10.0.{_}.0/24",
                                                            vpc_id=self.application_vpc.vpc_id
                                                            ) for _ in range(2)]
        self.application_private_subnets = [ec2.Subnet(self, f"AppPrivateSubnet{_}",
                                                             availability_zone=self.availability_zones[_],
                                                             cidr_block=f"10.0.{_ + 2}.0/24",
                                                             vpc_id=self.application_vpc.vpc_id
                                                             ) for _ in range(2)]

        self.database_private_subnets = [ec2.Subnet(self, f"DBPrivateSubnet{_}",
                                                          availability_zone=self.availability_zones[_],
                                                          cidr_block=f"192.168.{_}.0/24",
                                                          vpc_id=self.application_vpc.vpc_id
                                                          ) for _ in range(2)]
        for _ in self.application_public_subnets:
            _.add_default_internet_route(self.internet_gateway.attr_internet_gateway_id, self.internet_gateway)

        for count, _ in enumerate(self.application_private_subnets):
            _.add_route(id=f"AppPrivateRoute{count}", router_id=self.peering_connection.attr_id,
                        router_type=ec2.RouterType.VPC_PEERING_CONNECTION, destination_cidr_block=self.database_vpc.vpc_id)

        for count, _ in enumerate(self.database_private_subnets):
            _.add_route(id=f"DBPrivateRoute{count}", router_id=self.peering_connection.attr_id,
                        router_type=ec2.RouterType.VPC_PEERING_CONNECTION, destination_cidr_block=self.application_vpc.vpc_id)

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
    def app_private_subnets(self) -> List[ec2.ISubnet]:
        return self.application_private_subnets

    @property
    def db_private_subnets(self) -> List[ec2.ISubnet]:
        return self.db_private_subnets

