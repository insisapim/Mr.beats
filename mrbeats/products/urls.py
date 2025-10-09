from django.urls import path
from . import views

urlpatterns = [
        path("", views.HomepageView.as_view(), name="home"),
        path("browse/", views.ProductListView.as_view(), name="product_list"),
        path("uploads/", views.UploadView.as_view(), name="uploads"),
        path("cart/", views.CartView.as_view(), name="cart"),
        path("cart/add/<int:product_id>", views.CartAddView.as_view(), name="cartadd"),
        path("cart/delete/<int:id>", views.CartDeleteView.as_view(), name="cartdelete"),
        path("dowload/", views.DowloadView.as_view(), name="dowload"),
    ]
