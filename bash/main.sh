#!/bin/bash

# Application VPC
OUTPUT_APPLICATION_VPC=$(aws ec2 create-vpc --cidr-block 10.0.0.0/8)
APPLICATION_VPC_ID=$(jq -r '.Vpc.VpcId' <<< ${OUTPUT_APPLICATION_VPC})
echo "Application VPC created"
# Internet Gateway
OUTPUT_INTERNET_GATEWAY=$(aws ec create-internet-gateway)
INTERNET_GATEWAY_ID=$(jq -r '.InternetGateway.InternetGatewayId' <<< ${OUTPUT_INTERNET_GATEWAY})
aws ec attach-internet-gateway --internet-gateway-id $INTERNET_GATEWAY_ID --vpc-id $APPLICATION_VPC_ID
echo "Internet Gateway in Application VPC created and attached"
# Public Route Table
OUTPUT_APP_SUBNET_PUBLIC_RT=$(aws ec2 create-route-table --vpc-id $APPLICATION_VPC_ID)
APP_SUBNET_PUBLIC_RT_ID=$(jq -r '.RouteTable.RouteTableId' <<< ${OUTPUT_APP_SUBNET_PUBLIC_RT})
aws ec2 create-route --destination-cidr-block 0.0.0.0/0 --route-table-id $APP_SUBNET_PUBLIC_RT_ID --gateway-id $INTERNET_GATEWAY_ID
# Public Subnets
OUTPUT_APP_PUBLIC_SUBNET_1=$(aws ec2 create-subnet --availability-zone us-east-1a --cidr-block 10.0.1.0/24 --vpc-id $APPLICATION_VPC_ID)
APP_PUBLIC_SUBNET_1_ID=$(jq -r '.Subnet.SubnetId' <<< ${OUTPUT_PUBLIC_RT_APP_SUBNET_1})
OUTPUT_APP_PUBLIC_SUBNET_2=$(aws ec2 create-subnet --availability-zone us-east-1b --cidr-block 10.0.2.0/24 --vpc-id $APPLICATION_VPC_ID)
APP_PUBLIC_SUBNET_2_ID=$(jq -r '.Subnet.SubnetId' <<< ${OUTPUT_PUBLIC_RT_APP_SUBNET_2})
aws ec2 associate-route-table --route-table-id $APP_SUBNET_PUBLIC_RT_ID --subnet-id $APP_PUBLIC_SUBNET_1_ID
aws ec2 associate-route-table --route-table-id $APP_SUBNET_PUBLIC_RT_ID --subnet-id $APP_PUBLIC_SUBNET_2_ID
# Public Route Table
OUTPUT_APP_SUBNET_PRIVATE_RT=$(aws ec2 create-route-table --vpc-id $APPLICATION_VPC_ID)
APP_SUBNET_PRIVATE_RT_ID=$(jq -r '.RouteTable.RouteTableId' <<< ${OUTPUT_APP_SUBNET_PRIVATE_RT})
echo "Public Subnets and Route Tables in Application VPC created"
# Private Subnets
OUTPUT_APP_PRIVATE_SUBNET_1=$(aws ec2 create-subnet --availability-zone us-east-1a --cidr-block 10.0.3.0/24 --vpc-id $APPLICATION_VPC_ID)
APP_Private_SUBNET_1_ID=$(jq -r '.Subnet.SubnetId' <<< ${OUTPUT_APP_PRIVATE_SUBNET_1})
OUTPUT_APP_PRIVATE_SUBNET_2=$(aws ec2 create-subnet --availability-zone us-east-1b --cidr-block 10.0.4.0/24 --vpc-id $APPLICATION_VPC_ID)
APP_Private_SUBNET_2_ID=$(jq -r '.Subnet.SubnetId' <<< ${OUTPUT_APP_PRIVATE_SUBNET_2})
aws ec2 associate-route-table --route-table-id $APP_SUBNET_PRIVATE_RT_ID --subnet-id $APP_Private_SUBNET_1_ID
aws ec2 associate-route-table --route-table-id $APP_SUBNET_PRIVATE_RT_ID --subnet-id $APP_Private_SUBNET_2_ID
echo "Private Subnets and Route Tables in Application VPC created"


# DB VPC
OUTPUT_DB_VPC=$(aws ec2 create-vpc --cidr-block 192.168.0.0./16)
DB_VPC_ID=$(jq -r '.Vpc.VpcId' <<< ${OUTPUT_DB_VPC})
echo "Private Subnets and Route Tablec in Application VPC created"
# Public Route Table
OUTPUT_DB_SUBNET_PRIVATE_RT=$(aws ec2 create-route-table --vpc-id $DB_VPC_ID)
DB_SUBNET_PRIVATE_RT_ID=$(jq -r '.RouteTable.RouteTableId' <<< ${OUTPUT_DB_SUBNET_PRIVATE_RT})
# Private Subnets
OUTPUT_DB_PRIVATE_SUBNET_1=$(aws ec2 create-subnet --availability-zone us-east-1a --cidr-block 192.168.1.0/24 --vpc-id $DB_VPC_ID)
DB_Private_SUBNET_1_ID=$(jq -r '.Subnet.SubnetId' <<< ${OUTPUT_DB_PRIVATE_SUBNET_1})
OUTPUT_DB_PRIVATE_SUBNET_2=$(aws ec2 create-subnet --availability-zone us-east-1b --cidr-block 192.168.2.0/24 --vpc-id $DB_VPC_ID)
DB_Private_SUBNET_2_ID=$(jq -r '.Subnet.SubnetId' <<< ${OUTPUT_DB_PRIVATE_SUBNET_2})
echo "Private Subnets and Route Tables in Application VPC created"

# VPC Peering
OUTPUT_VPC_PEERING=$(aws ec2 create-vpc-peering-connection --vpc-id $APPLICATION_VPC_ID  --peer-vpc-id $DB_VPC_ID)
VPC_PEERING_ID=$(jq -r '.VpcPeeringConnection.VpcPeeringConnectionId' <<< ${OUTPUT_VPC_PEERING})
aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id $VPC_PEERING_ID 
aws ec2 create-route --route-table-id $DB_SUBNET_PRIVATE_RT_ID --destination-cidr-block 10.0.0.0/8 --vpc-peering-connection-id $VPC_PEERING_ID
aws ec2 create-route --route-table-id $APP_SUBNET_PRIVATE_RT_ID --destination-cidr-block 192.168.0.0/16 --vpc-peering-connection-id $VPC_PEERING_ID
echo "Peering Cnnection between DB and Application VPCs established"