from aws_cdk import NestedStack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from constructs import Construct


class BastionLayerStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        app_vpc: ec2.IVpc,
        alb_subnets: ec2.ISubnet,
        bastion_sg: ec2.ISecurityGroup,
        config: dict,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.bastion_role = iam.Role(
            self,
            "BastionRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMManagedInstanceCore"
                )
            ],
        )

        self.bastion_instance = ec2.Instance(
            self,
            "BastionInstance",
            vpc=app_vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=alb_subnets),
            instance_type=ec2.InstanceType(instance_type_identifier="t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            security_group=bastion_sg,
            role=self.bastion_role,
            key_name=config["key_name"],
        )
