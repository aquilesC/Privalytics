from django.urls import path

from accounts.views import WebsiteDetails, SignUpView

urlpatterns = [
    path('stats/<str:website_url>', WebsiteDetails.as_view(), name='website-details'),
    path('signup', SignUpView.as_view(), name='signup'),
    # path('login', LoginView.as_view(), name='login'),
]