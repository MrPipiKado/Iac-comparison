from typing import Dict, List

from aws_cdk import (
    NestedStack,
    aws_ec2 as ec2,
    aws_autoscaling as asg,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as elb_targets
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
                                            security_group=lb_sg
                                            )
        target_group = elbv2.ApplicationTargetGroup(
            self, "TG",
            vpc=app_vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[app_asg]
        )
        # Listener ALB port 443
        #alb_listeners_443 = alb.add_listener(
        #    id="ALBListeners443",
        #    port=443,
        #    default_target_groups=[target_group]
        #)
        # Listener ALB port 80 redirect
        alb_listener_80 = alb.add_listener(
            id="ALBListeners80",
            port=80,
            default_target_groups=[target_group]
        )
