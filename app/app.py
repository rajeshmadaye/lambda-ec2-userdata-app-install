#************************************************************************
## Lambda Function  : EC2 Instance Ansible Installation
## Description      : Lambda Function install base commands on EC2 instance
## Author           :
## Copyright        : Copyright 2021
## Version          : 1.0.0
## Mmaintainer      :
## Email            :
## Status           : Development first draft done.
##************************************************************************
## Version Info:
## 1.0.0 : 30-Oct-2021 : Created first version to auto install apps on ec2
##************************************************************************
import sys, os, json, time
import base64
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import traceback

##************************************************************************
## Global Default Parameters :: User should modify default values.
##************************************************************************
DEF_APP_REGION_NAME          = 'us-east-1'  # region name to process instances.
WAIT_INTERVAL                = 5    # 05 seconds wait interval after sending stop request
##***********************************************************************
## Class Definition
##***********************************************************************
class InstallEC2Apps:
  #************************************************************************
  # Class constructor
  #************************************************************************
  def __init__(self):
    rc = True
    self.region         = self.get_env_value('APP_REGION_NAME', DEF_APP_REGION_NAME)
    self.ec2client      = boto3.client('ec2', region_name=self.region)
    return

  #************************************************************************
  # Setup environment parameters if exists
  #************************************************************************
  def get_env_value(self, key, default):
    value = os.environ[key] if key in os.environ else default
    return value

  #************************************************************************
  # Function to run main logic
  #************************************************************************
  def run(self):
    rc = False
    response = self.ec2client.describe_instances(Filters=self.get_filler())
    instances_to_stop = []
    instances_to_start = []
    for instances in response['Reservations']:
      for instance in instances['Instances']:
        print("INST Found:", instance['InstanceId'])
        if instance['State']['Name'] == 'running':
          instances_to_stop.append(instance['InstanceId'])
        instances_to_start.append(instance['InstanceId'])

        if(len(instances_to_stop)):
          self.stop_ec2_instance(instances_to_stop)

        if(len(instances_to_start)):
          self.add_user_data(instances_to_start)

        if(len(instances_to_start)):
          self.start_ec2_instance(instances_to_start)

    return rc

  #************************************************************************
  # Get filler data
  #************************************************************************
  def get_filler(self):
    filter = [{ 'Name' : 'tag:type', 'Values' : ['ansible'] }]
    return filter


  #************************************************************************
  # Start EC2 instance
  #************************************************************************
  def start_ec2_instance(self, instances_to_start):
    rc = False
    try:
      print("Attempt to start EC2 instance")
      self.ec2client.start_instances(InstanceIds=instances_to_start)
      print("EC2 instances started successfully")
      rc = True
    except ClientError as e:
      print("Unable to perform start operation")
      rc = False

    if rc:
      rc = self.ec2_state_change_wait(instances_to_start, 'running')
      if rc:
        print("EC2 instances started successfully")

    return rc

  #************************************************************************
  # Stop EC2 instance
  #************************************************************************
  def stop_ec2_instance(self, instances_to_stop):
    rc = False

    try:
      print("Attempt to stop EC2 instance")
      self.ec2client.stop_instances(InstanceIds=instances_to_stop)
      rc = True
    except ClientError as e:
      print("Unable to perform stop operation on EC2 instances :")
      rc = False

    if rc:
      rc = self.ec2_state_change_wait(instances_to_stop, 'stopped')
      if rc:
        print("EC2 instances stopped successfully")

    return rc

  def ec2_state_change_wait(self, instance_list, state):
    #Block program untill all resource stopped successfully.
    rc = False
    wait = True
    while wait:
      wait = False
      response = self.ec2client.describe_instances(InstanceIds=instance_list)
      for instances in response['Reservations']:
        for instance in instances['Instances']:
          if instance['State']['Name'] != state:
            print("Waiting for {} action on instance {}".format(state, instance['InstanceId']))
            time.sleep(WAIT_INTERVAL)
            wait = True
    if not wait:
      rc = True
    return rc

  #************************************************************************
  # Add user data
  #************************************************************************
  def add_user_data(self, instances_to_start):
    rc = False

    for instance in instances_to_start:
      try:
        print("Add user data to instance :", instance)
        user_data = self.get_user_data(instance)
        print("User Data:", user_data)
        response = self.ec2client.modify_instance_attribute(
          InstanceId=instance,
          UserData={
            'Value': user_data
          }
        )
        print("User data added on instance {} successfully".format(instance))
      except ClientError as e:
        print("Unable to perform add user data operation on instance:", instance)
        traceback.print_exc()
        rc = False
    return rc

  #************************************************************************
  # Get cloud-init data
  #************************************************************************
  def get_user_data(self, instance):
    user_data = '''
#!/bin/bash
sudo rm -Rf /var/lib/cloud/instances/{}/sem
yum install -y git
sudo amazon-linux-extras install -y epel
sudo amazon-linux-extras install -y ansible2
'''.format(instance)
    return user_data

#************************************************************************
# main lambda handler
#************************************************************************
def lambda_handler(event, context):
  rc = False
  print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
  print("INFO :: Lambda function executon initiated")
  try:
    IEC = InstallEC2Apps()
    rc = IEC.run()
    rc = True
  except Exception as inst:
    print("Error:: Unable to process request:", inst)
    traceback.print_exc()

  print("Lambda Execution Status :", rc)
  print("INFO :: Lambda function executon completed")
  print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

  return rc

if __name__ == "__main__":
    lambda_handler('','')
