from flask import Flask, jsonify, request, make_response
from pathlib import Path
import uuid
import yaml


app = Flask(__name__)


# ==========================================================
# In-memory database
# ==========================================================

TASKS = {}


# ==========================================================
# Helper functions
# ==========================================================

def problem(status, title, detail):
    response = jsonify({
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path
    })

    response.status_code = status
    response.headers["Content-Type"] = "application/problem+json"

    return response


def find_task(task_id):
    return TASKS.get(task_id)


# ==========================================================
# GET /v1/tasks
# ==========================================================

@app.get("/v1/tasks")
def list_tasks():

    tasks = list(TASKS.values())

    # status filter
    status = request.args.get("status")

    if status:
        if status not in {"open", "done"}:
            return problem(
                422,
                "Validation error",
                "status must be open or done"
            )

        tasks = [
            task
            for task in tasks
            if task["status"] == status
        ]

    # limit
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return problem(
            422,
            "Validation error",
            "limit must be an integer"
        )

    if limit < 1 or limit > 100:
        return problem(
            422,
            "Validation error",
            "limit must be between 1 and 100"
        )

    tasks = tasks[:limit]

    return jsonify({
        "data": tasks,
        "total": len(tasks)
    }), 200


# ==========================================================
# POST /v1/tasks
# ==========================================================

@app.post("/v1/tasks")
def create_task():

    if not request.is_json:
        return problem(
            415,
            "Unsupported Media Type",
            "Content-Type must be application/json"
        )

    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()

    if not title:
        return problem(
            422,
            "Validation error",
            "title is required"
        )

    status = data.get("status", "open")
    priority = data.get("priority", "normal")

    if status not in {"open", "done"}:
        return problem(
            422,
            "Validation error",
            "status must be open or done"
        )

    if priority not in {"low", "normal", "high"}:
        return problem(
            422,
            "Validation error",
            "priority must be low, normal or high"
        )

    task_id = str(uuid.uuid4())

    task = {
        "id": task_id,
        "title": title,
        "status": status,
        "priority": priority,
        "dueDate": data.get("dueDate"),
        "assigneeId": data.get("assigneeId")
    }

    TASKS[task_id] = task

    response = make_response(jsonify(task), 201)

    response.headers["Location"] = (
        f"/v1/tasks/{task_id}"
    )

    return response


# ==========================================================
# GET /v1/tasks/{taskId}
# ==========================================================

@app.get("/v1/tasks/<task_id>")
def get_task(task_id):

    task = find_task(task_id)

    if task is None:
        return problem(
            404,
            "Task not found",
            f"Task {task_id} does not exist"
        )

    return jsonify(task), 200


# ==========================================================
# PATCH /v1/tasks/{taskId}
# ==========================================================

@app.patch("/v1/tasks/<task_id>")
def patch_task(task_id):

    task = find_task(task_id)

    if task is None:
        return problem(
            404,
            "Task not found",
            f"Task {task_id} does not exist"
        )

    if not request.is_json:
        return problem(
            415,
            "Unsupported Media Type",
            "Content-Type must be application/json"
        )

    data = request.get_json(silent=True) or {}

    if "title" in data:

        title = str(data["title"]).strip()

        if not title:
            return problem(
                422,
                "Validation error",
                "title must not be empty"
            )

        task["title"] = title


    if "status" in data:

        if data["status"] not in {"open", "done"}:
            return problem(
                422,
                "Validation error",
                "status must be open or done"
            )

        task["status"] = data["status"]


    if "priority" in data:

        if data["priority"] not in {
            "low",
            "normal",
            "high"
        }:
            return problem(
                422,
                "Validation error",
                "priority must be low, normal or high"
            )

        task["priority"] = data["priority"]


    if "dueDate" in data:
        task["dueDate"] = data["dueDate"]


    if "assigneeId" in data:
        task["assigneeId"] = data["assigneeId"]


    return jsonify(task), 200


# ==========================================================
# DELETE /v1/tasks/{taskId}
# ==========================================================

@app.delete("/v1/tasks/<task_id>")
def delete_task(task_id):

    if task_id not in TASKS:
        return problem(
            404,
            "Task not found",
            f"Task {task_id} does not exist"
        )

    del TASKS[task_id]

    return "", 204


# ==========================================================
# OpenAPI JSON
# ==========================================================

@app.get("/openapi.json")
def openapi_json():

    yaml_path = Path(__file__).parent / "openapi.yaml"

    with yaml_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        spec = yaml.safe_load(file)

    return jsonify(spec)


# ==========================================================
# Swagger UI
# ==========================================================

@app.get("/docs")
def swagger_docs():

    return """
    <!DOCTYPE html>

    <html>

    <head>

        <title>Tasks API Docs</title>

        <link
            rel="stylesheet"
            href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"
        />

    </head>

    <body>

        <div id="swagger-ui"></div>

        <script
            src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js">
        </script>

        <script>

            SwaggerUIBundle({
                url: "/openapi.json",
                dom_id: "#swagger-ui"
            });

        </script>

    </body>

    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)