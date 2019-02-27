import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import NON_FIELD_ERRORS
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import now
from django.views import View
from django.views.generic import CreateView
from django.contrib.auth import login as auth_login
from accounts.forms import SignUpForm, WebsiteCreationForm
from accounts.tokens import account_activation_token
from logs.models import AccountTypeSelected, TimeToStore
from tracker.models import Website


class SignUpView(View):
    template_name = 'accounts/sign_up.html'

    def get(self, request, account_type=None):
        form = SignUpForm()
        if account_type:
            if account_type == "basic":
                AccountTypeSelected.objects.create(account_type=AccountTypeSelected.BASIC)
            elif account_type == 'advanced':
                AccountTypeSelected.objects.create(account_type=AccountTypeSelected.ADVANCED)
            else:
                AccountTypeSelected.objects.create(account_type=AccountTypeSelected.OTHER)
            request.session['account_type'] = account_type
            print(request.session.get('account_type'))
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Privalytics Account'
            message = render_to_string('emails/account_activation.txt', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8'),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message, from_email='Privalytics <noreply@privalytics.io>')
            user.profile.account_selected = request.session.get('account_type')
            user.save()
            user.profile.save()
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('account')
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
            return render(self.request, 'accounts/activation_failed.html')


class DashboardView(LoginRequiredMixin, View):
    login_url = '/login'

    def get(self, request):
        t0 = time.time()
        ctx = {}
        websites = request.user.websites.all()
        account_id = request.user.profile.account_id
        ctx.update({'websites': websites, 'account_id': account_id})
        result = render(request, 'accounts/dashboard.html', ctx)
        t1 = time.time()
        TimeToStore.objects.create(measured_time=t1-t0, measured_type=TimeToStore.MAKE_DASHBOARD)
        return result


class CreateWebsite(LoginRequiredMixin, CreateView):
    model = Website
    form_class = WebsiteCreationForm
    template_name = 'accounts/new_website.html'
    success_url = reverse_lazy('account')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            total_websites = request.user.websites.count()
            if total_websites >= request.user.profile.max_websites:
                form.errors[NON_FIELD_ERRORS] = ['You can\'t register more websites']
                return render(request, self.template_name, {'form': form})
            website = form.save(commit=False)
            website.owner = request.user
            website.save()
            return redirect('account')
        return render(request, self.template_name, {'form': form})

