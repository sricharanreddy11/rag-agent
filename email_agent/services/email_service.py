import base64
import logging
from datetime import datetime, timezone, timedelta
import imaplib
import socket
import re
from cryptography.fernet import Fernet
import requests
from django.db import transaction
from imap_tools import MailBox, AND

from typing import List, Dict, Any
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders, utils

from email_agent.models import MailToken, EmailMessage, Thread
from email_agent.utils import format_datetime, convert_timestamp_to_utc

logger = logging.getLogger(__name__)

class EmailService:
    """Service for handling email operations using SMTP/IMAP protocols"""

    def __init__(self, mail_token: MailToken = None):
        self.mail_token = mail_token
        if mail_token:
            self.smtp_settings = mail_token.meta.get('others_mail', {})
            self.imap_settings = mail_token.meta.get('others_mail', {})
            self.user_id = mail_token.user_id

    def send_message(self,
                    to: List[str],
                    subject: str = '',
                    msg_html: str = None,
                    msg_plain: str = None,
                    cc: List[str] = None,
                    bcc: List[str] = None,
                    attachments: List[dict] = None,
                    in_reply_to: str = None) -> tuple[bool, dict]:
        """
        Sends an email message using SMTP.

        Args:
            to: List of recipient email addresses
            subject: Email subject
            msg_html: HTML body content
            msg_plain: Plain text body content
            cc: List of CC recipients
            bcc: List of BCC recipients
            attachments: List of attachment dictionaries with 'filename' and 'data' keys
            in_reply_to: Message-ID of the message being replied to

        Returns:
            tuple: (success: bool, metadata: dict)
        """
        if not self.mail_token:
            return False, {"error": "No mail token provided"}

        try:
            message = MIMEMultipart()
            message['From'] = self.mail_token.email
            message['To'] = ",".join(to)
            message['Subject'] = subject

            if cc:
                message['Cc'] = ",".join(cc)
                to.extend(cc)
            if bcc:
                message['Bcc'] = ",".join(bcc)
                to.extend(bcc)

            # Handle reply
            if in_reply_to:
                message['In-Reply-To'] = in_reply_to
                message['References'] = in_reply_to
                # Get the original message and its thread
                original_message = EmailMessage.objects.filter(
                    message_id=in_reply_to,
                    user_id=self.user_id
                ).first()
                if original_message:
                    thread = original_message.thread
                else:
                    thread = None
            else:
                thread = None

            # Generate unique message ID
            new_message_id = f'<{datetime.now().strftime("%d%m%Y%H%M%s")}-{self.mail_token.email}>'
            message['Message-ID'] = new_message_id

            # Attach body
            if msg_html:
                message.attach(MIMEText(msg_html, 'html'))
            if msg_plain:
                message.attach(MIMEText(msg_plain, 'plain'))

            # Handle attachments
            if attachments:
                for attachment in attachments:
                    filename = attachment.get('filename')
                    data = attachment.get('data')
                    if data:
                        self._attach_base64_attachment(message, filename, data)

            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_settings.get('smtpserver'),
                            int(self.smtp_settings.get('smtpserverport'))) as server:
                server.starttls()
                server.login(self.mail_token.email,
                           self.decrypt_password(self.smtp_settings.get('password'),
                                               self.smtp_settings.get('key')))

                server.send_message(message)

            # Create or update thread
            with transaction.atomic():
                if not thread:
                    # Create new thread
                    thread = Thread.objects.create(
                        thread_id=new_message_id,
                        subject=subject,
                        participants=self._build_participants(to, cc, bcc),
                        sender=self.mail_token.email,
                        thread_owner=self.mail_token.email,
                        is_sent=True,
                        is_inbox=False,
                        last_active_time=datetime.now(timezone.utc),
                        user_id=self.user_id
                    )

                # Store sent message
                EmailMessage.objects.create(
                    message_id=new_message_id,
                    thread=thread,
                    in_reply_to=in_reply_to,
                    sender=self.mail_token.email,
                    recipients=to,
                    cc=cc,
                    bcc=bcc,
                    subject=subject,
                    body_html=msg_html,
                    body_plain=msg_plain,
                    attachments=attachments,
                    received_at=datetime.now(timezone.utc),
                    mail_status="DELIVERED",
                    user_id=self.user_id
                )

                # Update thread
                thread.size = thread.messages.count()
                thread.last_active_time = datetime.now(timezone.utc)
                thread.save()

            return True, {
                "message_id": new_message_id,
                "thread_id": thread.thread_id,
                "sent_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False, {"error": str(e)}

    def pull_mail(self, start_date=None, end_date=None) -> tuple[bool, List[dict]]:
        """
        Pulls emails from the IMAP server and stores them in the database.

        Args:
            start_date: Start date for email range (optional)
            end_date: End date for email range (optional)

        Returns:
            tuple: (success: bool, messages: List[dict])
        """
        if not self.mail_token:
            return False, []

        try:
            with MailBox(self.imap_settings.get('imapserver')).login(
                self.mail_token.email,
                self.decrypt_password(self.imap_settings.get('password'),
                                    self.imap_settings.get('key'))
            ) as mailbox:
                # Build date filter
                date_filter = ""
                if start_date:
                    date_filter += f" SINCE {start_date.strftime('%d-%b-%Y')}"
                if end_date:
                    date_filter += f" BEFORE {(end_date + timedelta(days=1)).strftime('%d-%b-%Y')}"

                # Fetch messages
                messages = []
                for msg in mailbox.fetch(date_filter.strip()):
                    message_data = self.format_message_data(msg)

                    # Process message and store in database
                    success = self._process_message(message_data)
                    if success:
                        messages.append(message_data)

                # Update last sync time
                self.mail_token.last_sync_time = datetime.now(timezone.utc)
                self.mail_token.save()

                return True, messages

        except Exception as e:
            logger.error(f"Error pulling emails: {str(e)}")
            return False, []

    def _process_message(self, message_data: Dict[str, Any]) -> bool:
        """Process a single email message and store it in the database"""
        try:
            with transaction.atomic():
                # Check if message already exists
                if EmailMessage.objects.filter(
                    message_id=message_data['message_id'],
                    user_id=self.user_id
                ).exists():
                    return True

                # Handle reply
                in_reply_to = message_data.get('in_reply_to')
                if in_reply_to:
                    # Find the original message and its thread
                    original_message = EmailMessage.objects.filter(
                        message_id=in_reply_to,
                        user_id=self.user_id
                    ).first()
                    if original_message:
                        thread = original_message.thread
                    else:
                        # Create new thread if original message not found
                        thread = self._create_thread(message_data)
                else:
                    # Create new thread for non-reply messages
                    thread = self._create_thread(message_data)

                # Create message
                EmailMessage.objects.create(
                    message_id=message_data['message_id'],
                    thread=thread,
                    in_reply_to=in_reply_to,
                    sender=message_data['sender'],
                    recipients=message_data['recipients'],
                    cc=message_data.get('cc'),
                    bcc=message_data.get('bcc'),
                    subject=message_data['subject'],
                    body_html=message_data['body_html'],
                    body_plain=message_data.get('body_plain'),
                    attachments=message_data.get('attachments'),
                    received_at=message_data['received_at'],
                    mail_status="RECEIVED",
                    user_id=self.user_id
                )

                # Update thread
                thread.size = thread.messages.count()
                thread.last_active_time = message_data['received_at']
                thread.save()

                return True

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return False

    def _create_thread(self, message_data: Dict[str, Any]) -> Thread:
        """Create a new thread for a message"""
        return Thread.objects.create(
            thread_id=message_data['message_id'],
            subject=message_data['subject'],
            participants=self._build_participants(
                message_data['recipients'],
                message_data.get('cc', []),
                message_data.get('bcc', [])
            ),
            sender=message_data['sender'],
            thread_owner=self.mail_token.email,
            is_sent=message_data['sender'] == self.mail_token.email,
            is_inbox=message_data['sender'] != self.mail_token.email,
            last_active_time=message_data['received_at'],
            user_id=self.user_id
        )

    def _build_participants(self, to: List[str], cc: List[str] = None, bcc: List[str] = None) -> dict:
        """Build a dictionary of all participants in a thread"""
        participants = {
            'to': list(set(to)),
            'cc': list(set(cc or [])),
            'bcc': list(set(bcc or []))
        }
        return participants

    def format_message_data(self, mail_message) -> dict:
        """Formats raw email message into a structured dictionary"""
        return {
            'message_id': mail_message.uid,
            'in_reply_to': mail_message.obj.get('In-Reply-To', ''),
            'sender': mail_message.from_,
            'recipients': mail_message.to,
            'cc': mail_message.cc,
            'bcc': mail_message.bcc,
            'subject': mail_message.subject,
            'body_html': mail_message.html,
            'body_plain': mail_message.text,
            'attachments': [
                {
                    'filename': att.filename,
                    'content_type': att.content_type,
                    'size': att.size,
                    'data': att.payload,
                    'is_inline': att.content_disposition == 'inline'
                }
                for att in mail_message.attachments
            ],
            'received_at': mail_message.date
        }

    def _attach_base64_attachment(self, msg, filename, base64_data):
        """Attaches a base64 encoded file to the email message"""
        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(base64.b64decode(base64_data))
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)
        except Exception as e:
            logger.error(f"Error attaching file {filename}: {str(e)}")

    def encrypt_password(self, password: str, key: str) -> tuple[str, str]:
        """Encrypts the email password using Fernet encryption"""
        f = Fernet(key)
        encrypted_password = f.encrypt(password.encode()).decode()
        return encrypted_password, key

    def decrypt_password(self, encrypted_password: str, key: str) -> str:
        """Decrypts the email password"""
        f = Fernet(key)
        return f.decrypt(encrypted_password.encode()).decode()

    def generate_key(self) -> str:
        """Generates a new Fernet encryption key"""
        return Fernet.generate_key().decode()

    def extract_emails_from_str(self, mail):
        """Extracts emails from given string using regex pattern"""
        if mail:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, mail)
            return emails
        return []

    @staticmethod
    def verify_imap_server(imap_server, username, password):
        """Verifies if the IMAP server connection is valid"""
        try:
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(username, password)
            mailbox_status, _ = mail.select('inbox')
            if mailbox_status == 'OK':
                mail.close()
                mail.logout()
                return True
            return False
        except:
            return False

    def verify_host_and_port(self, host, port):
        """Verifies if a given host and port are accessible"""
        try:
            ip_address = socket.gethostbyname(host)
            with socket.create_connection((ip_address, port), timeout=15):
                return True
        except (socket.timeout, ConnectionRefusedError):
            return False
        except Exception as e:
            return False




