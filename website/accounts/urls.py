from django.conf.urls import url
from django.contrib.auth.views import LoginView
from django.urls import path

from accounts.views import WebsiteDetails, SignUpView, ActivateView, DashboardView


urlpatterns = [
    path('stats/<str:website_url>', WebsiteDetails.as_view(), name='website-details'),
    path('signup', SignUpView.as_view(), name='signup'),
    path('signup/<str:account_type>', SignUpView.as_view(), name='signup'),
    path('activate/<str:uidb64>/<str:token>', ActivateView.as_view(), name='activate'),
    path('login', LoginView.as_view(template_name='privalytics/login.html'), name='login'),
    path('account', DashboardView.as_view(), name='account')
]