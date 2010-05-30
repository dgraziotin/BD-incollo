"""
    This file is part of BD-incollo.

    BD-incollo is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    BD-incollo is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with BD-incollo.  If not, see <http://www.gnu.org/licenses/>.
"""

from django.forms import ModelForm
from django import forms
from models import Paste

class PasteForm(ModelForm):
    '''Form for inserting a Paste
    '''
    class Meta:
        model = Paste
        fields = ('title', 'language','private','body')

REPORT_REASONS = (
    ('spam', 'Spam'),
    ('warez', 'Serials/Link to Warez'),
    ('other', 'Other'),
)

class ReportForm(forms.Form):
    '''Form for reporting a Paste
    '''
    reason = forms.ChoiceField(choices=REPORT_REASONS,widget=forms.RadioSelect())
    comment = forms.CharField(widget=forms.Textarea(attrs={'size':'10'}))
    email = forms.EmailField()
