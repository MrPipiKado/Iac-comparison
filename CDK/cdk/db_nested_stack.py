from aws_cdk import Duration, NestedStack, RemovalPolicy
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_cloudwatch_actions as cw_actions
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subscriptions
from constructs import Construct

db_engine_maping = {
    "MYSQL": rds.DatabaseInstanceEngine.MYSQL,
    "POSTGRES": rds.DatabaseInstanceEngine.POSTGRES,
    "SQL_SERVER_SE": rds.DatabaseInstanceEngine.SQL_SERVER_SE,
}


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
            engine=db_engine_maping[config["db_engine"]],
            port=int(config["db_port"]),
            instance_type=ec2.InstanceType(config["db_instance_type"]),
            vpc=db_vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=db_subnets),
            security_groups=[db_sg],
            deletion_protection=False,
            allocated_storage=config["storage"],
            max_allocated_storage=100,
            storage_type=rds.StorageType.GP2,
            backup_retention=Duration.days(7),
            removal_policy=RemovalPolicy.DESTROY,
            credentials=rds.Credentials.from_generated_secret(
                "mysql_admin", secret_name=f"{env_name}-db-secret"
            ),
        )

        # Create an SNS topic for notifications
        self.sns_topic = sns.Topic(self, "RdsAlertTopic")

        # Create a CloudWatch alarm for storage usage
        self.alarm = cloudwatch.Alarm(
            self,
            "RdsStorageAlarm",
            metric=self.db_instance.metric_free_storage_space(),
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_OR_EQUAL_TO_THRESHOLD,
            threshold=config["alert_on_storage_percentage"] / 10 * config["storage"],
            evaluation_periods=1,
            alarm_name="RDS Storage Alarm",
            alarm_description="The RDS storage is 70% full or above",
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
            actions_enabled=True,
        )

        self.alarm.add_alarm_action(cw_actions.SnsAction(self.sns_topic))

        # Add a subscription to the SNS topic to receive notifications
        self.sns_topic.add_subscription(
            subscriptions.EmailSubscription(config["notification_email"])
        )
