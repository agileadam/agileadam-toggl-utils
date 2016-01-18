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

### time_by_day_project_task.py

Reports time for a specific Workspace by day, by project, and by task (as a tree)

1. Workspace ID (`-w`/`--wid`) is required
1. Start date (`-s`/`--start-date`) is required
1. End date (`-e`/`--end-date`) is required

Usage: `time_by_day_project_task.py [-h] [-v] -w 123456 -s YYYY-MM-DD -e YYYY-MM-DD`

Example: `python time_by_day_project_task.py -w 1214302 -s 2016-01-11 -e 2016-01-17`

Output Example:

```
2016-01-15
     my-first-project
         Project management 02:12h [2.21h]
         PROJECT TOTAL: 02:12h [2.21h]

     my-second-project
         #4641522 Redirect issues 02:40h [2.67h]
         PROJECT TOTAL: 02:40h [2.67h]

     DAY TOTAL: 04:52h [4.88h]

2016-01-16
     my-second-project
         Development 00:29h [0.48h]
         Unit testing 02:36h [2.60h]
         PROJECT TOTAL: 03:05h [3.09h]

     DAY TOTAL: 03:05h [3.09h]

ALL TOTAL: 7:57h [7.97h]
```