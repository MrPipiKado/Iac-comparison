from aws_cdk import NestedStack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from cdk.get_my_ip import MyIP


class SGLayerStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        app_vpc: ec2.IVpc,
        db_vpc: ec2.IVpc,
        env_name: str,
        general_config: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.load_balancer_sg = ec2.SecurityGroup(
            self,
            "LB_SG",
            vpc=app_vpc,
            security_group_name=f"{env_name}-load-balancer-sg",
        )
        self.application_sg = ec2.SecurityGroup(
            self,
            "APP_SG",
            vpc=app_vpc,
            security_group_name=f"{env_name}-application-sg",
        )
        self.database_sg = ec2.SecurityGroup(
            self, "DB_SG", vpc=db_vpc, security_group_name=f"{env_name}-database-sg"
        )

        self.load_balancer_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(80)
        )
        self.load_balancer_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(443)
        )

        self.application_sg.add_ingress_rule(
            peer=self.load_balancer_sg, connection=ec2.Port.tcp(80)
        )

        self.database_sg.add_ingress_rule(
            peer=self.application_sg, connection=ec2.Port.tcp(3306)
        )

        if general_config["BastionHost"]["enabled"]:
            # Create a security group for the bastion host
            self.bastion_host_sg = ec2.SecurityGroup(
                self,
                "BastionSecurityGroup",
                vpc=app_vpc,
                security_group_name=f"{env_name}-bastion-sg",
            )

            if general_config["BastionHost"]["access"] == "my_ip":
                self.bastion_host_sg.add_ingress_rule(
                    ec2.Peer.ipv4(MyIP().get_ip_cidr()), ec2.Port.tcp(22), "SSH access"
                )
            elif general_config["BastionHost"]["access"] == "any":
                self.bastion_host_sg.add_ingress_rule(
                    ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "SSH access"
                )
            else:
                self.bastion_host_sg.add_ingress_rule(
                    ec2.Peer.ipv4(general_config["BastionHost"]["access"]),
                    ec2.Port.tcp(22),
                    "SSH access",
                )

            self.application_sg.add_ingress_rule(
                peer=self.bastion_host_sg, connection=ec2.Port.tcp(22)
            )

    @property
    def lb_sg(self) -> ec2.ISecurityGroup:
        return self.load_balancer_sg

    @property
    def app_sg(self) -> ec2.ISecurityGroup:
        return self.application_sg

    @property
    def db_sg(self) -> ec2.ISecurityGroup:
        return self.database_sg

    @property
    def bastion_sg(self) -> ec2.ISecurityGroup:
        return self.bastion_host_sg
