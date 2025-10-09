from django.urls import path
from . import views

urlpatterns = [
        path("", views.HomepageView.as_view(), name="home"),
        path("browse/", views.ProductListView.as_view(), name="product_list"),
        path('uploads/', views.UploadView.as_view(), name='uploads'),
    ]
