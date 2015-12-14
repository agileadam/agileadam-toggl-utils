# WARNING:

Feel free to use these scripts, but they're not very polished.
I've published them for a few co-workers and myself.

# Requirements:

1. Requests - http://docs.python-requests.org/en/latest/
1. A working Toggl account with a working API token

# The Utilities

Use --help with any utility to see documentation

## start-timer.py

1. Automatically creates the a project in Toggl (saving several steps) if it doesn't already exist
1. If a timer is already running when you start a new one, the running timer will stop and the new one will start.

Usage: `start-timer.py [-h] [-q] -w 123456 -p "Project name" -d "Time entry description"`

## stats.py

1. Shows a breakdown of time for each project in the current week (week goes from Monday to Sunday)
1. You can pass a "goal" option to work towards a specific goal

Usage: `stats.py [-h] -w 123456 [-g 35]`

# Setup

## Toggl configuration

1. Create `~/.togglrc` file: (use your own token)<pre>[toggl]<br/>token=e0926223d8c73bbe7ab136d042530d9a</pre>
