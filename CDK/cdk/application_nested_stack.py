from typing import Dict, List

from aws_cdk import (
    NestedStack,
    aws_ec2 as ec2,
    aws_autoscaling as asg,
    aws_elasticloadbalancingv2 as elbv2
)
from constructs import Construct


class ApplicationLayerStack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, app_vpc: ec2.IVpc, alb_subnets: List[ec2.ISubnet], lb_sg: ec2.ISecurityGroup, app_sg: ec2.ISecurityGroup, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        template = ec2.LaunchTemplate(self, "LaunchTemplate",
                                      instance_type=ec2.InstanceType("t2.micro"),
                                      key_name="DiplomaKey",
                                      launch_template_name="diploma-app",
                                      machine_image=ec2.MachineImage.latest_amazon_linux(),
                                      security_group=app_sg
                                      )
        app_asg = asg.AutoScalingGroup(self, "ASG",
            vpc=app_vpc,
            launch_template=template,
            auto_scaling_group_name="application-asg",
            max_capacity=1,
            min_capacity=1,
            desired_capacity=1,
        )

        alb = elbv2.ApplicationLoadBalancer(self,
                                            'MyAppALB',
                                            vpc=app_vpc,
                                            internet_facing=True,
                                            vpc_subnets=ec2.SubnetSelection(subnets=alb_subnets),
                                            security_group=lb_sg,
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
