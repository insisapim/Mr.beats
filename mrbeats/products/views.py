from django.http import FileResponse, Http404
from django.shortcuts import render, redirect
from .models import Product
from .models import CartItem, Product, Cart
from django.views import View
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from orders.models import Order, OrderItem

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
        current_type = request.GET.get('type', 'all')
        genre = request.GET.get("genre", "")
        price = request.GET.get("price", "")
        search = request.GET.get("search", "")
        sort = request.GET.get("sort", "")
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
                products = products.order_by(sort)
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
                products = products.order_by(sort)
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
                products = products.order_by(sort)
                
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

class CartView(View):
   
    def get(self, request):
        if request.user.is_authenticated:    
            subtotal = 0  
            cart = Cart.objects.filter(user=request.user).first()
            print("user id", request.user.id)
            if cart is None:
                cart = Cart.objects.create(user=request.user)

            cart_items = CartItem.objects.filter(cart=cart)
            for i in cart_items:
                # print("----------")
                # print("product is :", item.product.title)
                # print("buyer :", item.cart.user.username)
                # print("seller :", item.product.seller.artist_name if item.product.seller.artist_name else item.product.seller.username)
                # print("price :", item.product.price)
                # print("----------")
                subtotal += i.product.price
            fee = float(subtotal) * 0.05
            total = float(subtotal) + fee 
            return render(request, 'cart.html', {'cart_item':cart_items, 'fee':fee, 'subtotal':subtotal, 'total':total})
            # cart = request.session.get('cart', {})
            # print("cart : ", cart)
            # cart_item = []
            # subtotal = 0
            # for i in cart:
            #     subtotal += Decimal(cart[i]['price'])
            #     cart_item.append({
            #         'id' : cart[i]['id'],
            #         'title' : cart[i]['title'],
            #         'seller_id' : cart[i]['seller_id'],
        #         'seller' : cart[i]['seller'],
        #         'price' : cart[i]['price']
        #     })
        # fee = float(subtotal) * 0.05
        # total = float(subtotal) + fee 
        # return render(request, 'cart.html', {'cart_item':cart_item, 'fee':fee, 'subtotal':subtotal, 'total':total})
        return render(request, 'login.html')

    
class CartAddView(View):
    def post(self, request, product_id):
        if request.user.is_authenticated:
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
        #     product = Product.objects.get(id=product_id)
        #     cart = request.session.get('cart', {})
        #     if str(product_id) not in cart:
        #         cart[str(product_id)] = {
        #             'id' : product.id,
        #             'title' : product.title,
        #             'seller_id' : product.seller_id,
        #             'seller' : product.seller.username,
        #             'price' : str(product.price)
        #         }
        #         request.session['cart'] = cart
        #         print(f"add {product.title} in cart")
        #         return redirect('product_list')
        #     else:         
        #         print(f"{product.title} is already in cart")
        #     return redirect('product_list')
        return render(request, 'login.html')

class CartDeleteView(View):

    def get(self, request, id):
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
            cart_item = CartItem.objects.get(id=id, cart=cart)
            print(f"Deleting item: {cart_item.product.title}")
            cart_item.delete()
            print("Item deleted successfully.")
            return redirect('cart')

        return render(request, 'login.html')
    

# class ClearSession(View):

#     def get(self, request):
#         request.session.flush()
#         return redirect('cart')
class EditProductView(View):

    def get(self, request, id):
        if request.user.is_authenticated:

            product = Product.objects.get(id=id)
            
            if (product.lyrics_text == ""):
                productForm = ProductForm(instance=product)
            else:
                productForm = LyricsForm(instance=product)

        return render(request, 'editproduct.html', {"productForm": productForm, "product": product})
    
    def post(self, request, id):
        if request.user.is_authenticated:
            license_type = request.POST.get('license_type')
            prod = Product.objects.get(id=id)
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
                return redirect('home')
            else:
                raise ValidationError(form.errors);

class DeleteProductView(View):

    def post(self, request, id):
        if not request.user.is_authenticated:
            return redirect('login')
        prod = Product.objects.get(id=id)

        if prod.seller_id != request.user.id:
            raise PermissionDenied("You cannot delete this product")

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


class DowloadView(View):

    def get(self, request):
        if request.user.is_authenticated:
            user_id = request.user.id
            order = OrderItem.objects.filter(order__buyer=user_id).distinct('product__title')
            return render(request, 'dowload.html', {"data":order, "user_id":user_id})    
        return render(request, 'login.html')
    
    def post(self, request):
        product_id = request.POST.get('item_id')
        userid = request.POST.get('user_id')
        print("product_id L", product_id)
        print("userid L", userid)
        if request.user.is_authenticated:
            try:
                product = Product.objects.get(id=product_id)
                file_path = product.file.path
                return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=product.title + '.mp3')
            except OrderItem.DoesNotExist:
                raise Http404("File not found.")
        return redirect('dowload')
