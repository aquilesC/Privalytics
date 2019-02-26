from django import forms
from bootstrap_daterangepicker import widgets, fields


class DateRangeForm(forms.Form):
    date_range = fields.DateRangeField(
        input_formats=['%d/%m/%Y'],
        widget=widgets.DateRangeWidget(
            format='%d/%m/%Y'
        )
    )
