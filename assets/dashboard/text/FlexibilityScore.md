# Understanding Flexibility Score

EC2 Flexibility Score Dashboard assesses any configuration used to launch instances through an Autoscaling Group (ASG) against the recommended EC2 best practices. It converts the best practice adoption on the following four components into a “Flexibility Score” that can be used to identify, improve, and monitor the configurations (and subsequently, overall organization level adoption of Spot best practices) which may have room to improve the flexibility by implementing architectural best practices. On a scale of 1 (worse) to 10 (best), the Flexibility score is a weighted average of the four ‘component scores’ seen below.

The higher the score, the more likely a configuration is set up to effectively leverage the latest EC2 features and services.

&nbsp;

## Components of the Flexibility Score

To build this score, we look at how a customer is using different features that indicate the Flexibility posture of a customer at any given point in time. We then compare these features against the set of best practices for each component, and generate a score for each component. Finally, each score is added up through a weight assigned to each component, in order of their importance in improving (or indicating) flexibility of a customer. This gives the Flexibility Score on a scale of 1 (worse) - 10 (good). The higher the score, the better a customer is set up to leverage the best that AWS EC2 offers, including EC2 Spot.