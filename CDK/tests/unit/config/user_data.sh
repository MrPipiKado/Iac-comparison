#!/bin/bash

cd /home/ec2-user
yum update -y
yum install -y git
yum install -y jq
yum install -y mysql

wget https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.rpm
sudo yum -y install ./jdk-17_linux-x64_bin.rpm

sudo wget https://repos.fedorapeople.org/repos/dchen/apache-maven/epel-apache-maven.repo -O /etc/yum.repos.d/epel-apache-maven.repo
sudo sed -i s/\$releasever/6/g /etc/yum.repos.d/epel-apache-maven.repo
sudo yum install -y apache-maven

export JAVA_HOME=/usr/lib/jvm/jdk-17-oracle-x64/
export PATH=$PATH:$JAVA_HOME/bin

my_secret=$(aws secretsmanager get-secret-value --secret-id DevEnv-db-secret --query "SecretString" --output text --region us-east-1)

password=$(echo "$my_secret" | jq -r '.password')
username=$(echo "$my_secret" | jq -r '.username')
host=$(echo "$my_secret" | jq -r '.host')

cd /home/ec2-user

echo "database=mysql" >> /home/ec2-user/mysql.properties
echo "spring.datasource.url=jdbc:mysql://${host}:3306/petclinic" >> /home/ec2-user/mysql.properties
echo "spring.datasource.username=petclinic" >> /home/ec2-user/mysql.properties
echo "spring.datasource.password=petclinic" >> /home/ec2-user/mysql.properties
echo "spring.sql.init.mode=always" >> /home/ec2-user/mysql.properties

git clone https://github.com/spring-projects/spring-petclinic.git
cd spring-petclinic
./mvnw package

echo "CREATE DATABASE IF NOT EXISTS petclinic;" >> /home/ec2-user/init.sql
echo "ALTER DATABASE petclinic" >> /home/ec2-user/init.sql
echo "  DEFAULT CHARACTER SET utf8" >> /home/ec2-user/init.sql
echo "  DEFAULT COLLATE utf8_general_ci;" >> /home/ec2-user/init.sql
echo "CREATE USER IF NOT EXISTS 'petclinic'@'%' IDENTIFIED BY 'petclinic';" >> /home/ec2-user/init.sql
echo "GRANT ALL PRIVILEGES ON petclinic.* TO 'petclinic'@'%';" >> /home/ec2-user/init.sql

mysql -h $host -p$password -u $username < /home/ec2-user/init.sql
mysql -h $host -p$password -u $username petclinic < /home/ec2-user/spring-petclinic/src/main/resources/db/mysql/schema.sql
mysql -h $host -p$password -u $username petclinic < /home/ec2-user/spring-petclinic/src/main/resources/db/mysql/data.sql

nohup java -jar target/*.jar --spring.profiles.active=/home/ec2-user/mysql.properties --spring.config.location=/home/ec2-user/mysql.properties --server.port=80 &