# Part 1 - Method A:
In version-A-durable-functions folder

# Part 2 - Method B:
In version-B-logic-apps folder

# Part 3: Comparison Analysis

## Development Experience: Which was faster to build? Easier to debug? Which gave you more confidence the logic was correct?
In terms of being faster to build, I found method A to be the quick of the two to construct due to not needing to fiddle around with logic app architecture. For debugging and confidence however, I have to go with method B, as the error messages from azure made it very easy to track down what went wrong and where, allowing me to be confident in what was working and what wasn't.

## Testability: Which was easier to test locally? Could you write automated tests for either?
Both were fairly easy to test locally, and automated tests could easily be written for either due to their nature of simply parsing input json data.

## Error Handling: How does each handle failures? Which gives more control over retries and recovery?
Method A handled errors by posting error logs to the console. Method B had the run history tab which showed you the path a given input took, as well as where it failed when applicable. Of the two, method B had far more control with error handling, retries, and recovery compared to method A.

## Human Interaction Pattern: How did each handle "wait for manager approval"? Which was more natural?
Method A handled waiting for manager approval by waiting for a post request from the manager with the key related to the request and their approval decision, whereas method B sent an email to the manager and let them click a button to either approve or deny the request. Method B was far more natural compared to method A due to the ease of use.

## Observability: Which made it easier to monitor runs and diagnose problems?
As mentioned in the development experience section, I have to go with method B, as the error messages from azure made it very easy to track down what went wrong and where, allowing me to be diagnose issues quite easily.

## Cost: Estimate cost at ~100 expenses/day and ~10,000 expenses/day. Use the Azure Pricing Calculator and state your assumptions.

### Scenario 1: ~100 expenses/day (~3,000/month)
Method A: Durable Functions:
- Executions: ~60,000/month
- Cost: $0.20–$1/month

Method B: Logic App and Service Bus
- Logic App
    - 3,000 × 20 actions = 60,000 actions
- Cost:
    - $1–$5/month
- Service Bus
    - $10/month (Standard tier base)
Total:
- $10–$15/month

### Scenario 2: ~10,000 expenses/day (~300,000/month)
Method A: Durable Functions
- Executions: 
    - ~6,000,000/month
- Cost: 
    - $15–$40/month

Method B: Logic App and Service Bus
- Logic App: 
    - 300,000 × 20 = 6 million actions
- Cost: 
    - $150–$300/month
Service Bus
    - $10–$20/month
- Total:
    - $180–$350/month