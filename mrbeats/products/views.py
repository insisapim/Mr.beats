from django.shortcuts import render, redirect
from .models import Product
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

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
    
class UploadView(LoginRequiredMixin, View):

    def get(self, request):
        form = ProductForm()
        return render(request, 'upload.html', {"productForm": form,})
    
    def post(self, request):
        upload_type = request.POST.get('upload_type') or request.GET.get('upload_type')
        license_type = request.POST.get('license_type')
        if upload_type == "beat":
            form = ProductForm(request.POST, request.FILES)
        elif upload_type == "lyrics":
            form = LyricsForm(request.POST, request.FILES)
            print("FILES:", request.FILES)
        else:
            return redirect('home')

        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            if upload_type == "lyrics":
                product.license_type = "exclusive"
            if license_type == "royalty_free":
                product.price = 0
            product.save()
            form.save_m2m()
            return redirect('home')
        else:
            raise ValidationError(form.errors);
            


