from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, update_session_auth_hash
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from accounts.forms import *
from .models import *
from payments.models import Payment
from reviews.models import Review
from orders.models import OrderItem
from django.db.models import Avg, Count, Min, Sum, F
from django.db.models.functions import TruncMonth
import json
from django.core.exceptions import PermissionDenied


class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {"form": form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request,user)
            return redirect('home')  
        return render(request, 'login.html', {"form": form})

class RegisterView(View):
    def get(self, request):
        form = UserForm() 
        return render(request, 'register.html', {"form": form})
    
    def post(self, request):
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, 'register.html', {"form": form})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
    
class ProfileView(View):
    def get(self, request, id):
        earnings_qs = (
                OrderItem.objects
                .filter(seller_id=id, order__payment_status='paid')
                .annotate(month=TruncMonth('order__created_at'))
                .values('month')
                .annotate(total=Sum(F('unit_price') * F('quantity')))
                .order_by('month')
            )
        


        months = [p['month'].strftime('%Y-%m') for p in earnings_qs]
        earnings = [float(p['total'] or 0) for p in earnings_qs]

        #ทำ dic ตามคะแนน รีวิว
        ratings = (Review.objects
                .filter(product__seller_id=id)
                .values('rating')
                .annotate(cnt=Count('id'))
                .order_by('rating'))
        
        # ใส่ว่าแต่ละคะแนนมีกี่ตัว แล้ว แยกเป็น list 
        rating_counts = {i: 0 for i in range(1, 6)}
        for r in ratings:
            rating_counts[r['rating']] = r['cnt']
        rating_labels = list(rating_counts.keys())
        rating_values = list(rating_counts.values())

        context = {
        'months_json': json.dumps(months),
        'earnings_json': json.dumps(earnings),
        'rating_labels_json': json.dumps(rating_labels),
        'rating_values_json': json.dumps(rating_values),
    }
        
        user = User.objects.get(id=id)
        products = user.products.all()
        prodcount = user.products.all().count()
        totalearn = OrderItem.objects.filter(seller_id=id).aggregate(total_earn=Sum(F('unit_price') * F('quantity')),total_count=Count('id'))
        user_rating = Review.objects.filter(product__seller_id=id).aggregate(
            avg_rating=Avg('rating'),
        )
        avg_rating = user_rating['avg_rating'] or 0
        MAX_CHARS = 600  # limit ขนาดที่จะส่งไปยัง template

        for p in products:
            preview_text = ""
            if getattr(p, "lyrics_text", None):
                preview_text = p.lyrics_text.strip()
                if len(preview_text) > MAX_CHARS:
                    preview_text = preview_text[:MAX_CHARS].rsplit("\n", 1)[0] + "\n\n..."
            p.preview_text = preview_text

        return render(request, 'profile.html', {"profileinfo": user, "product": products, "prodcount": prodcount, "totalearn": totalearn, "user_rating": avg_rating, "context": context})

    

class EditProfileView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "login"
    raise_exception=True

    def test_func(self):
        pk = self.kwargs.get('id')
        return pk == self.request.user.id

    def get(self, request, id):
        user = User.objects.get(id=id)
        
        forms = ProfileEditForm(instance=user)
        return render(request, "editprofile.html", {"form": forms})
    
    def post(self, request, id):
        user = User.objects.get(id=id)
        
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = user.password
            user.save()
            update_session_auth_hash(request, user)
            return redirect('profile', id=id)
        return render(request, 'accounts/edit_profile.html', {'form': form})
    

class EditAccountView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "login"
    raise_exception=True

    def test_func(self):
        pk = self.kwargs.get('id')
        return pk == self.request.user.id

    def get(self, request, id):
        user = User.objects.get(id=id)
        
        forms = AccountEditForm(instance=user)
        return render(request, "editaccount.html", {"form": forms})

    def post(self, request, id):
        user = User.objects.get(id=request.user.id)
        form = AccountEditForm(request.POST, instance=user)
        
        if form.is_valid():
            form.save()
            if form.cleaned_data.get("password"):
                update_session_auth_hash(request, user)
            return redirect("profile", id=id)  # เปลี่ยนไปหน้าโปรไฟล์
        else:
            return render(request, "editaccount.html", {"form": form})
