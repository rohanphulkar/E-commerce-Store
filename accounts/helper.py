from django.core.mail import send_mail
from django.conf import settings

def send_password_reset_email(url,email):
    subject = "Password reset request"
    body = f"You can reset your password by clicking the link below.\n\n{url}"
    try:
        send_mail(subject,body,settings.EMAIL_HOST_USER,[email])
        return True
    except:
        return False