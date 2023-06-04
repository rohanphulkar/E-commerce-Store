from django.core.mail import send_mail
from django.template.loader import render_to_string
from decouple import config
def sendOrderEmail(context):
    msg_plain = render_to_string('email/email.txt',context)
    msg_html = render_to_string('email/order_placed.html',context)
    send_mail(
        'You order has been placed',
        msg_plain,
        config("EMAIL_USER"),
        [context['email']],
        html_message=msg_html,
        )