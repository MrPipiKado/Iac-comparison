from aws_cdk import Duration, NestedStack, RemovalPolicy
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from constructs import Construct


class DBLayerStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        db_sg: ec2.ISecurityGroup,
        db_vpc: ec2.IVpc,
        db_subnets: ec2.ISubnet,
        env_name: str,
        config: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.db_instance = rds.DatabaseInstance(
            self,
            "MyRdsInstance",
            instance_identifier=f"{env_name}-db",
            engine=rds.DatabaseInstanceEngine.MYSQL,
            instance_type=ec2.InstanceType(config["db_instance_type"]),
            vpc=db_vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=db_subnets),
            security_groups=[db_sg],
            deletion_protection=False,
            allocated_storage=20,
            max_allocated_storage=100,
            storage_type=rds.StorageType.GP2,
            backup_retention=Duration.days(7),
            removal_policy=RemovalPolicy.DESTROY,
            credentials=rds.Credentials.from_generated_secret(
                "mysql_admin", secret_name=f"{env_name}-db-secret"
            ),
        )
