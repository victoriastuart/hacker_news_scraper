#!/usr/bin/env  python3
# coding: utf-8
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python textwidth=220

""" ===========================================================================
         file: /mnt/Vancouver/programming/python/scripts/hn.py
        about: Python script to scrape Hacker News feed and filter by {points | number of comments | keywords}
        title: Hacker News Scraper
       author: Victoria A. Stuart
     based on: https://github.com/RBrache21/HackerNewsScrapper
      created: 2020-04-09
      version: 07
last modified: 2020-05-05 10:46:31 -0700 (PST)

   Notes: I program in Vim with textwidth=220

Versions:
    * v01 : modifications to script sourced from GitHub (link above)
    * v02 : scripting / testing
    * v03 : added [exclusions] list; cleaned up code (removed extraneous comments ...)
    * v04 : added URL to Hacker News source (which contains the Comments, if any)
    * v05 : edited (cleaned) script
    * v06 : minor edits: replaced brittle results older that code with simple "if float(item['age (h)']) < 12:"; ...
    * v07 : run 2x daily --> once/day (6 am); added (method; regex expressions dict) to process output text

See also:
    * https://edavis.github.io/hnrss/
    * https://news.ycombinator.com/newsfaq.html

Usage: via crontab and/or ~/.bashrc alias.  Recommendation: 2x daily via crontab.

    # ----------------------------------------------------------------------------
    * CRONTAB (sudo vim crontab):

        # ============================================================================
        # HACKER NEWS FEED UPDATE
        # ============================================================================
        # m    h    dom    mon    dow    user    nice    command
        # "At 6 and 18 daily." [http://crontab.guru/]:
        0    6,18    *    *    *    victoria    nice -n 19    /home/victoria/venv/py3.7/bin/python /mnt/Vancouver/programming/python/scripts/hn.py
        0    6,18    *    *    *    victoria    nice -n 19    notify-send -i "/mnt/Vancouver/programming/python/scripts/hacker_news.png" -t 0 "New Hacker News feeds at" "<span color='#57dafd' font='16px'><a href=\"file:///mnt/Vancouver/programming/python/scripts/output/\">/mnt/Vancouver/programming/python/scripts/output/</a></span>"

        The last line above, reformatted here for readability but one line in crontab, is:

            notify-send -i "/mnt/Vancouver/programming/python/scripts/hacker_news.png" -t 0 "New Hacker News feeds at" \
            "<span color='#57dafd' font='16px'><a href=\"file:///mnt/Vancouver/programming/python/scripts/output/\" > \
            /mnt/Vancouver/programming/python/scripts/output/</a></span>"

    # ----------------------------------------------------------------------------
    * BASHRC (~/.bashrc [p37 venv]):

        alias hn='/home/victoria/venv/py3.7/bin/python /mnt/Vancouver/programming/python/scripts/hn.py; sleep 5; cat /mnt/Vancouver/programming/python/scripts/output/hn.txt'

        alias hncat='cat /mnt/Vancouver/programming/python/scripts/output/hn.txt'
==============================================================================
"""
# https://stackoverflow.com/questions/879173/how-to-ignore-deprecation-warnings-in-python
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
warnings.filterwarnings("ignore", category=UserWarning)
# ============================================================================

# ----------------------------------------------------------------------------
## SAMPLE SOURCE HTML [2020-04-17 07:51:58 -0700 (PST)]:

# <tr class='athing' id='22897846'>
#     <td align="right" valign="top" class="title">
#         <span class="rank">1.</span>
#     </td>
#     <td valign="top" class="votelinks">
#         <center>
#             <a id='up_22897846' onclick='return vote(event, this, "up")' href='vote?id=22897846&amp;how=up&amp;auth=f2e63e48e9e0d1fdcf28e42b663a0e586b67f28f&amp;goto=news'><div class='votearrow' title='upvote'></div></a>
#         </center>
#     </td>
#     <td class="title">
#         <a href="https://www.npr.org/2020/04/17/820707276/deep-sea-squid-communicate-by-glowing-like-e-readers" class="storylink">Deep Sea Squid Communicate by Glowing Like E-Readers</a>
#         <span class="sitebit comhead"> (<a href="from?site=npr.org"> <span class="sitestr">npr.org</span></a>) </span>
#     </td>
# </tr>
#
# <tr>
#     <td colspan="2"></td>
#     <td class="subtext">
#         <span class="score" id="score_22897846">77 points</span> by <a href="user?id=pseudolus" class="hnuser">pseudolus</a>
#         <span class="age"><a href="item?id=22897846">3 hours ago</a></span>
#         <span id="unv_22897846"></span> | <a href="flag?id=22897846&amp;auth=f2e63e48e9e0d1fdcf28e42b663a0e586b67f28f&amp;goto=news">flag</a> | <a href="hide?id=22897846&amp;auth=f2e63e48e9e0d1fdcf28e42b663a0e586b67f28f&amp;goto=news" onclick="return hidestory(event, this, 22897846)">hide</a> | <a href="item?id=22897846">24&nbsp;comments</a>
#     </td>
# </tr>
#
# <tr class="spacer" style="height:5px"></tr>

