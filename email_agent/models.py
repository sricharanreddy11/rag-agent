from django.db import models
from django.utils import timezone

from authenticator.user_manager import UserAbstractModel


class MailToken(UserAbstractModel):
    """Model to store email account tokens and credentials"""
    email = models.EmailField(unique=True)
    provider = models.CharField(max_length=50)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True)
    meta = models.JSONField(default=dict)
    token_type = models.CharField(max_length=50, default="EMAIL")
    status = models.CharField(max_length=20, default="ACTIVE")
    is_primary = models.BooleanField(default=False)
    last_sync_time = models.DateTimeField(null=True)
    last_connected_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mail_token'


class Thread(UserAbstractModel):
    """Model to store email conversation threads"""
    thread_id = models.CharField(max_length=255, unique=True)
    subject = models.TextField()
    participants = models.JSONField(default=dict)  # Store all participants in the thread
    sender = models.EmailField()
    thread_owner = models.EmailField()  # The email account that owns this thread
    is_sent = models.BooleanField(default=False)  # Whether this is a sent thread
    is_inbox = models.BooleanField(default=False)  # Whether this is an inbox thread
    last_active_time = models.DateTimeField()
    size = models.IntegerField(default=0)  # Number of messages in thread
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'email_thread'


class EmailMessage(UserAbstractModel):
    """Model to store email messages"""
    message_id = models.CharField(max_length=255, unique=True)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    in_reply_to = models.CharField(max_length=255, null=True, blank=True)  # Message-ID of the message being replied to
    sender = models.EmailField()
    recipients = models.JSONField()
    cc = models.JSONField(null=True, blank=True)
    bcc = models.JSONField(null=True, blank=True)
    subject = models.TextField()
    body_html = models.TextField()
    body_plain = models.TextField(null=True, blank=True)
    attachments = models.JSONField(null=True, blank=True)
    received_at = models.DateTimeField()
    mail_status = models.CharField(max_length=20, default="RECEIVED")  # RECEIVED, DELIVERED, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'email_message'
