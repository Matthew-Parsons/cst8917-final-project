# Part 1 - Method A:
In version-A-durable-functions folder

# Part 2 - Method B:
In version-B-logic-apps folder
### NOTE: I named my queue expense-results by mistake and couldn't change it. Minor error on my part.

# Part 3: Comparison Analysis

## 1. Development Experience

Building the workflow using Azure Durable Functions felt more natural from a software engineering perspective. The code-first approach allowed me to express the entire workflow as a structured program using Python. The orchestrator function clearly defined the control flow (validation → branching → waiting → notification), which made it easy to reason about the logic step-by-step. Debugging was also familiar because I could use logs, breakpoints, and local execution tools.

However, Durable Functions required more initial setup and understanding of orchestration concepts like replay behavior and deterministic execution. For example, I had to be careful not to include non-deterministic operations (like random values or current timestamps) directly in the orchestrator.

In contrast, Azure Logic Apps provided a much faster start. The visual designer made it easy to assemble the workflow by connecting triggers, conditions, and actions. For straightforward logic (such as validation branching or sending emails), this approach was significantly quicker and required less code. The drag-and-drop interface also reduced the likelihood of syntax errors.

That said, as the workflow became more complex (especially around manager approval and timeout handling), the Logic App became harder to manage. The visual representation grew cluttered, and tracking logic across multiple branches was less intuitive than reading code. Debugging also required navigating run histories instead of stepping through execution.

Overall, Logic Apps was faster for initial development, but Durable Functions provided more clarity and confidence for complex workflows.

## 2. Testability

Durable Functions was clearly superior in terms of testability. Because the workflow is written in Python, I could isolate and test activity functions independently using standard unit testing frameworks like pytest. For example, I could directly test validation logic with different inputs and verify outputs without deploying to Azure.

Testing the orchestrator required more care due to its deterministic nature, but it was still possible using mocks and controlled inputs. Additionally, the provided HTTP endpoints made it easy to simulate manager approval scenarios programmatically.

On the other hand, Logic Apps was difficult to test locally. Most testing had to be done after deployment using the Azure portal. While the run history provides detailed execution traces, it is not a substitute for automated testing. There is no straightforward way to write unit tests for Logic App workflows, which made regression testing slower and more manual.

As a result, Durable Functions provided a much stronger and more scalable testing experience, especially for iterative development.

## 3. Error Handling

Durable Functions offered fine-grained control over error handling. I could explicitly define retry policies, exception handling, and fallback logic within the orchestrator and activity functions. For example, I could wrap validation or notification steps in try/catch blocks and implement custom retry behavior using built-in retry options.

Additionally, Durable Functions automatically preserves state, allowing workflows to resume after failures without losing progress. This made the system more resilient and predictable.

Logic Apps also includes built-in retry policies and error handling through configuration. For example, each action can be configured with retry counts and intervals, and failure paths can be defined using “run after” conditions. However, this approach is more declarative and less flexible than writing custom logic in code.

In practice, error handling in Logic Apps felt more rigid. Complex recovery scenarios required additional branches and conditions, which made the workflow harder to read and maintain.

Overall, Durable Functions provided more control and flexibility, while Logic Apps offered simpler but less customizable error handling.

## 4. Human Interaction Pattern

The human interaction requirement (waiting for manager approval) highlighted a major difference between the two approaches. Durable Functions has built-in support for this pattern. Using external events and durable timers, I was able to implement a clean solution:

1.  The orchestrator waits for either a manager response event or a timeout. 
2. A timer triggers escalation if no response is received. 

The logic is expressed clearly in a single place. This approach felt natural and aligned with the workflow requirements.

Logic Apps does not natively support this pattern in the same way. To implement it, I had to design a workaround using Azure Service Bus. The workflow involved:

1. Sending a message to a queue for manager approval. 
2. Waiting for a response via another queue or HTTP endpoint. 
3. Implementing timeout logic using delay actions or separate workflows.

This made the solution more complex and less intuitive. The logic was split across multiple components, making it harder to follow and debug.

Durable Functions was clearly more natural and better suited for long-running, event-driven workflows involving human input.

## 5. Observability

Logic Apps excelled in observability. The Azure portal provides a detailed run history with a visual breakdown of each step, including inputs, outputs, and execution times. This made it very easy to diagnose issues and understand exactly what happened during each workflow execution.

Durable Functions also provides monitoring through Application Insights and logs, but the experience is less visual. To trace execution, I had to rely on logs and correlation IDs, which required more effort to interpret.

However, Durable Functions offers deeper insights for developers who are comfortable with logging and telemetry tools. It is more flexible but less user-friendly compared to Logic Apps.

In summary, Logic Apps was easier for quick diagnostics, while Durable Functions required more effort but offered more detailed control.

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

# Recommendation
If I were building this system for production, I would choose Azure Durable Functions.

The main reason is control. Durable Functions provides a clear, code-driven way to define complex workflows, especially those involving long-running processes and human interaction. The ability to implement the manager approval step using native constructs like external events and durable timers makes the solution both elegant and maintainable. In addition, the strong testability and support for automated testing would be critical for a production system where reliability and regression safety matter.

Durable Functions is also more cost-effective at scale, which becomes important as the number of expense requests grows. The flexibility in error handling and retry logic further strengthens its suitability for real-world scenarios.

That said, I would choose Azure Logic Apps in situations where speed of development and ease of use are the top priorities. For example, if a business team needed a simple workflow quickly with minimal coding, Logic Apps would be ideal. Its visual interface and built-in connectors make it accessible to non-developers and suitable for straightforward automation tasks.

In summary, Durable Functions is better for complex, scalable, and testable systems, while Logic Apps is better for rapid development and simpler integrations.