from django.db import models
from django.conf import settings

class ContractWork(models.Model):
    STATUS_CHOICES = (
        ('requested','Requested'),
        ('pending','Pending'),
        ('accepted','Accepted'),
        ('rejected','Rejected'),
        ('completed','Completed'),
    )
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requested_contracts')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_contracts')
    title = models.CharField(max_length=200)
    details = models.TextField()
    wages = models.DecimalField(max_digits=12, decimal_places=2)
    deadline = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='requested')
    created_at = models.DateTimeField(auto_now_add=True)

class ContractMessage(models.Model):
    contract = models.ForeignKey(ContractWork, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