# ----------------------------------------------------------------------------
## INITIALIZATIONS:
## ----------------

import json
import re
import requests
from bs4 import BeautifulSoup
from operator import itemgetter

res = requests.get('https://news.ycombinator.com/news')
soup = BeautifulSoup(res.text, 'html.parser')
# print(soup)

athing = soup.select('.athing')
links = soup.select('.storylink')
subtext = soup.select('.subtext')

exclusions = ['dead', 'flagged', 'youtube', 'wikipedia']

# ----------------------------------------------------------------------------
## DATE, TIME:
## -----------

import datetime
from datetime import datetime
now = datetime.now()

## Get old_datetime:
try:
    with open('/tmp/old_date', 'r') as f:
        old_datetime_str = f.readline()
        ## Convert saved datetime string object back to datetime:
        old_datetime = datetime.strptime(old_datetime_str, '%Y-%m-%d %H:%M:%S')
except FileNotFoundError:
    old_datetime = now

## Save current datetime as old_datetime:
with open('/tmp/old_date', 'w') as f:
    ## writes datetime object to file as a str:
    f.write(now.strftime('%Y-%m-%d %H:%M:%S'))


def create_custom_hn(links, subtext):
    hn = []
    hn_base_url = 'https://news.ycombinator.com/item?id='
    # ----------------------------------------
    for idx, item in enumerate(links):
        # ----------------------------------------
        ## HN ID -- Hacker News item source ('comments') URL:
        ## -----------------------------------------
        ## https://stackoverflow.com/questions/51837685/get-the-numbers-within-the-following-html-tag-via-beautifulsoup
        ## https://stackoverflow.com/questions/24962673/beautiful-soup-getting-tag-id
        hn_id = athing[idx].get('id')
        hn_url = hn_base_url + hn_id
        # print('hn_id:', hn_id)
        # print('hn_url:', hn_url)
        # ----------------------------------------
        ## Title:
        ## ------
        title = links[idx].getText()
        # ----------------------------------------
        ## TARGET_URL:
        ## ----
        href = links[idx].get('href', None)
        # ----------------------------------------
        ## Points (votes):
        ## ---------------
        vote = subtext[idx].select('.score')
        try:
            points = int(re.sub(r' point.*', '', vote[0].getText()))
        except IndexError:
            pass
        # ----------------------------------------
        ## Comments:
        ## ---------
        hn_element = soup.select('td.subtext')
        hn_element_text = hn_element[idx].get_text()
        ## 107 points by pcr910303 2 hours ago  | hide | 52 comments 
        ## https://stackoverflow.com/questions/4666973/how-to-extract-the-substring-between-two-markers
        try:
            comments = re.search('hide \| (.+?)\scomment.*$', hn_element_text).group(1)
        except AttributeError:
            pass
        # ----------------------------------------
        ## Age:
        ## ----
        raw_age = subtext[idx].select('.age')
        age = raw_age[0].getText()
        #
        # ============================================================================
        ## SET MINIMUM {POINTS | COMMENTS} AND EXCLUSIONS HERE:
        ## ====================================================
        ## ----------------------------------------------------
        ## match: check for match only at beginning of string | search: check for match anywhere in string
        ## Use any of these:
        # if points > 100:
        # if int(comments) >= 100:
        # if (points > 100) and (int(comments) >= 100):
        ## https://stackoverflow.com/questions/2152898/filtering-a-list-of-strings-based-on-contents
        if (points > 5) and \
                (int(comments) > 1) and \
                (not [w for w in exclusions if w in title.lower()]) and \
                (not [w for w in exclusions if w in href.lower()]):
            hn.append({'title': title, 'hn_url': hn_url, 'ext_link': href, 'votes': points, 'comments': comments, 'age (h)': age})
    for i in hn:
        ## match: check for match only at beginning of string | search: check for match anywhere in string
        if re.search('minute', i['age (h)']):
            s = [int(s) for s in i['age (h)'].split() if s.isdigit()]
            age = s[0]/60.0
            i['age (h)'] = age
        elif re.search('hour', i['age (h)']):
            s = [int(s) for s in i['age (h)'].split() if s.isdigit()]
            age = s[0]
            i['age (h)'] = age
        elif re.search('day', i['age (h)']):
            s = [int(s) for s in i['age (h)'].split() if s.isdigit()]
            age = s[0]*24.0
            i['age (h)'] = age
        else:
            pass
    # ----------------------------------------
    ## Return:
    ## -------
    # print('hn:\n:', hn)
    return hn

hn_list = create_custom_hn(links, subtext)

# hn_list_sorted  = sorted(hn_list, key = itemgetter('age (h)'), reverse=True)
hn_list_sorted  = sorted(hn_list, key = itemgetter('age (h)'), reverse=True)
# print('\nhn_list_sorted:\n', hn_list_sorted)

print('\nOld date, time:', old_datetime)
print('           now:', now.strftime('%Y-%m-%d %H:%M:%S'))

