from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView

from tracker.models import Website


class WebsiteDetails(DetailView):
    model = Website
    template_name = 'accounts/bar-charts.html'
    context_object_name = 'website'

    def get_object(self):
        return get_object_or_404(Website, website_url=self.kwargs.get('website_url'))


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'privalytics/signup.html'