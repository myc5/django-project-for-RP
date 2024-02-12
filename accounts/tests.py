from django.test import TestCase

from django.core.mail import EmailMessage, mail_managers
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .variables import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

class EmailTestCase(TestCase):
    
    def setUp(self):
        settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
        settings.EMAIL_HOST = "sandbox.smtp.mailtrap.io"
        settings.EMAIL_HOST_USER =EMAIL_HOST_USER
        settings.EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
        settings.EMAIL_PORT = "2525"
        
    def test_send_mail(self):
        subject = "Subject"
        html_message = render_to_string("mail_template.html", {"context": "values"})
        plain_message = strip_tags(html_message)
        from_email = "from@yourdjangoapp.com"
        to = "mehmet.yilmaz@rapidproto.de"
        
        message = EmailMessage(subject=subject, body=plain_message, from_email=from_email, to=(to,))
        with open("Attachment.txt") as file:
            message.attach("Attachment.txt", file.read(), "file/txt")
            
        message.send()