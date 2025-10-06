from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from accounts.forms import UserForm

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

        return render(request,'register.html', {"form":form})

class RegisterView(View):
    def get(self, request):
        form = UserForm() 
        return render(request, 'register.html', {"form": form})
    
    def post(self, request):
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        return render(request, 'register.html', {"form": form})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')