#!/usr/bin/env python

import json
import argparse
import requests
import os
import ConfigParser

config = ConfigParser.RawConfigParser()
try:
    config.read(os.path.expanduser('~/.togglrc'))
    toggl_api_token = config.get('toggl', 'token')
except:
    raise UserWarning('Please create a ~/.togglrc file with your token. View README for setup instructions.')

parser = argparse.ArgumentParser(description='Starts a timer in Toggl, creating a project if the project is not found', version='1.0', add_help=True)
parser.add_argument('-q', '--quiet', help='Only show errors', dest='only_errors', action='store_true')
parser.add_argument('-w', '--wid', help='ID of the Toggl workspace', required=True, metavar='123456', type=int)
parser.add_argument('-p', '--project', help='Name of the project (url slug pattern is best)', required=True, metavar='"Project name"')
parser.add_argument('-d', '--description', help='Description for the time entry', required=True, metavar='"Time entry description"')
args = parser.parse_args()


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
        print "Error processing request"
        response.raise_for_status()

    return response.json()


def get_workspaces():
    return toggl_query('/workspaces', None, 'GET')


def get_workspace_projects(workspace_id):
    return toggl_query('/workspaces/' + workspace_id + '/projects', None, 'GET')


def create_project(project_name, workspace_id):
    project_data = {"name": project_name, 'wid': workspace_id}
    project_data_json = json.dumps({'project': project_data})
    return toggl_query('/projects', None, 'POST', project_data_json)


def get_running_timer():
    return toggl_query('/time_entries/current', None, 'GET')


def stop_timer(timer_id):
    return toggl_query('/time_entries/' + str(timer_id) + '/stop', None, 'PUT')


def start_timer(description, project_id):
    time_entry_data = {"description": description, 'pid': project_id, 'created_with': 'kmtoggl'}
    time_entry_data_json = json.dumps({'time_entry': time_entry_data})
    return toggl_query('/time_entries/start', None, 'POST', time_entry_data_json)


workspaces = get_workspaces()
workspace_found = False
for workspace in workspaces:
    if workspace['id'] == args.wid:
        workspace_found = True
        break

if not workspace_found:
    raise UserWarning('Could not find a Toggl workspace with this ID')

# Convert to a string
args.wid = str(args.wid)

# Build a dict of existing projects in this workspace
workspace_projects = get_workspace_projects(args.wid)
all_projects = {}
if workspace_projects:
    for project in workspace_projects:
        all_projects[project['name']] = project['id']
else:
    if not args.only_errors:
        print 'Did not find any existing projects in this Toggl workspace'

project_id = None
# Get a project ID for the time entry
if args.project in all_projects:
    project_id = all_projects[args.project]
else:
    # Create the project
    project = create_project(args.project, args.wid)
    project_id = project['data']['id']

if project_id is not None:
    # Get running time entry
    running_timer = get_running_timer()
    if running_timer['data'] is not None:
        stop_timer(running_timer['data']['id'])

    # Start a new time entry
    start_timer(args.description, project_id)
    if not args.only_errors:
        print "Started timer for", args.description, "in project", args.project

exit()
