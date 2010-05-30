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

from django.db import models
import datetime
import time
import hashlib
import random

class Paste(models.Model):
    entry_date = models.DateTimeField(auto_now_add=True)
    last_view = models.DateTimeField(auto_now_add=True, auto_now=False)
    body = models.TextField()
    language = models.CharField(max_length=50)
    title = models.CharField(max_length=50,blank=True)
    private = models.BooleanField(default=False)
    in_response_to = models.ForeignKey('self',blank=True,null=True)
    hash_key = models.CharField(max_length=50)
    
    class Meta:
        ordering = ["-entry_date"]
        
    def hash(self):
        time_now_epoch = datetime.datetime.now()
        time_now_seconds = int(time.mktime(time_now_epoch.timetuple()))
        return str(hashlib.sha1(str(abs(
                (hash(self) * random.randint(1,5) + time_now_seconds)
            ))).hexdigest())[4:13]
    
    @models.permalink
    def get_absolute_url(self):
        return ('Paste.views.view_paste', [str(self.hash_key)])

    def __unicode__(self):
        return ((self.title or "Untitled Paste") + " - " + (self.language or "No Language Defined"))
    