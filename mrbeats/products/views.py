from django.shortcuts import render, redirect
from .models import Product
from .models import CartItem, Product, Cart
from django.views import View
from decimal import Decimal


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
        product = Product.objects.all()

        return render(request, 'product_list.html', {"product": product})
    
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
