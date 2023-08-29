# Instance Diversification Score (25% weight)

The flexibility to leverage several different instance types improves the likelihood of acquiring the desired EC2 capacity, particularly for EC2 Spot instances where instance diversification helps to replace Spot instances which may receive an instance termination notification. This component score provides insight into whether Autoscaling configurations are set-up to leverage a diverse set of instance types. Being flexible across several different instance types, including families, generations, sizes, Availability Zones, and AWS regions - increases the likelihood of accessing the desired compute capacity, as well as helps to effectively replace EC2 Spot interruption events.

Note: Launch configuration based ASGs receive a default score of 2. For Launch Templates, the score is calculated as below:

&nbsp;

Amount of configured Instance types | Score
----|----- 
> 15 or [Attribute-based Instance type selection](https://docs.aws.amazon.com/autoscaling/ec2/userguide/create-asg-instance-type-requirements.html) | 10
11-15 | 8
6-10 | 6
2-5 | 4
1 | 2

&nbsp;

## What are the steps I can take to improve Instance Diversification Score?

1. Use Attribute Based Instance Selection (ABIS) to automate qualification and use of all possible instance types your workload can use. ABS can only be used with Launch Templates (see Launch Template Score section)
2. Use [EC2 Instance Selector](https://ec2spotworkshops.com/using_ec2_spot_instances_with_eks/040_eksmanagednodegroupswithspot/selecting_instance_types.html) to understand the various instance type options that can work for your requirements.
3. Check [EC2 Spot Best Practices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-best-practices.html#be-instance-type-flexible): ensure that all Availability Zones are configured for use in your VPC and selected for your workload.
4. Use Karpenter to provision and scale capacity. If you are using node groups and cluster autoscaler with EKS, Karpenter can help improve instance diversification by launching right-sized compute resources in response to changing application load, thereby reducing waste as well as ensuring access to capacity across all eligible instance types. It is an open-source, highly performant cluster autoscaler for Kubernetes.
5. Use [Spot Placement Score](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-placement-score.html) which indicates how it is that a Spot Request will succeed in an AWS region or an Availability Zone. The open source project [EC2 Spot Placement Score Tracker](https://github.com/aws-samples/ec2-spot-placement-score-tracker) offers the ability to track SPS over time for different configurations.
