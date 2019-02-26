from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('logout', LogoutView.as_view(), name='logout'),
    path('', TemplateView.as_view(template_name='privalytics/index.html'), name='index'),
    path('no-personal-information', TemplateView.as_view(template_name='privalytics/no_private_information.html'), name='no-personal-information'),
    path('privacy', TemplateView.as_view(template_name='privalytics/privacy.html'), name='privacy'),
    path('terms', TemplateView.as_view(template_name='privalytics/terms.html'), name='terms'),
    path('data-collection', TemplateView.as_view(template_name='privalytics/data_collection.html'), name='data-collection'),
    path('', include('accounts.urls')),
    path('', include('tracker.urls')),
]
