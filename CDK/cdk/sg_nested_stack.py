from typing import Dict, List

from aws_cdk import (
    NestedStack,
    aws_ec2 as ec2
)
from constructs import Construct


class SGLayerStack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, app_vpc: ec2.IVpc, db_vpc: ec2.IVpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.load_balancer_sg = ec2.SecurityGroup(self, "LB_SG",
                                       vpc=app_vpc,
                                        security_group_name="load-balancer-sg"
                                       )
        self.application_sg = ec2.SecurityGroup(self, "APP_SG",
                                                  vpc=app_vpc,
                                                security_group_name="application-sg"
                                                  )
        self.database_sg = ec2.SecurityGroup(self, "DB_SG",
                                                  vpc=db_vpc,
                                             security_group_name="database-sg"
                                                  )

        self.load_balancer_sg.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(80))
        self.load_balancer_sg.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(443))

        self.application_sg.add_ingress_rule(peer=self.load_balancer_sg, connection=ec2.Port.tcp(80))

        self.database_sg.add_ingress_rule(peer=self.application_sg, connection=ec2.Port.tcp(1443))

    @property
    def lb_sg(self) -> ec2.ISecurityGroup:
        return self.load_balancer_sg

    @property
    def app_sg(self) -> ec2.ISecurityGroup:
        return self.application_sg

    @property
    def db_sg(self) -> ec2.ISecurityGroup:
        return self.database_sg
