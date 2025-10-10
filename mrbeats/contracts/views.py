from django.shortcuts import render, redirect
from django.views import View
from contracts.forms import ContractWorkForm
from contracts.models import ContractWork
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
 
class ContractView(LoginRequiredMixin, View):
    def get(self, request):
        seven_day = timezone.now() - timedelta(days=7)
        active_job = ContractWork.objects.filter(contractor__isnull=True).count()
        avg_budget = ContractWork.objects.filter(contractor__isnull=True).aggregate(Avg("wages", default=0))
        recent = ContractWork.objects.filter(created_at__gt=seven_day).count()
        contract_data = ContractWork.objects.filter(contractor__isnull=True).order_by('-created_at')
        return render(request, 'contract.html', { 'active_job' : active_job, 'avg_budget': avg_budget, 'recent':recent, 'contract_data': contract_data})

    def post(self, request):
        contractor_id = request.POST.get('contractor_id')
        add_contractor = ContractWork.objects.get(id=contractor_id)
        if add_contractor.client_id == request.user.id:
            return redirect('contract')
        add_contractor.contractor = request.user
        add_contractor.status = 'pending'
        add_contractor.save()
        return redirect('contract')
        
class ContractCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ContractWorkForm()
        return render(request, 'createcontract.html', {'form' : form})
    
    def post(self, request):
        form = ContractWorkForm(request.POST)
        if form.is_valid():
            contracts = form.save(commit=False)  
            contracts.client = request.user  
            contracts.save() 
            return redirect('contract')
        return render(request,'createcontract.html', {"form":form})
    
class MyContractView(LoginRequiredMixin, View):
    def get(self, request):
        contract = ContractWork.objects.filter(client_id=request.user.id)
        myapply_contract = ContractWork.objects.filter(contractor_id=request.user.id)
        return render(request, 'mycontract.html', {'contract':contract, 'count_my_contract':contract.count(), 'myapply_contract':myapply_contract, 'count_myapply_contract':myapply_contract.count()})


class ActionView(LoginRequiredMixin, View):
    def get(self, request, action, contract_id):
        get_contract = ContractWork.objects.filter(id=contract_id).first()
        if action == 'accepted':
            if get_contract.status == 'accepted':
                return redirect('mycontract')
            get_contract.status = 'accepted'
            get_contract.save()
        if action == 'rejected':
            if get_contract.status == 'rejected':
                get_contract.contractor = None
                return redirect('mycontract')
            get_contract.status = 'rejected'
            get_contract.contractor = None
            get_contract.save()
        if action == 'completed':
            get_contract.delete()
        if action == 'cancel':
            get_contract.contractor = None
            get_contract.save()
        return redirect('mycontract')
    
class ContractEditView(LoginRequiredMixin, View):
    def get(self, request, contract_id):
        get_contract = ContractWork.objects.filter(id=contract_id).first()

        form = ContractWorkForm(initial={
            "title" : get_contract.title,
            "details" : get_contract.details,
            "wages" : get_contract.wages,
            "deadline" : get_contract.deadline
        })
        return render(request, 'editcontract.html', {'form':form, 'contract_id':contract_id})
    def post(self, request, contract_id):
        get_contract = ContractWork.objects.filter(id=contract_id).first()
        form = ContractWorkForm(request.POST, instance=get_contract)
        if form.is_valid():
            form.save()
            return redirect('mycontract')
        return render(request, 'editcontract.html', {'form':form, 'contract_id':contract_id})
        
