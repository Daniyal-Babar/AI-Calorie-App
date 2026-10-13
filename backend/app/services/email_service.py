import logging

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_password_reset(to_email: str, reset_token: str) -> bool:
        logger.info(f"[EmailService] Password reset token for {to_email}: {reset_token}")
        return True

    @staticmethod
    def send_notification(to_email: str, subject: str, message: str) -> bool:
        logger.info(f"[EmailService] Notification to {to_email}: [{subject}] {message}")
        return True
