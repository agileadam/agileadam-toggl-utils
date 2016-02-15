#!/usr/bin/env python

import json
import requests
import os
import ConfigParser
from datetime import datetime, date, timedelta
import argparse

parser = argparse.ArgumentParser(description='Reports time for a specific Workspace by project and task between two dates', version='1.0', add_help=True)
parser.add_argument('-w', '--wid', help='ID of the Toggl workspace', required=True, metavar='123456', type=int)
parser.add_argument('-s', '--start-date', help='Start date', required=True, metavar='YYYY-MM-DD')
parser.add_argument('-e', '--end-date', help='End date', required=True, metavar='YYYY-MM-DD')
parser.add_argument('-d', '--decimal-only', help='Show only decimal values', required=False, action='store_true')
parser.add_argument('-t', '--totals-only', help='Show only total values (so exclude tasks)', required=False, action='store_true')
args = parser.parse_args()

config = ConfigParser.RawConfigParser()
try:
    config.read(os.path.expanduser('~/.togglrc'))
    toggl_api_token = config.get('toggl', 'token')
except:
    raise UserWarning('Please create a ~/.togglrc file with your token. View README for setup instructions.')


def toggl_query(url, params, method, payload=None):
    api_url = 'https://www.toggl.com/api/v8' + url
    auth = (toggl_api_token, 'api_token')
    headers = {'content-type': 'application/json'}

    if method == "POST":
        response = requests.post(api_url, auth=auth, headers=headers, params=params, data=payload)
    elif method == "PUT":
        response = requests.put(api_url, auth=auth, headers=headers, params=params)
    elif method == "GET":
        response = requests.get(api_url, auth=auth, headers=headers, params=params)
    else:
        raise UserWarning('GET, POST and PUT are the only supported request methods.')

    # If the response errored, raise for that.
    if response.status_code != requests.codes.ok:
        response.raise_for_status()

    return response.json()


def report_query(url, params):
    api_url = 'https://toggl.com/reports/api/v2' + url
    auth = (toggl_api_token, 'api_token')
    headers = {'content-type': 'application/json'}
    params['user_agent'] = "agileadam toggl utils - stats.py"
    response = requests.get(api_url, auth=auth, headers=headers, params=params)

    # If the response returned an error, raise for it.
    if response.status_code != requests.codes.ok:
        response.raise_for_status()

    return response.json()


def get_workspaces():
    return toggl_query('/workspaces', None, 'GET')


def get_timeslips_query(**kwargs):
    params = {
        'grouping': 'users',
        'subgrouping': 'projects',
        'order_field': 'date',
    }

    for key in kwargs:
        if not params.get(key):
            params[key] = kwargs.get(key)

    response = report_query("/details", params)

    return response


def get_timeslips(**kwargs):
    timeslips = []
    response = get_timeslips_query(**kwargs)
    data = response['data']
    per_page = response['per_page']
    total_count = response['total_count']

    if data:
        for row in data:
            timeslips.append(row)

    if total_count > per_page:
        # There are more records than can be returned in one go-round.
        total_pages = total_count / per_page
        if total_count % per_page:
            total_pages += 1

        for current_page in range(total_pages):
            page = current_page + 1
            if page > 1:
                response = get_timeslips_query(page=page, **kwargs)
                data = response['data']
                if data:
                    for row in data:
                        timeslips.append(row)

    return timeslips


def hhmm(tdelta):
    minutes, seconds = divmod(tdelta.seconds + tdelta.days * 86400, 60)
    hours, minutes = divmod(minutes, 60)
    return '{:02d}:{:02d}h'.format(hours, minutes)


def hours(ms):
    hours = ms / 1000 / 3600.0
    return '{0:.2f}'.format(hours)

workspaces = get_workspaces()
workspace_found = False
for workspace in workspaces:
    if workspace['id'] == args.wid:
        workspace_found = True
        print workspace['name']
        print ""
        break

if not workspace_found:
    raise UserWarning('Could not find a Toggl workspace with this ID')

# Convert to a string
timeslips = get_timeslips(workspace_id=str(args.wid), since=args.start_date, until=args.end_date)

entries = {}

# Print projects
for entry in timeslips:
    start_day = str(entry["start"])[0:10]
    project = entry["project"]
    task = entry["description"]
    dur = entry["dur"]

    if start_day not in entries:
        entries[start_day] = {}
    if project not in entries[start_day]:
        entries[start_day][project] = {}
    if task not in entries[start_day][project]:
        entries[start_day][project][task] = 0
    entries[start_day][project][task] += dur

all_dur = 0
for day_key, day_value in sorted(entries.iteritems()):
    this_day_dur = 0
    print day_key
    for project_name, project_tasks in day_value.iteritems():
        this_project_dur = 0
        print "     " + project_name
        for task, dur in project_tasks.iteritems():
            this_project_dur += dur
            this_day_dur += dur
            all_dur += dur
            t = timedelta(milliseconds=dur)
            if not args.totals_only:
                if args.decimal_only:
                    print "         " + task + " " + hours(dur) + "h"
                else:
                    print "         " + task + " " + hhmm(t) + " [" + hours(dur) + "h]"
        project_t = timedelta(milliseconds = this_project_dur)
        if args.decimal_only:
            print "         PROJECT TOTAL: " + hours(this_project_dur) + "h"
        else:
            print "         PROJECT TOTAL: " + hhmm(project_t) + " [" + hours(this_project_dur) + "h]"
        print
    day_t = timedelta(milliseconds = this_day_dur)
    if args.decimal_only:
        print "     DAY TOTAL: " + hours(this_day_dur) + "h"
    else:
        print "     DAY TOTAL: " + hhmm(day_t) + " [" + hours(this_day_dur) + "h]"
    print

all_t = timedelta(milliseconds = all_dur)
if args.decimal_only:
    print "ALL TOTAL: " + hours(all_dur) + "h"
else:
    print "ALL TOTAL: " + hhmm(all_t) + " [" + hours(all_dur) + "h]"
