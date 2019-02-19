from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from accounts.views import SignUpView, ActivateView, DashboardView, CreateWebsite, WebsiteStats, WebsiteDates, \
    PublicWebsiteView, PublicWebsiteDates

urlpatterns = [
    path('signup', SignUpView.as_view(), name='signup'),
    path('signup/<str:account_type>', SignUpView.as_view(), name='signup'),
    path('activate/<str:uidb64>/<str:token>', ActivateView.as_view(), name='activate'),
    path('login', LoginView.as_view(template_name='privalytics/login.html'), name='login'),
    path('account', DashboardView.as_view(), name='account'),
    path('account/new-website', CreateWebsite.as_view(), name='create-website'),
    path('account/<str:website_url>', WebsiteStats.as_view(), name='website-stats'),
    path('account/<str:website_url>/dates', WebsiteDates.as_view(), name='website-dates'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('ws/<str:website_url>', PublicWebsiteView.as_view(), name='public-stats'),
    path('ws/<str:website_url>/dates', PublicWebsiteDates.as_view(), name='public-website-dates'),
]
