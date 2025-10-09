from django.db import models
from django.conf import settings
from orders.models import Order

class Payment(models.Model):
    PAYMENT_METHOD = (('qr', 'QR'), ('credit', 'CreditCard'), ('wallet','Wallet'))
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    provider_payment_id = models.CharField(max_length=200, blank=True, null=True)  # transaction id from gateway
    created_at = models.DateTimeField(auto_now_add=True)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

