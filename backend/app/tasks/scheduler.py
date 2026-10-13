import logging
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from app.extensions import db
from app.models.reminder import Reminder
from app.models.conversation import Conversation, Message

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def check_and_push_reminders(app):
    """Scan active reminders matching current hour/minute and push into chat."""
    with app.app_context():
        try:
            now_str = datetime.now(timezone.utc).strftime("%H:%M")
            reminders = Reminder.query.filter_by(is_active=True, schedule_time=now_str).all()

            for r in reminders:
                # Find latest conversation or create one
                conv = (
                    Conversation.query.filter_by(user_id=r.user_id)
                    .order_by(Conversation.updated_at.desc())
                    .first()
                )
                if not conv:
                    conv = Conversation(user_id=r.user_id, title="Nutrition Assistant")
                    db.session.add(conv)
                    db.session.commit()

                nudge_text = f"⏰ {r.text}"
                msg = Message(
                    conversation_id=conv.id,
                    role="assistant",
                    content=nudge_text,
                    blocks=[{"type": "text", "content": nudge_text}],
                )
                db.session.add(msg)
                db.session.commit()
                logger.info(f"Pushed reminder to user {r.user_id} into conversation {conv.id}")
        except Exception as e:
            logger.error(f"Error checking reminders: {e}")

def init_scheduler(app):
    if not app.config.get("TESTING"):
        scheduler.add_job(
            func=lambda: check_and_push_reminders(app),
            trigger="interval",
            minutes=1,
            id="calorie_reminders_job",
            replace_existing=True,
        )
        if not scheduler.running:
            scheduler.start()
            logger.info("Background reminder scheduler started.")
