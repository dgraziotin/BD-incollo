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
    
    This file contains all the functions regarding diff generation.
"""

import difflib
import datetime
import diff_match_patch

def get_html_diff_list(first_paste,second_paste):
    # creates a diff_match_patch object to prepare diffs
    dmp = diff_match_patch.diff_match_patch()
    # computes the diff and prepares it as human readable
    diffs = dmp.diff_main(first_paste.body, second_paste.body)
    dmp.diff_cleanupSemantic(diffs)
    # convert the diff in html
    html_diffs = dmp.diff_prettyHtml(diffs)
    # creates a uniform placeholder for "return", which is &para;
    html_diffs = html_diffs.replace("<BR>","").replace("\r&para;","&para;")
    # splits the generated html diff, one entry for each line
    html_diffs_list = html_diffs.split("&para;") 
    html_diffs_list_line_no = add_line_numbers(html_diffs_list)
    return html_diffs_list_line_no

def add_line_numbers(html_diffs_list):
    # inserts the line number at the beginning of each line
    result = ""
    line_counter = 1
    for line in html_diffs_list:
        result = result + "<span class=\"lineno\">" + str(line_counter)+ "</span>" + line + "\n"
        line_counter = line_counter + 1
    return result