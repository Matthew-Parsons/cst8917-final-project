import azure.functions as func
import json

app = func.FunctionApp()

VALID_CATEGORIES = {
    "travel", "meals", "supplies", "equipment", "software", "other"
}

@app.function_name(name="validate_expense")
@app.route(route="validate", methods=["POST"])
def validate_expense(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()

        required_fields = [
            "employee_name",
            "employee_email",
            "amount",
            "category",
            "description",
            "manager_email"
        ]

        missing = [f for f in required_fields if f not in data or data[f] in [None, ""]]

        if missing:
            return func.HttpResponse(
                json.dumps({
                    "valid": False,
                    "reason": f"Missing fields: {', '.join(missing)}"
                }),
                status_code=200,
                mimetype="application/json"
            )

        if data["category"] not in VALID_CATEGORIES:
            return func.HttpResponse(
                json.dumps({
                    "valid": False,
                    "reason": "Invalid category"
                }),
                status_code=200,
                mimetype="application/json"
            )

        return func.HttpResponse(
            json.dumps({
                "valid": True,
                "amount": data["amount"]
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"valid": False, "reason": str(e)}),
            status_code=500,
            mimetype="application/json"
        )