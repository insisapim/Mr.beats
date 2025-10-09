from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, update_session_auth_hash
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from accounts.forms import *
from .models import *
from payments.models import Payment
from reviews.models import Review
from django.db.models import Avg, Count, Min, Sum


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
        user = User.objects.get(id=id)
        products = user.products.all()
        prodcount = user.products.all().count()
        totalearn = Payment.objects.filter(user_id=id).aggregate(
            total_earn=Sum("amount"),
            total_count=Count("id")
        )
        user_rating = Review.objects.filter(product__seller_id=id).aggregate(
            avg_rating=Avg('rating'),
        )
        avg_rating = user_rating['avg_rating'] or 0
        return render(request, 'profile.html', {"profileinfo": user, "product": products, "prodcount": prodcount, "totalearn": totalearn, "user_rating": avg_rating})
    

class EditProfileView(View):

    def get(self, request, id):
        user = User.objects.get(id=id)
        forms = ProfileEditForm(instance=user)
        return render(request, "editprofile.html", {"form": forms})
    
    def post(self, request, id):
        user = request.user
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = user.password
            user.save()
            update_session_auth_hash(request, user)
            return redirect('profile', id=id)
        return render(request, 'accounts/edit_profile.html', {'form': form})
    

class EditAccountView(View):

    def get(self, request, id):
        user = User.objects.get(id=id)
        forms = AccountEditForm(instance=user)
        return render(request, "editaccount.html", {"form": forms})

    def post(self, request, id):
        user = request.user
        form = AccountEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            if form.cleaned_data.get("password"):
                update_session_auth_hash(request, user)
            return redirect("profile", id=id)  # เปลี่ยนไปหน้าโปรไฟล์
        else:
            raise ValidationError(form.errors)
