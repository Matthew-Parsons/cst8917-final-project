import azure.functions as func
import azure.durable_functions as df
from datetime import timedelta
from typing import Any

app = func.FunctionApp()

# ----------------------------
# Activity Functions
# ----------------------------

VALID_CATEGORIES = ["travel", "meals", "supplies", "equipment", "software", "other"]

@app.activity_trigger(input_name="input")
def validate_expense(input: Any) -> Any:
    data = dict(input)

    required_fields = [
        "employee_name", "employee_email",
        "amount", "category", "description", "manager_email"
    ]

    for field in required_fields:
        if field not in data or not data[field]:
            return {"is_valid": False, "error": f"Missing field: {field}"}

    if data["category"] not in VALID_CATEGORIES:
        return {"is_valid": False, "error": "Invalid category"}

    return {"is_valid": True}

@app.activity_trigger(input_name="input")
def send_notification(input: Any):
    data = dict(input)

    print(f"[EMAIL] To: {data.get('email')} | Status: {data.get('status')} | Reason: {data.get('reason', '')}")
# ----------------------------
# Orchestrator Function
# ----------------------------

@app.orchestration_trigger(context_name="context")
def orchestrator_function(context: df.DurableOrchestrationContext):
    request = context.get_input()

    # Step 1: Validation
    validation_result = yield context.call_activity("validate_expense", request)

    if not validation_result["is_valid"]:
        yield context.call_activity("send_notification", {
            "email": request.get("employee_email"),
            "status": "Validation Error",
            "reason": validation_result["error"]
        })
        return "Validation Failed"

    amount = request["amount"]

    # Step 2: Auto-approve
    if amount < 100:
        yield context.call_activity("send_notification", {
            "email": request["employee_email"],
            "status": "Approved",
            "reason": "Auto-approved under $100"
        })
        return "Auto-approved"

    # Step 3: Manager Approval (Human Interaction)
    approval_task = context.wait_for_external_event("ManagerApproval")
    timeout_task = context.create_timer(context.current_utc_datetime + timedelta(seconds=30))

    done = yield context.task_any([approval_task, timeout_task])

    approved = None
    if done == approval_task:
        approved = approval_task.result
        timeout_task.cancel()

    if isinstance(approved, str):
        approved = approved.strip().lower() in ["true", "1", "yes"]

    if approved is True:
        managerResponse = "Approved"
    elif approved is False:
        managerResponse = "Rejected"
    else:
        managerResponse = "Escalated"

    print("FINAL DECISION:", managerResponse)
    print("APPROVED VALUE:", approved)
    print("approved type:", type(approved))
    
    # Step 4: Notification
    print("DECISION MADE:", managerResponse)
    yield context.call_activity("send_notification", {
        "email": request["employee_email"],
        "status": managerResponse
    })

    return managerResponse


# ----------------------------
# Client Function (Start Workflow)
# ----------------------------

@app.route(route="start", methods=["POST"])
@app.durable_client_input(client_name="client")
async def start_workflow(req: func.HttpRequest, client):
    request_data = req.get_json()

    instance_id = await client.start_new(
        "orchestrator_function",
        None,
        request_data
    )

    return client.create_check_status_response(req, instance_id)


# ----------------------------
# Manager Approval Endpoint
# ----------------------------

@app.route(route="manager-response", methods=["POST"])
@app.durable_client_input(client_name="client")
async def manager_response(req: func.HttpRequest, client: df.DurableOrchestrationClient):

    if client is None:
        return func.HttpResponse(
            "Durable client not initialized",
            status_code=500
        )

    instance_id = req.params.get("instanceId")
    raw = req.params.get("approved", "false")
    approved = str(raw).strip().lower() in ["true", "1", "yes"]

    if not instance_id:
        return func.HttpResponse(
            "Missing instanceId",
            status_code=400
        )

    await client.raise_event(
        instance_id,
        "ManagerApproval",
        approved
    )

    return func.HttpResponse(
        f"Manager decision recorded for {instance_id}",
        status_code=200
    )