import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from decimal import Decimal
from payments.models import Payment
from orders.models import Order, OrderItem
from products.models import Cart, CartItem
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from products.models import Product
stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.
class PaymentsView(LoginRequiredMixin, View):
    def post(self, request):
        total = request.POST.get('total')
        fee = request.POST.get('fee')
        try:
            with transaction.atomic():
                cart = Cart.objects.filter(user=request.user).first()
                check_order = Order.objects.filter(buyer=cart.user, payment_status='pending').first()
                
                if check_order is None:
                    cart_item = CartItem.objects.filter(cart=cart)
                    create_order = Order.objects.create(buyer=cart.user, total_price=total, fee=fee)
                    
                    order_id = create_order.id
                    for i in cart_item:
                        OrderItem.objects.create(order=create_order, product=i.product, unit_price=i.product.price, seller=i.product.seller)
                else:
                    order_id = check_order.id
                
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    mode='payment',
                    line_items=[
                        {
                            'price_data': {
                                'currency': 'usd',
                                'product_data': {
                                    'name': 'Order #' + str(order_id),
                                },
                                'unit_amount': int(float(total) * 100)
                            },
                            'quantity': 1,
                        },
                    ],
                    metadata={'order_id': order_id},
                    success_url=request.build_absolute_uri(f'/payments/success/{order_id}'),
                    cancel_url=request.build_absolute_uri('/payments/cancel/'),
                )
                return redirect(session.url, code=303)
        except ValueError:
            print("values error")
            return redirect('cart')
        

class PaymentSuccessView(LoginRequiredMixin, View):

    def get(self, request, order_id):
        order = Order.objects.filter(id=order_id).first()
        if not order:
            return redirect('product_list')
        if order.payment_status == 'paid':
            return redirect('product_list')
        order = Order.objects.get(id=order_id)
        order.payment_status = 'paid'
        order.order_status = 'completed'
        order.save()

        Payment.objects.create(order=order, user=order.buyer, amount=order.total_price, payment_method='credit', provider='stripe_session', fee=order.fee)
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            CartItem.objects.filter(cart=cart).delete()
        
        return render(request, 'success.html', {"user_id": order.buyer.id})
    
class PaymentFailView(LoginRequiredMixin, View):
    
    def get(self, request):
        return render(request, 'cancel.html')
    

