from django.shortcuts import render
from .models import Product
from django.views import View

class home(View):
    
    def get(self, request):
        query = request.GET.get('q')

        if query:
            products = Product.objects.filter(name__icontains=query)
        else:
            products = Product.objects.all()

        return render(request, 'home.html', {'products': products})


class ProductListView(View):

    def get(self, request):

        return render(request, 'product_list.html')
    
class UploadView(View):

    def get(self, request):
        return render(request, 'upload.html')
