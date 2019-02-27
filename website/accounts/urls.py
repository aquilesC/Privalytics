from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from accounts.views import SignUpView, ActivateView, DashboardView, CreateWebsite

urlpatterns = [
    path('signup', SignUpView.as_view(), name='signup'),
    path('signup/<str:account_type>', SignUpView.as_view(), name='signup-account-type'),
    path('activate/<str:uidb64>/<str:token>', ActivateView.as_view(), name='activate'),
    path('login', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('account', DashboardView.as_view(), name='account'),
    path('account/new-website', CreateWebsite.as_view(), name='create-website'),
    path('logout', LogoutView.as_view(), name='logout'),
]
