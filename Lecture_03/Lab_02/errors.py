from flask import jsonify, request
from werkzeug.exceptions import HTTPException


class ProblemError(Exception):
    def __init__(
        self,
        status,
        title,
        detail,
        type_uri="about:blank",
        **extra
    ):
        super().__init__(detail)

        self.status = status
        self.title = title
        self.detail = detail
        self.type_uri = type_uri
        self.extra = extra


def register_error_handlers(app):

    # Handle our custom API errors
    @app.errorhandler(ProblemError)
    def handle_problem_error(error):
        body = {
            "type": error.type_uri,
            "title": error.title,
            "status": error.status,
            "detail": error.detail,
            "instance": request.path
        }

        # Optional extra fields
        body.update(error.extra)

        response = jsonify(body)
        response.status_code = error.status
        response.headers["Content-Type"] = "application/problem+json"

        return response


    # Handle normal Flask/Werkzeug HTTP errors:
    # 404, 405, etc.
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        body = {
            "type": "about:blank",
            "title": error.name,
            "status": error.code,
            "detail": error.description,
            "instance": request.path
        }

        response = jsonify(body)
        response.status_code = error.code
        response.headers["Content-Type"] = "application/problem+json"

        return response


    # Handle unexpected server errors
    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):

        # Log detailed error only on server
        app.logger.exception(error)

        body = {
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred.",
            "instance": request.path
        }

        response = jsonify(body)
        response.status_code = 500
        response.headers["Content-Type"] = "application/problem+json"

        return response