from flask import jsonify

class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self):
        rv = {"error": self.message, "status_code": self.status_code}
        if self.details:
            rv["details"] = self.details
        return rv

class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)

class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify(err.to_dict()), err.status_code

    @app.errorhandler(404)
    def handle_404(err):
        return jsonify({"error": "Endpoint not found", "status_code": 404}), 404

    @app.errorhandler(500)
    def handle_500(err):
        return jsonify({"error": "Internal server error", "status_code": 500}), 500
