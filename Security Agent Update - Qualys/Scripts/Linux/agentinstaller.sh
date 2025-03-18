#!/bin/bash

export CUSTOMERID="XXXXXX"
export ACTIVATIONID="YYYY"

install_awscli(){
    local arch=$1
    if [ $arch == 'aarch64' ]
    then
        awspack='awscli-exe-linux-aarch64.zip'
    else
        awspack='awscli-exe-linux-x86_64.zip'
    fi
    mkdir -p /tmp/agents
    cd /tmp/agents
    sudo curl "https://awscli.amazonaws.com/$awspack" -o "/tmp/agents/awscliv2.zip"
    sudo unzip awscliv2.zip
    sudo ./aws/install
    /usr/local/bin/aws --version
}

install_amaz_rhel(){
    local arch=$1
    if [ $arch == 'aarch64' ]
    then
        folder='arm64'
    else
        folder='86_64'
    fi
    
    #/usr/local/bin/aws s3 cp s3://qualys-agents-installer/StateRAMP/Linux/RHEL_AmazonLinux/$folder/QualysCloudAgent.rpm /tmp/agents/QualysCloudAgent.rpm
    sudo rpm -ivh /tmp/agents/RHEL_AmazonLinux/$folder/QualysCloudAgent.rpm
    sudo /usr/local/qualys/cloud-agent/bin/qualys-cloud-agent.sh ActivationId=$ACTIVATIONID CustomerId=$CUSTOMERID ServerUri=https://qagpublic.qg2.apps.qualys.com/CloudAgent/
    echo "successful"
    rm -rf /tmp/agents/*
    sudo systemctl status qualys-cloud-agent
    if [ $? == 0 ]
    then
        touch /tmp/qualys.txt
    fi
}


install_ubuntu(){
    local arch=$1
    if [ $arch == 'aarch64' ]
    then
        folder='arm64'
        awspack='awscli-exe-linux-aarch64.zip'
    else
        folder='86_64'
        awspack='awscli-exe-linux-x86_64.zip'
    fi
    
    cd /tmp/agents
    #/usr/local/bin/aws s3 cp s3://qualys-agents-installer/StateRAMP/Linux/Ubuntu/$folder/QualysCloudAgent.deb /tmp/agents/QualysCloudAgent.deb
    sudo dpkg --install /tmp/agents/Ubuntu/$folder/QualysCloudAgent.deb
    sudo /usr/local/qualys/cloud-agent/bin/qualys-cloud-agent.sh ActivationId=$ACTIVATIONID CustomerId=$CUSTOMERID ServerUri=https://qagpublic.qg2.apps.qualys.com/CloudAgent/
    echo "successful"
    rm -rf /tmp/agents/*
    sudo systemctl status qualys-cloud-agent
    if [ $? == 0 ]
    then
        touch /tmp/qualys.txt
    fi
}


if [ -f /tmp/qualys.txt ]
then
    echo "Qualys is already installed. Hence exiting the"
    exit 0
else
    echo "Qualys is not installed. Hence Continue"
fi

if [ -f /etc/os-release ]
then
    ostype=`cat /etc/os-release |grep -w ID |awk -F "=" '{print $2}'`
    arch=`uname -m`
    if [ $ostype == "ubuntu" ]
    then
        echo "It is a Ubuntu machine"
        sudo apt update
        sudo apt install unzip -y
        #install_awscli $arch
        install_ubuntu $arch
    elif [ $ostype == '"amzn"' ]
    then
        #sudo yum update -y
        sudo yum install unzip -y
        echo "It is a Amzon machine"
        #install_awscli $arch
        install_amaz_rhel $arch
    elif [ $ostype == '"rhel"' ]
    then
        #sudo yum update -y
        sudo yum install unzip -y
        echo "It is a RHEL machine"
        #install_awscli $arch
        install_amaz_rhel $arch
    elif [ $ostype == '"centos"' ]
    then
        echo "It is a centos machine"
        #sudo yum update -y
        sudo yum install unzip -y
        #sudo yum install awscli
        #install_awscli $arch
        install_amaz_rhel $arch
    fi
fi