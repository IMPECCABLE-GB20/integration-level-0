# Integration Level 0

Assumptions:

* All workflows execute on Summit.
* Each workflow executes on dedicated computing resources.

Current workflow implementations:

* Stand-alone Python applications.
* May require command line parameters.
* May require dedicated config files.
* Encode resource requests.
* Defines I/O paths.

Requirements:

* Execute each workflow in an arbitrary sequence on Summit.
* Each workflow submits a batch job and executes on a dedicated pilot.
* Each workflow reads/writes from/to the same shared filesystem.
* Create a framework for Level 1 and 2.

Implementation:

The current implementation offers a place where to unify workflow and resource configs across workflows. Ready for subprocess execution.

* Edit `gb20-covid19-0.json`
* execute `gb20-covid19-0.py`