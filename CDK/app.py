#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.cdk_stack import CdkStack
from cdk.config_reader import ConfigReader

configs = ConfigReader("./config")
app = cdk.App()
for env in configs.config_names:
    CdkStack(app, env, configs.configs_with_names[env])
    cdk.Tags.of(app).add("Env", env)

app.synth()
