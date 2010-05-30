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
    
    This file contains all the views accessible by a HTTP request.
"""

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, Http404
from django.db.models import Q
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template import RequestContext

from models import Paste
from forms import PasteForm, ReportForm

from utils import is_collision
from utils import clean_pastes
from utils import update_last_view
from utils import colorize_syntax
from utils import remember_the_paste
from utils import is_owner_of

from diff import get_html_diff_list

from honeypot.decorators import check_honeypot

@check_honeypot
def add_paste(request):
    """ Adds a new paste in the database
    """
    clean_pastes()
    if request.method == 'POST': # If the form has been submitted...
        form = PasteForm(request.POST) # creates a PasteForm object with the posted data
        if form.is_valid():
            tempPaste = form.save(commit=False)
            tempPaste.hash_key = tempPaste.hash()
            # recompute the hash key if there is a collision
            while (is_collision(tempPaste.hash_key)): 
                tempPaste.hash_key = tempPaste.hash()   
            tempPaste.save()
            remember_the_paste(request,tempPaste)
            return HttpResponseRedirect(tempPaste.get_absolute_url()) # visualize the Paste
    else:
        form = PasteForm() # A new form
    return render_to_response('paste_form.html', {
        'error_message': None,
        'form': form,
    },context_instance=RequestContext(request))

def search_pastes(request):
    """ Queries the database and searches public Pastes
    """
    query = request.GET.get('q','')
    entries = []
    if query:
        qset = (
            Q(title__icontains=query) |
            Q(language__icontains=query) |
            Q(body__icontains=query)
        )
        entries = Paste.objects.filter(qset,private=False).distinct()

    return render_to_response('search_pastes.html', {
        'entries': entries,
        'query': query,
    },context_instance=RequestContext(request))


def view_latest_pastes(request):
    """ Visualizes the last Pastes
    """
    entries = []
    try:
        entries = Paste.objects.filter(private=False)[:settings.MAX_PASTES_FOR_LATEST_PASTES_SECTION]
    except IndexError:
        entries = Paste.objects.filter(private=False)
    return render_to_response('view_latest_pastes.html', {
        'personal_pastes': False,
        'entries': entries,
    },context_instance=RequestContext(request))


def view_paste(request,hash_key):
    """ Given its hash key, visualizes it
    """
    hash_key = str(hash_key)
    entry = get_object_or_404(Paste, hash_key=hash_key)
    update_last_view(entry)
    clean_pastes()
    # generates syntax highlighting
    colorized_body = colorize_syntax(entry.body,entry.language)

    # creates the form for reporting the Paste to admin
    report_form = ReportForm()
    report_message = ""

    if request.method == 'GET':
        if request.GET.has_key("reported"):
            report_message = "Thank you for your report!"
        if request.GET.has_key("error_report"):
            report_message = "There has been an error. Please contact an administrator!"
    return render_to_response('view_paste.html', {
        'entry': entry,
        'colorized_body': colorized_body,
        'report_form': report_form,
        'report_message': report_message,
    },context_instance=RequestContext(request))

def download_paste(request,hash_key):
    """ Given its hash key, returns the Paste as plain text file
    """
    hash_key = str(hash_key)
    entry = get_object_or_404(Paste, hash_key=hash_key)
    update_last_view(entry)
    clean_pastes()
    response = HttpResponse(mimetype='text/plain')  # set the mimetype for a text file
    response.write(entry.body)                      # write it to the response
    response['Filename'] = 'incollo.com-'+ str(entry.hash_key) +'.txt'
    response['Content-Disposition'] = 'attachment; filename=incollo.com-'+ str(entry.hash_key) +'.txt'
    return response


def report_paste(request,hash_key):
    """ Sends a e-mail to the site administrator, reporting a Paste
    """
    entry = get_object_or_404(Paste, hash_key=hash_key)
    report_message = ""
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            comment = form.cleaned_data['comment']
            email = form.cleaned_data['email']
            # prepare the e-mail with data submitted by the user
            report_body = ''' Paste located at http://incollo.com/%s has been reported with reason '%s'.\n Additional comment: %s .\n User e-mail: %s ''' %  (hash_key, reason, comment, email)
            # send the e-mail
            report = EmailMessage('Report abuse from bd-incollo!',
                                  report_body,
                                  to=settings.MANAGERS[0],
                                  )
            report.send()
            report_message = "Thank you for your report!"
        else:
            report_message = "Some fields are either missing or invalid, please complete the form"    
    
    report_form = ReportForm()  # create a form for reporting the Paste (if needed)
    return render_to_response('report_paste.html', {
        'report_message': report_message,
        'entry': entry,
        'report_form': report_form,
    },context_instance=RequestContext(request))

@check_honeypot
def discuss_paste(request,hash_key):
    """ Creates a new Paste, linking it with a previous one.
        In this way, Pastes may be enhanced and diffs can be performed
    """
    paste_discussed = get_object_or_404(Paste, hash_key=hash_key)
    update_last_view(paste_discussed)
    clean_pastes()
    form = PasteForm(instance=paste_discussed)
    language = paste_discussed.language
    private = paste_discussed.private
    
    if request.method == 'POST': 
        form = PasteForm(request.POST)
        if form.is_valid():
            tempPaste = form.save(commit=False)
            tempPaste.hash_key = tempPaste.hash()
            # recompute the hash key if there is a collision
            while (is_collision(tempPaste.hash_key)): 
                tempPaste.hash_key = tempPaste.hash()
            tempPaste.in_response_to = paste_discussed
            tempPaste.private = private
            tempPaste.save()
            return HttpResponseRedirect(tempPaste.get_absolute_url()) # visualize the Paste'''
    return render_to_response('discuss_paste.html', {
        'error_message': None,
        'paste_discussed': paste_discussed,
        'form': form,
    },context_instance=RequestContext(request))


def compare_pastes(request,first_hash_key, second_hash_key):
    """ Given their hash keys, retrieves two Pastes and compares them.
        Diff is computed using diff-match-patch by Neil Fraser (http://code.google.com/p/google-diff-match-patch/)
        Line numbering for snippets is computed manually, only for this view
    """
    first_hash_key = str(first_hash_key)
    second_hash_key = str(second_hash_key)
    first_entry = get_object_or_404(Paste, hash_key=first_hash_key)
    second_entry = get_object_or_404(Paste, hash_key=second_hash_key)
    
    update_last_view(first_entry)
    update_last_view(second_entry)
    clean_pastes()
    
    
    html_diff = get_html_diff_list(first_entry,second_entry)

    return render_to_response('compare_pastes.html', {
        'diff': html_diff,
    },context_instance=RequestContext(request))

def view_latest_user_pastes(request):
    ''' Looks for the "user_pastes" session Cookies. If found, searches the corresponding Pastes
        and returns them to the template.
    '''
    try:
        user_pastes = Paste.objects.filter(id__in=request.session.get('user_pastes', None))
    except:
        user_pastes = None
   
    return render_to_response('view_latest_pastes.html', {
        'personal_pastes': True,
        'entries': user_pastes,
    },context_instance=RequestContext(request))

def delete_paste(request,hash_key):
    ''' Given its hash key, deletes a Paste if and only if the user is also
        the owner of the Paste
    '''
    hash_key = str(hash_key)
    paste = get_object_or_404(Paste,hash_key=hash_key)
    if is_owner_of(request,paste):
        request.session['user_pastes'].remove(paste.id)
        paste.delete()
        return HttpResponseRedirect(reverse(view_latest_user_pastes))
    else:
        raise Http404


def mark_as_spam(request,hash_key):
    """ Given the hash keys, retrieves the corresponding Paste, marks it as Spam, deletes it
        and returns the result of the operation
    """
    entry_hash_key = str(hash_key)
    if not request.user.is_superuser:
        return HttpResponse(False, mimetype="# text/ecmascript")
    try:
        entry = Paste.objects.get(hash_key=entry_hash_key)
        submit_spam(request,entry.body)
        entry.delete()
    except: 
        return HttpResponse(False, mimetype="# text/ecmascript")
    return HttpResponse(True, mimetype="# text/ecmascript")
   