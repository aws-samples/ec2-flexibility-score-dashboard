# Launch Template Score (25% weight)

The recommended best practice is to use Launch Templates (LTs), which allow access to the latest instance types and features of AWS Autoscaling Groups. Launch configurations (LCs) no longer add support for new Amazon EC2 instance types that are released after December 31, 2022. This component score is calculated as the share of vCPU-hours driven from Autoscaling Groups that use Launch Templates. Accounts using Launch Templates for all EC2 usage receive a score of 10.

Launch Template Score = `vCPUHours from LTs / (vCPUHours from LCs + vCPUHours from LTs) * 10`

&nbsp;

## What are the steps I can take to improve Launch Template Score?
1. Use [Launch Templates](https://docs.aws.amazon.com/autoscaling/ec2/userguide/launch-templates.html) to create any new Autoscaling Groups.
2. [Migrate your Launch Configurations to Launch Templates](https://docs.aws.amazon.com/autoscaling/ec2/userguide/migrate-to-launch-templates.html).
3. Follow [this workshop](https://ec2spotworkshops.com/ec2-auto-scaling-with-multiple-instance-types-and-purchase-options.html) to familiarise with general Auto Scaling best practices.