## https://stackoverflow.com/questions/24217641/how-to-get-the-difference-between-two-dates-in-hours-minutes-and-seconds
date_diff = now - old_datetime

## AttributeError: 'datetime.timedelta' object has no attribute 'hours'
# print('date_diff.seconds:', date_diff.seconds)
date_diff_hours = date_diff.seconds / 3600

print(' date_diff (h): {:0.4f}'.format(date_diff_hours))
print()

## https://stackoverflow.com/questions/4110891/how-to-redirect-the-output-of-print-to-a-txt-file
## Write results to file (redirects all print statements):

import sys
with open('/mnt/Vancouver/programming/python/scripts/output/hn.txt', 'w') as f:
    """ mode='a' : append | "w" : overwrite
    """
    sys.stdout = f

    i = 0
    found = False
    for item in hn_list_sorted:
        # Since I run this script every 12 h (6 am/pm), regard "new" < 12h:
        # if float(item['age (h)']) < 12:
        if float(item['age (h)']) < 24:
            found = True
            break
        else:
            i += 1
    if found:
        for item in range(0, i):
            print(json.dumps(hn_list_sorted[item], indent=2))
        print('\n==============================================================================')
        print('Older results: {}'.format(old_datetime))
        print('==============================================================================\n')
        for item in range(i, len(hn_list_sorted)):
            print(json.dumps(hn_list_sorted[item], indent=2))
    else:
        ## All results are 'new,;' so print all of them:
        print(json.dumps(item, indent=2))

# ============================================================================
## POSTPROCESSING

""" Address various annoyances in JSON output ("hn.txt") file.

    ISSUE: it's difficult:

    1. to edit a file "in place" in Python (like the linux `sed -i ...` command)
       [two-step solution: open and read file; open and write file]; and

    2. to make multiple (different regex expressions) edits to multiple lines in that file
       [solution: create a dictionary of replacements; open file and make those substitutions;
        write those results to file].

    The "with open() as file:" expression, e.g.

        # https://stackoverflow.com/questions/4427542/how-to-do-sed-like-text-replace-with-python
        # Can't "rw" in one operation (open file), so do in two parts:

        with open('/mnt/Vancouver/programming/python/scripts/output/hn.txt', 'r') as f:
            lines = f.readlines()
        with open('/mnt/Vancouver/programming/python/scripts/output/hn.txt', 'w') as f:
            for line in lines:
                ## remove trailing commas at end of JSON output lines (interferes with Vim `gx` (open URL) command:
                f.write(re.sub(r',$', '', line))
        with open('/mnt/Vancouver/programming/python/scripts/output/hn.txt', 'w') as f:
            for line in lines:
                ## remove quotation marks:
                f.write(re.sub(r',"', '', line))

    ... which offers a potential solution, BUT it only reads through the file once (hence you cannot make multiple edits).  Without fancy manipulations (e.g. resetting the file pointer [file.seek(0)] or using a "while loop" to loop over the file multiple times ("while True do ...", e.g.  https://stackoverflow.com/questions/42211541/how-to-go-through-file-multiple-times-in-python), imo those are messy approaches.

    The solutions offered in (corresponding to items {1.|2.} above, provide an elegant, flexible solution:
        1. https://stackoverflow.com/questions/4427542/how-to-do-sed-like-text-replace-with-python
           https://stackoverflow.com/a/4427835/1904943

        2. https://stackoverflow.com/questions/15175142/how-can-i-do-multiple-substitutions-using-regex-in-python
           https://stackoverflow.com/a/15175239/1904943

    ... as implemented, below.
"""
# ----------------------------------------------------------------------------
## https://stackoverflow.com/questions/15175142/how-can-i-do-multiple-substitutions-using-regex-in-python

def multiple_replace(dict, text):
    # Create a regular expression  from the dictionary keys:
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
    # For each match, look-up corresponding value in dictionary:
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)

""" Use a dict to replace various annoyances in the "hn.txt" file generated by my "hn.py" script:

    * remove trailing commas at end of JSON output lines (interferes with Vim `gx` (open URL) command

    * remove the unicode (e.g. "smart quotes") generated by BeautifulSoup 4; e.g.:

        https://stackoverflow.com/questions/42444559/replace-all-smart-quotes-in-beautiful-soup
        https://stackoverflow.com/questions/24358361/removing-u2018-and-u2019-character
"""

hn_dict = {
         ',' : ''
        ,'"' : ''
        ,"\\u201c" : '"'
        ,"\\u201d" : '"'
        ,"\\u2018" : "'"
        ,"\\u2019" : "'"
        ,"\\u2013" : "-"
        }

with open('/mnt/Vancouver/programming/python/scripts/output/hn.txt', 'r') as f:
    new_text = multiple_replace(hn_dict, f.read())

with open('/mnt/Vancouver/programming/python/scripts/output/hn.txt', 'w') as f:
    f.write(new_text)

# ============================================================================
## RESET PRINT REDIRECTS:

## https://stackoverflow.com/questions/4110891/how-to-redirect-the-output-of-print-to-a-txt-file
sys.stdout = sys.__stdout__

# ============================================================================
