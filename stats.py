#!/usr/bin/env python

import json
import requests
import os
import ConfigParser
from datetime import datetime, date, timedelta
import argparse

parser = argparse.ArgumentParser(description='Reports time for a specific Workspace by project for the current week', version='1.0', add_help=True)
parser.add_argument('-w', '--wid', help='ID of the Toggl workspace', required=True, metavar='123456', type=int)
parser.add_argument('-g', '--goal', help='How many hours you\'d like to achieve this week', required=False, metavar='35', type=int)
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


def hhmmss(tdelta):
    minutes, seconds = divmod(tdelta.seconds + tdelta.days * 86400, 60)
    hours, minutes = divmod(minutes, 60)
    return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

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

today = date.today()
monday = today - timedelta(days=today.weekday())
timeslips = get_timeslips(workspace_id=str(args.wid), since=monday)

entries = {}
all_dur = 0
for entry in timeslips:
    project = entry["project"]
    dur = entry["dur"]

    if project not in entries:
        entries[project] = 0
    entries[project] += dur
    all_dur += dur

# Print summary
if args.goal:
    if all_dur:
        total_time_hhmmss = hhmmss(timedelta(milliseconds=all_dur))
        total_time = timedelta(hours=int(total_time_hhmmss[0:2]), minutes=int(total_time_hhmmss[3:5]), seconds=int(total_time_hhmmss[6:8]))
    else:
        total_time_hhmmss = "00:00:00"
        total_time = timedelta(hours=0, minutes=0, seconds=0)

    goal_time = timedelta(hours=args.goal)
    remaining_time = goal_time - total_time

    print "Goal:", hhmmss(goal_time)
    print "Total:", total_time_hhmmss

    if remaining_time.days < 0:
        print "Exceeded goal by:", hhmmss(total_time - goal_time)
    else:
        print "Remaining:", hhmmss(remaining_time)

    print ""

# Print projects
for project_name, dur in sorted(entries.iteritems()):
    print project_name, hhmmss(timedelta(milliseconds=dur))
