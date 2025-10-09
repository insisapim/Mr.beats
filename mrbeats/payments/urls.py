from django.urls import path
from . import views

urlpatterns = [
        path('success/<int:order_id>', views.PaymentSuccessView.as_view(), name='success'),
        path('cancel/', views.PaymentFailView.as_view(), name='cancel'),
        path("<total>/<fee>", views.PaymentsView.as_view(), name="payments"),
    ]
