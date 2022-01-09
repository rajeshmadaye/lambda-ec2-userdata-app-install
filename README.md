# Amazon Lambda function to install softwares on running EC2 instances.
This project contains source code and supporting files for a python based Amazon lambda function to install
any software on EC2 running instances. 

This application will demonstrate way to install "ansible" on all the running EC2 instances. User should specify tag with some defined values (type: ansible) in tag section of EC2 instance. Lambda function can be invoked using cloudwatch event on defined time to loop through all the EC2 instances and update requested software on ec2 instance which tag value has (type : ansible).

## Pre-requsites
- Add tag for EC2 instances where you like to install the software.

## Features
- Lambda function to loop through all the EC2 instances where tag is defined as (type : ansible)
- If EC2 instance is running, then stop it and install ansible and then start it back. 
- userdata section of EC2 will be updated to install required software on next run.
- If EC2 instance is stopped, then just update userdata section and keep it in stopped status.


## Tech
Below are list of technologies used.
- [Python] - Python based lambda function.
- [boto3] - Python boto3 SDK used to interact with AWS services.

Below are list of AWS services used in this project.
- [EC2]     - Boto3 client object used to interact with AWS EC2 instances.
- [Lambda]  - AWS Lambda function created.


## Package installation steps

User should use below command to create this package.
```bash
sam package --region $AWSRegion --profile $ProfileName --s3-bucket $BucketName --template-file $BuiltTemplate --output-template-file deploy.yaml
```

User should use below command to deploy this package.
```bash
sam deploy --region $AWSRegion --profile $ProfileName --s3-bucket $BucketName --template-file $BuiltTemplate --stack-name $StackName --capabilities CAPABILITY_IAM

```


## License
MIT
