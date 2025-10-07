from django.urls import path

from contracts.views import ContractView, ContractCreateView


urlpatterns = [
    path('', ContractView.as_view(), name="contract"),
    path('create/', ContractCreateView.as_view(), name="createcontract"),
]