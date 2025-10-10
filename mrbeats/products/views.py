from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .models import CartItem, Product, Cart
from django.views import View
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from .forms import *
from django.db.models import Q
from django.http import HttpResponseForbidden
from orders.models import Order, OrderItem
from reviews.models import Review
class HomepageView(View):
    def get(self, request):
        products = Product.objects.all().order_by("-downloads")[:4]
        MAX_CHARS = 600  # limit ขนาดที่จะส่งไปยัง template
        for p in products:
            preview_text = ""
            if getattr(p, "lyrics_text", None):
                preview_text = p.lyrics_text.strip()
                if len(preview_text) > MAX_CHARS:
                    preview_text = preview_text[:MAX_CHARS].rsplit("\n", 1)[0] + "\n\n... (truncated)"
            p.preview_text = preview_text

        return render(request, 'home.html', {'products': products})


class ProductListView(View):

    def get(self, request):
        current_type = request.GET.get('type', 'all')
        genre = request.GET.get("genre", "")
        price = request.GET.get("price", "")
        search = request.GET.get("search", "")
        sort = request.GET.get("sort", "")
        sortby = request.GET.get("sort-by", "")

        final_sort = sortby+sort
        print("type:", current_type, "\n", "genre:", genre, "\n", "price:", price, "\n", "search:", search, "\n", "sort:", sort)

        if (current_type == "" or current_type == 'all'):
            products = Product.objects.select_related('seller').all()
            if (genre and genre != "all"):
                products = products.filter(genre__name=genre)
            if (price != "all" and price != ""):
                if "+" in price:
                    min_price = int(price.replace("+", ""))
                    products = products.filter(price__gte=min_price)
                else:
                    min_price, max_price = map(int, price.split("-"))
                    products = products.filter(price__range=(min_price, max_price))

            if (search != ""):
                products = products.filter(Q(title__icontains=search) | Q(lyrics_text__icontains=search))
            if (sort != ""):
                products = products.order_by(final_sort)
        elif (current_type == 'beats'):
            products = Product.objects.select_related('seller').filter(Q(lyrics_text__isnull=True) | Q(lyrics_text=""))
            if (genre and genre != "all"):
                products = products.filter(genre__name=genre)
            if (price != "all" and price != ""):
                if "+" in price:
                    min_price = int(price.replace("+", ""))
                    products = products.filter(price__gte=min_price)
                else:
                    min_price, max_price = map(int, price.split("-"))
                    products = products.filter(price__range=(min_price, max_price))
            if (search != ""):
                products = products.filter(title__icontains=search)
            if (sort != ""):
                products = products.order_by(final_sort)
        elif (current_type == "lyrics"):
            products = Product.objects.select_related('seller').exclude(Q(lyrics_text__isnull=True) | Q(lyrics_text=""))
            if (genre and genre != "all"):
                products = products.filter(genre__name=genre)
            if (price != "all" and price != ""):
                if "+" in price:
                    min_price = int(price.replace("+", ""))
                    products = products.filter(price__gte=min_price)
                else:
                    min_price, max_price = map(int, price.split("-"))
                    products = products.filter(price__range=(min_price, max_price))

            if (search != ""):
                products = products.filter(Q(title__icontains=search) | Q(lyrics_text__icontains=search))
            if (sort != ""):
                products = products.order_by(final_sort)
                
        MAX_CHARS = 600  # limit ขนาดที่จะส่งไปยัง template
        for p in products:
            preview_text = ""
            if getattr(p, "lyrics_text", None):
                preview_text = p.lyrics_text.strip()
                if len(preview_text) > MAX_CHARS:
                    preview_text = preview_text[:MAX_CHARS].rsplit("\n", 1)[0] + "\n\n... (truncated)"
            p.preview_text = preview_text

        genres = Genre.objects.all()
        return render(request, 'product_list.html', {"product": products, "genres" : genres})
    
class UploadView(LoginRequiredMixin, View):
    login_url = 'login'
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
            raise ValidationError(form.errors)

class CartView(LoginRequiredMixin, View):
   
    def get(self, request):
        subtotal = 0  
        cart = Cart.objects.filter(user=request.user).first()
        if cart is None:
            cart = Cart.objects.create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        for i in cart_items:
            subtotal += i.product.price
        fee = float(subtotal) * 0.05
        total = float(subtotal) + fee 
        return render(request, 'cart.html', {'cart_item':cart_items, 'fee':fee, 'subtotal':subtotal, 'total':total})
    

    
