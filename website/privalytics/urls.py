from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include


from tracker.views import Index, NoPersonalInformation, PrivacyView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('logout', LogoutView.as_view(), name='logout'),
    path('', Index.as_view(), name='index'),
    path('no-personal-information', NoPersonalInformation.as_view(), name='no-personal-information'),
    path('privacy', PrivacyView.as_view(), name='privacy'),
    path('', include('accounts.urls')),
]
