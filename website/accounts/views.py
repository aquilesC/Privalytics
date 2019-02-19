import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import now
from django.views import View
from django.views.generic import DetailView, CreateView
from django.contrib.auth import login as auth_login
from accounts.forms import SignUpForm, WebsiteCreationForm, DemoForm
from accounts.tokens import account_activation_token
from logs.models import AccountTypeSelected, TimeToStore
from tracker.models import Website


class SignUpView(View):
    template_name = 'privalytics/sign_up.html'

    def get(self, request, account_type=None):
        form = SignUpForm()
        if account_type:
            if account_type == "basic":
                AccountTypeSelected.objects.create(account_type=AccountTypeSelected.BASIC)
            elif account_type == 'advanced':
                AccountTypeSelected.objects.create(account_type=AccountTypeSelected.ADVANCED)
            else:
                AccountTypeSelected.objects.create(account_type=AccountTypeSelected.OTHER)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            current_site = get_current_site(request)
            subject = 'Activate Your Privalytics Account'
            message = render_to_string('emails/account_activation.txt', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8'),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('index')
        return render(request, self.template_name, {'form': form})


class ActivateView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.profile.email_validated = True
            user.profile.email_validated_date = now()
            user.save()
            auth_login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('account')
        else:
            return render(self.request, 'privalytics/activation_failed.html')


class DashboardView(LoginRequiredMixin, View):
    login_url = '/login'

    def get(self, request):
        t0 = time.time()
        ctx = {}
        websites = request.user.websites.all()
        account_id = request.user.profile.account_id
        ctx.update({'websites': websites, 'account_id': account_id})
        result = render(request, 'privalytics/dashboard.html', ctx)
        t1 = time.time()
        TimeToStore.objects.create(measured_time=t1-t0, measured_type=TimeToStore.MAKE_DASHBOARD)
        return result


class CreateWebsite(LoginRequiredMixin, CreateView):
    model = Website
    form_class = WebsiteCreationForm
    template_name = 'privalytics/new_website.html'
    success_url = reverse_lazy('account')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            website = form.save(commit=False)
            website.owner = request.user
            website.save()
            return redirect('account')
        return render(request, self.template_name, {'form': form})


class WebsiteStats(LoginRequiredMixin, DetailView):
    model = Website
    template_name = 'privalytics/website_stats.html'
    context_object_name = 'website'

    def get_object(self, queryset=None):
        website = get_object_or_404(Website, website_url=self.kwargs.get('website_url'))
        if self.request.user.has_perm('can_view_website', website):
            return website
        raise PermissionDenied("You do not have permission to Enter Clients in Other Company, Be Careful")

    def get_context_data(self, **kwargs):
        context = super(WebsiteStats, self).get_context_data(**kwargs)
        context['form'] = DemoForm()
        return context


class WebsiteDates(LoginRequiredMixin, View):
    template_name = 'privalytics/website_dates.html'

    def get(self, request, *args, **kwargs):
        t0 = time.time()
        ctx = {}
        website = get_object_or_404(Website, website_url=kwargs['website_url'])
        ctx.update({'website': website})
        form = DemoForm(request.GET)
        ctx.update({'form': form})
        if form.is_valid():
            print(form.cleaned_data['date_range'])
            start_date = form.cleaned_data['date_range'][0]
            end_date = form.cleaned_data['date_range'][1]
            data = website.get_stats_dates(start_date, end_date)
            ctx.update({'data': data})
            result = render(request, self.template_name, ctx)
            t1 = time.time()
            TimeToStore.objects.create(measured_time=t1-t0, measured_type=TimeToStore.MAKE_WEBSITE_STATS)
            return result
        return render(request, self.template_name, ctx)
