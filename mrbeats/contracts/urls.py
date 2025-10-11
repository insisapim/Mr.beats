from django.urls import path

from contracts.views import ContractView, ContractCreateView, ContractEditView, MyContractView, ActionView, ContractDeleteView


urlpatterns = [
    path('', ContractView.as_view(), name="contract"),
    path('create/', ContractCreateView.as_view(), name="createcontract"),
    path('edit/<int:contract_id>', ContractEditView.as_view(), name="editcontract"),
    path('delete/<int:contract_id>', ContractDeleteView.as_view(), name="deletecontract"),
    path('mycontract/', MyContractView.as_view(), name="mycontract"),
    path('action/<str:action>/<int:contract_id>', ActionView.as_view(), name="action"),

]