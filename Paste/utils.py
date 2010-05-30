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
    
    This file contains utilities functions regarding Pastes.
"""

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.core.mail import EmailMessage
from django.conf import settings

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from models import Paste

import datetime

def colorize_syntax(code,language):
    """ Given the code fragments and its programming language,
        returns the code formatted with Pygments as html table
        with line numbers as well
    """
    language = str(language)
    lexer = get_lexer_by_name(language, stripall=True)
    formatter = HtmlFormatter(linenos='inline',linenospecial=5)
    result = highlight(code, lexer, formatter)
    return result


def update_last_view(paste):
    """ Updates the last view of a Paste.
    """
    now = datetime.datetime.now() 
    paste.last_view = now
    paste.save()


def is_collision(hash_key):
    entry = None
    try:
        entry = Paste.objects.get(hash_key = hash_key)
    except Paste.DoesNotExist:
        return False
    return True

def clean_pastes():
    """ Finds Pastes not accessed since 4 weeks, and deletes them
    """
    now = datetime.datetime.now() 
    one_month_ago = now + datetime.timedelta(weeks=-4)
    # retrieve pastes no more viewed since 8 weeks and deletes them
    pastes_to_be_deleted = Paste.objects.filter(last_view__lte=one_month_ago)
    if pastes_to_be_deleted.count() > 0:
        pastes_to_be_deleted.delete() 

def remember_the_paste(request, paste):
    user_pastes = request.session.get('user_pastes', False)
    if not user_pastes:
        user_pastes = []
    else:
        if len(user_pastes) >= settings.MAX_PASTES_REMEMBERED_PER_USER:
            user_pastes.remove(user_pastes[0])
    user_pastes.append(paste.id)
    request.session['user_pastes'] = user_pastes
    
def is_owner_of(request, paste):
    user_pastes = request.session.get('user_pastes', False)
    if not user_pastes:
        return false
    if paste.id in user_pastes:
        return True
    else:
        return False
