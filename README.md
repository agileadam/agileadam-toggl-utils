## WARNING:

Feel free to use these scripts, but they're not very polished.
I've published them for a few co-workers and myself.

## Requirements:

1. Requests - http://docs.python-requests.org/en/latest/
1. A working Toggl account with a working API token

## Setup:

1. Create `~/.togglrc` file: (use your own token)<pre>[toggl]<br/>token=e0926223d8c73bbe7ab136d042530d9a</pre>

## The Utilities:

Use --help with any utility to see documentation

### start-timer.py

Starts a timer in Toggl, creating a project if the project is not found

1. If a timer is already running when you start a new one, the running timer will stop and the new one will start.
1. Workspace ID (`-w`/`--wid`) is required
1. Project name (`-p`/`--project`) is required
1. Time entry description (`-d`/`--description`) is required
1. Quiet mode (`-q`/`--quiet`) will only show errors (useful for only showing an alert if there's a problem; works well with Alfred notifications)

Usage: `start-timer.py [-h] [-q] -w 123456 -p "Project name" -d "Time entry description"`

Example: `python start-timer.py -w 1214302 -p "internal-meetings" -d "Meeting with Bob Smith"`

### stats.py

Reports time for a specific Workspace by project for the current week

1. Workspace ID (`-w`/`--wid`) is required
1. You can pass a "goal" option (`-g`/`--goal`) to work towards a specific goal

Usage: `stats.py [-h] -w 123456 [-g 35]`

Example: `python stats.py -w 1214302 -g 35`
