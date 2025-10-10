from django.urls import path

from contracts.views import ContractView, ContractCreateView, ContractEditView, MyContractView, ActionView


urlpatterns = [
    path('', ContractView.as_view(), name="contract"),
    path('create/', ContractCreateView.as_view(), name="createcontract"),
    path('edit/<int:contract_id>', ContractEditView.as_view(), name="editcontract"),
    path('mycontract/', MyContractView.as_view(), name="mycontract"),
    path('action/<str:action>/<int:contract_id>', ActionView.as_view(), name="action"),

]