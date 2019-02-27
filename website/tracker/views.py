from datetime import timedelta

from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from django.views import View

from tracker.forms import DateRangeForm
from tracker.models import Website


class WebsiteStats(View):
    template_name = 'tracker/website_stats.html'

    def get_context(self, website, start_date, end_date):
        visitors = website.get_daily_visits(start_date, end_date)
        total_visitors = website.get_page_views(start_date, end_date)
        referrers = website.get_top_referrers(start_date, end_date)
        pages = website.get_top_pages(start_date, end_date)
        devices = website.get_top_devices(start_date, end_date)
        operating_systems = website.get_top_os(start_date, end_date)
        screen_widths = website.get_top_screen_width(start_date, end_date)

        ctx = {}
        ctx.update({
            'visitors': visitors,
            'total_visitors': total_visitors,
            'referrers': referrers,
            'pages': pages,
            'devices': devices,
            'operating_systems': operating_systems,
            'screen_widths': screen_widths,
        })
        ctx.update({'website': website})

        if website.owner.profile.can_geolocation:
            countries = website.get_top_countries(start_date, end_date)
            ctx.update({'countries': countries})
        return ctx

    def get(self, request, website_url):
        start_date = now()-timedelta(days=30)
        end_date = now()

        website = get_object_or_404(Website, website_url=website_url)
        if not website.is_public and not self.request.user.has_perm('can_view_website', website):
            return redirect('login')

        ctx = self.get_context(website, start_date, end_date)
        ctx.update({'form': DateRangeForm(initial={'date_range': (start_date, end_date)})})
        return render(request, self.template_name, ctx)

    def post(self, request, website_url):
        website = get_object_or_404(Website, website_url=website_url)
        if not website.is_public and not self.request.user.has_perm('can_view_website', website):
            return redirect('login')
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['date_range'][0]
            end_date = form.cleaned_data['date_range'][1]
            ctx = self.get_context(website, start_date, end_date)
            ctx.update({'form': form})
            return render(request, self.template_name, ctx)
        return redirect(website.get_absolute_url())
