from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from accounts.forms import DemoForm
from tracker.models import Website


class WebsiteStats(LoginRequiredMixin, DetailView):
    model = Website
    template_name = 'tracker/website_stats.html'
    context_object_name = 'website'

    def get_object(self, queryset=None):
        website = get_object_or_404(Website, website_url=self.kwargs.get('website_url'))
        if self.request.user.has_perm('can_view_website', website):
            return website
        raise PermissionDenied("You do not have permission to view this website")

    def get_context_data(self, **kwargs):
        context = super(WebsiteStats, self).get_context_data(**kwargs)
        context['form'] = DemoForm()
        return context