class CartAddView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        cart = Cart.objects.filter(user=request.user).first()
        if cart is None:
            cart = Cart.objects.create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        get_product = Product.objects.get(id=product_id)
        
        for i in cart_items:
            if product_id == i.product.id:
                print("already have this item")
                return redirect('product_list')       
        add_cart_items = CartItem(cart=cart, product=get_product)
        add_cart_items.save()
        return redirect('cart')

class CartDeleteView(LoginRequiredMixin, View):

    def get(self, request, id):
        cart = Cart.objects.filter(user=request.user).first()
        cart_item = CartItem.objects.get(id=id, cart=cart)
        cart_item.delete()
        return redirect('cart')

    

# class ClearSession(View):

#     def get(self, request):
#         request.session.flush()
#         return redirect('cart')
class EditProductView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'login'
    raise_exception = True

    def get_object(self):
        # ดึง id จาก kwargs (คุณส่ง id ผ่าน URL เช่น path('editproduct/<int:id>/', ...))
        return get_object_or_404(Product, pk=self.kwargs.get('id'))

    def test_func(self):
        prod = self.get_object()
        return prod.seller_id == self.request.user.id
    
    def get(self, request, id):
        product = self.get_object()

        if (product.lyrics_text == ""):
            productForm = ProductForm(instance=product)
        else:
            productForm = LyricsForm(instance=product)

        return render(request, 'editproduct.html', {"productForm": productForm, "product": product})
    
    def post(self, request, id):
        license_type = request.POST.get('license_type')
        prod = self.get_object()
        
        if prod.lyrics_text == "" :
            form = EditProductForm(request.POST or None, request.FILES or None, instance=prod)
        else:
            form = EditLyricsForm(request.POST or None, request.FILES or None, instance=prod)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            if prod.lyrics_text == "":
                product.license_type = "exclusive"
            if license_type == "royalty_free":
                product.price = 0
            product.save()
            form.save_m2m()
            return redirect('product_list')
        else:
            raise ValidationError(form.errors);

class DeleteProductView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'login'
    raise_exception = True

    def get_object(self):
        # ดึง id จาก kwargs (คุณส่ง id ผ่าน URL เช่น path('editproduct/<int:id>/', ...))
        return get_object_or_404(Product, pk=self.kwargs.get('id'))

    def test_func(self):
        prod = self.get_object()
        print(prod)
        return prod.seller.id == self.request.user.id

    def post(self, request, id):
        prod = self.get_object()
        

        # ลบไฟล์ที่เกี่ยวข้อง (ถ้ามี)
        try:
            if prod.file:
                prod.file.delete(save=False)
            if prod.preview_file:
                prod.preview_file.delete(save=False)
            if prod.product_image:
                prod.product_image.delete(save=False)
        except Exception as e:
            print("Error deleting files:", e)

        prod.delete()
        return redirect('home')


class DowloadView(LoginRequiredMixin, View):

    def get(self, request):
        user_id = request.user.id
        order = OrderItem.objects.filter(order__buyer=user_id).distinct('product__title')
        return render(request, 'dowload.html', {"data":order, "user_id":user_id})    
    
    def post(self, request):
        product_id = request.POST.get('item_id')
        try:
            product = Product.objects.get(id=product_id)
            file_path = product.file.path
            product.downloads += 1 
            product.save()
            if product.lyrics_text:
                return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=product.title + '.txt')
            else:
                return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=product.title + '.mp3')
        except OrderItem.DoesNotExist:
            raise Http404("File not found.")

class ReviewView(LoginRequiredMixin, View):

    def post(self, request):
        score = request.POST.get("score")
        comment = request.POST.get("comment")
        product_id = request.POST.get("product_id")
        user = request.user
        get_product = Product.objects.filter(id=product_id).first()
        get_review = Review.objects.filter(product=get_product).first()
        
        if get_review is None:
            Review.objects.create(product=get_product, reviewer=user, rating=score, comment=comment)
        else:
            get_review.rating = score
            get_review.comment = comment
            get_review.save()
        return redirect('dowload')