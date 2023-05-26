from typing import List

from aws_cdk import NestedStack
from aws_cdk import aws_autoscaling as autoscaling
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from constructs import Construct


class ApplicationLayerStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        app_vpc: ec2.IVpc,
        alb_subnets: List[ec2.ISubnet],
        lb_sg: ec2.ISecurityGroup,
        app_sg: ec2.ISecurityGroup,
        env_name: str,
        config: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.template = ec2.LaunchTemplate(
            self,
            "LaunchTemplate",
            instance_type=ec2.InstanceType(config["app_instance_type"]),
            key_name=config["key_name"],
            launch_template_name=f"{env_name}-app",
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            security_group=app_sg,
        )
        self.app_asg = autoscaling.AutoScalingGroup(
            self,
            "ASG",
            vpc=app_vpc,
            launch_template=self.template,
            auto_scaling_group_name=f"{env_name}-application-asg",
            max_capacity=2,
            min_capacity=1,
            desired_capacity=1,
        )

        self.app_asg.scale_on_cpu_utilization(
            "ScaleASGAction", target_utilization_percent=40, disable_scale_in=False
        )

        self.alb = elbv2.ApplicationLoadBalancer(
            self,
            "MyAppALB",
            load_balancer_name=f"{env_name}-alb",
            vpc=app_vpc,
            internet_facing=True,
            vpc_subnets=ec2.SubnetSelection(subnets=alb_subnets),
            security_group=lb_sg,
        )
        self.target_group = elbv2.ApplicationTargetGroup(
            self,
            "TG",
            vpc=app_vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[self.app_asg],
        )
        # Listener ALB port 443
        # alb_listeners_443 = alb.add_listener(
        #    id="ALBListeners443",
        #    port=443,
        #    default_target_groups=[target_group]
        # )
        # Listener ALB port 80 redirect
        alb_listener_80 = self.alb.add_listener(
            id="ALBListeners80", port=80, default_target_groups=[self.target_group]
        )
