from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import now
from django.views import View
from django.views.generic import DetailView, CreateView
from django.contrib.auth import login as auth_login, login
from accounts.forms import SignUpForm
from accounts.tokens import account_activation_token
from logs.models import AccountTypeSelected
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
            auth_login(request, user)
            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
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
            login(self.request, user)
            return redirect('index')
        else:
            return render(self.request, 'privalytics/activation_failed.html')


class DashboardView(LoginRequiredMixin, View):
    login_url = '/login'

    def get(self, request):
        return render(request, 'accounts/bar-charts.html')

class WebsiteDetails(DetailView):
    model = Website
    template_name = 'accounts/bar-charts.html'
    context_object_name = 'website'

    def get_object(self):
        return get_object_or_404(Website, website_url=self.kwargs.get('website_url'))