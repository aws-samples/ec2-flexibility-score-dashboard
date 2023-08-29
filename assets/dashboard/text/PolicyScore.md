#  Policy Score (15% weight)

This component measures whether a customer is leveraging proactive scaling policies such as Predictive scaling (score of 10), 
or reactive scaling policies such as Target Tracking (score of 6.67), or Simple/Step scaling policies (score of 3.33). 
To capture the score across the whole account, Scaling Policy score is weighted by the vCPU-Hours driven from different scaling policies across different Autoscaling Groups.

&nbsp;

## What are the steps I can take to improve Scaling Policy Score?

1. Consider using [Predictive Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-predictive-scaling.html), which uses Machine Learning to predict capacity requirements based on historical usage from CloudWatch. Check out a [hands-on workshop](https://ec2spotworkshops.com/efficient-and-resilient-ec2-auto-scaling/lab1/10-predictive-scaling.html) to implement predictive scaling.
2. Evaluate if using [Target Tracking Policy](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html) can better serve your scaling needs than Simple/Step Scaling Policies.