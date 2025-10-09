from django.urls import path

from accounts.views import *


urlpatterns = [
    path('', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('register', RegisterView.as_view(), name="register"),
    path('profile/<int:id>', ProfileView.as_view(), name="profile"),
    path('editprofile/<int:id>', EditProfileView.as_view(), name="edit-profile"),
    path('editaccount/<int:id>', EditAccountView.as_view(), name="edit-account")
]