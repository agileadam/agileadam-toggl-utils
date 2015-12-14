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


def hhmmss(tdelta):
    minutes, seconds = divmod(tdelta.seconds + tdelta.days * 86400, 60)
    hours, minutes = divmod(minutes, 60)
    return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

def get_workspaces():
    return toggl_query('/workspaces', None, 'GET')

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
args.wid = str(args.wid)


today = date.today()
monday = today - timedelta(days=today.weekday())
result = report_query('/summary', {"workspace_id": args.wid, "since": monday})

# Print summary
if args.goal:
    if result["total_grand"]:
        total_time_hhmmss = hhmmss(timedelta(milliseconds=result["total_grand"]))
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
for project in result["data"]:
    print project["title"]["project"], hhmmss(timedelta(milliseconds=project["time"]))
