from datetime import timedelta, datetime

from cryptography.fernet import Fernet
from django.test import TestCase

from email_agent.models import MailToken
from email_agent.services.email_service import EmailService


def test_create_user_agent():
    """
    Placeholder test function for the email agent.
    This function should contain actual test logic.
    """
    email = "codedbycharan@gmail.com"
    password = "cufotgjdjapdweyv"
    encrypted_key = Fernet.generate_key().decode()
    encrypted_password, key = EmailService().encrypt_password(password=password, key=encrypted_key)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    imap_server = "imap.gmail.com"
    imap_port = 993
    mail_token = MailToken.objects.create(
        user_id=1,
        email=email,
        provider="other_mail",
        meta={
            "others_mail": {
                "smtpserver": smtp_server,
                "smtpserverport": smtp_port,
                "imapserver": imap_server,
                "imapserverport": imap_port,
                "username": email,
                "password": encrypted_password,
                "key": encrypted_key
            }
        }
    )

    print(mail_token.email)


def send_and_pull_email(email):

    mail_token = MailToken.objects.get(user_id=1, email=email)

    email_service = EmailService(mail_token)

    # Send an email
    # success, result = email_service.send_message(
    #     to=["160220d003@gmail.com"],
    #     subject="Test Email",
    #     msg_html="<p>Hello!</p>",
    #     msg_plain="Hello!"
    # )

    # Pull emails
    success, messages = email_service.pull_mail(
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now() + timedelta(days=1)
    )
    assert True, "This is a placeholder test for the email agent."