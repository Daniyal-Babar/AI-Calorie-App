from datetime import datetime, timezone
from flask import Blueprint, jsonify
from app.extensions import db

health_bp = Blueprint("health", __name__, url_prefix="/api/health")

@health_bp.route("", methods=["GET"])
def health_check():
    db_ok = True
    try:
        db.session.execute(db.text("SELECT 1"))
    except Exception:
        db_ok = False

    return jsonify({
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "architecture": "chat-only-agent",
    }), 200 if db_ok else 503
