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

from django.conf.urls.defaults import *

from Paste.models import Paste
from Paste.views import add_paste, view_paste, download_paste, report_paste, view_latest_pastes, search_pastes, discuss_paste, compare_pastes, mark_as_spam, view_latest_user_pastes, delete_paste

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    (r'^media/(.*)', 'django.views.static.serve', {'document_root': '/home/incollo/Incollo/media'}),
    (r'^media-admin/(.*)', 'django.views.static.serve', {'document_root': '/home/incollo/Incollo/media-admin'}),
    (r'^admin/(.*)', admin.site.root),
    (r'^about', 'django.views.generic.simple.direct_to_template', {'template': 'about.html'}),
    (r'^bug', 'django.views.generic.simple.direct_to_template', {'template': 'bug.html'}),
    (r'^news', 'django.views.generic.simple.direct_to_template', {'template': 'news.html'}),
    (r'^$', add_paste),
    (r'^(?P<hash_key>[A-Fa-f0-9]+)$', view_paste),
    (r'^download/(?P<hash_key>[A-Fa-f0-9]+)', download_paste),
    (r'^report/(?P<hash_key>[A-Fa-f0-9]+)', report_paste),
    (r'^discuss/(?P<hash_key>[A-Fa-f0-9]+)', discuss_paste),
    (r'^compare/(?P<first_hash_key>[A-Fa-f0-9]+)/(?P<second_hash_key>[A-Fa-f0-9]+)', compare_pastes),
    (r'^latest-pastes$', view_latest_pastes),
    (r'^latest-personal-pastes$', view_latest_user_pastes),
    (r'^search/$', search_pastes),
    (r'^spam/(?P<hash_key>[A-Fa-f0-9]+)$', mark_as_spam),
    (r'^delete/(?P<hash_key>[A-Fa-f0-9]+)', delete_paste),
    (r'^comments/', include('django.contrib.comments.urls')),

)


