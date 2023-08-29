# Scaling Score (35% weight)

Scaling Score measures the elasticity of the current usage patterns, captured at the level of a specific AWS Account ID. 
It’s calculated as the ratio of Max Running Instances (Peak) to the Minimum running instances (Trough) on any day. The ratio translates to a score as shown below, on a scale of 1-10.

	Ratio >1.07 (i.e. Peak instances used concurrently were 7% higher than the Trough) = Score of 10
    Ratio 1.05 - 1.07 = Score of 7.5
    Ratio 1.02 - 1.05 = Score of 5
    Ratio <1.02 = Score of 2.5

&nbsp;

## I have a low scaling score. What does it mean?
Low scaling score means that the usage in the specific account doesn't scale up or down too much over time, which could be an indicator of over-provisioning. 
While this is workload dependent, as some workloads may need the ability to scale more than others, it is worth evaluating if there is room for efficiency by using a more dynamic scaling approach. 
This could lead to greater cost savings and reducing waste of compute resources.

&nbsp;

## What are the steps I can take to improve scaling score?
1. Understand the different [scaling options](https://docs.aws.amazon.com/autoscaling/ec2/userguide/scale-your-group.html) you can use with Autoscaling Groups.
2. Adopt [Karpenter](https://aws.amazon.com/blogs/aws/introducing-karpenter-an-open-source-high-performance-kubernetes-cluster-autoscaler/). If you are using Managed Node Groups with EKS, Karpenter can help you improve your application availability and cluster efficiency by rapidly launching right-sized compute resources in response to changing application load, thus reducing waste. It is an open-source, highly performant cluster autoscaler for Kubernetes.
3. Set up [AWS Compute Optimizer](https://aws.amazon.com/compute-optimizer/) (free to use), which can help you right-size over-provisioned / under-utilized instances.