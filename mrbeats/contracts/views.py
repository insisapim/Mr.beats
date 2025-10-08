from django.shortcuts import render, redirect
from django.views import View
from contracts.forms import ContractWorkForm
from contracts.models import ContractWork
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
# Create your views here.
 
class ContractView(View):
    def get(self, request):
        seven_day = timezone.now() - timedelta(days=7)
        active_job = ContractWork.objects.filter(contractor__isnull=True).count()
        avg_budget = ContractWork.objects.aggregate(Avg("wages", default=0))
        recent = ContractWork.objects.filter(created_at__gt=seven_day).count()
        contract_data = ContractWork.objects.all().order_by('-created_at')
        return render(request, 'contract.html', { 'active_job' : active_job, 'avg_budget': avg_budget, 'recent':recent, 'contract_data': contract_data})

    def post(self, request):
        contractor_id = request.POST.get('contractor_id')
        print("contractor_id : ", contractor_id)
        print("id : ", request.user)
        if request.user.is_authenticated:
            add_contractor = ContractWork.objects.get(id=contractor_id)
            add_contractor.contractor = request.user
            add_contractor.status = 'pending'
            add_contractor.save()
            seven_day = timezone.now() - timedelta(days=7)
            active_job = ContractWork.objects.filter(contractor__isnull=True).count()
            avg_budget = ContractWork.objects.aggregate(Avg("wages", default=0))
            recent = ContractWork.objects.filter(created_at__gt=seven_day).count()
            contract_data = ContractWork.objects.all().order_by('-created_at')
            return render(request, 'contract.html', { 'active_job' : active_job, 'avg_budget': avg_budget, 'recent':recent, 'contract_data': contract_data})
        return render(request, 'login.html')
        
class ContractCreateView(View):
    def get(self, request):
        form = ContractWorkForm()
        if request.user.is_authenticated:
            return render(request, 'createcontract.html', {'form' : form})
        return render(request, 'login.html')
    
    def post(self, request):
        form = ContractWorkForm(request.POST)
        if form.is_valid():
            contracts = form.save(commit=False)  
            contracts.client = request.user  
            contracts.save() 
            return redirect('contract')
        return render(request,'createcontract.html', {"form":form})
    
