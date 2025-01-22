from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Part

@receiver(post_save, sender=Part)
def notify_low_stock(sender, instance, **kwargs):
    if instance.is_low_stock():
        subject = 'Low Stock Alert'
        message = 'The stock for {instance.name} is low ({instance.stock} left).'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ['admin@example.com']  # Replace with admin email
        send_mail(subject, message, email_from, recipient_list)
