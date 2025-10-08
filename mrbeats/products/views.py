from django.shortcuts import render, redirect
from .models import Product
from django.views import View
from .forms import *

class HomepageView(View):
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
    
class UploadBeatsView(View):

    def post(self, request):
        productform = ProductForm(request.POST, request.FILES)

        if productform.is_valid():
            productform.save()

            return redirect('home')
        
        print("errors:", productform.errors)
        return render(request, "upload.html", {"productForm": productform}) 
