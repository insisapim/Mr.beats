from django.shortcuts import render, redirect
from django.views import View
from accounts.forms import UserForm
# Create your views here.

class ContractView(View):
    def get(self, request):
        return render(request, 'contract.html')


class ContractCreateView(View):
    def get(self, request):
        return render(request, 'createcontract.html')