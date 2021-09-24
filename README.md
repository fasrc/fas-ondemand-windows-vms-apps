# FAS OnDemand Windows VMs Apps

This repository contains course-specific  Windows VM applications for Open OnDemand defined in a declarative configuration and programmatically generated. 

The [fas-ondemand-windows-vms](https://github.com/fasrc/fas-ondemand-windows-vms.git) repo is used as a base for all apps.

## Adding new apps

1. Add a new entry to `apps.json` (see examples).
2. Run the `update.py` script to create the app folder(s).
3. Commit and push the changes.

Notes:
- Existing apps will not be modified by the process above. This merely bootstraps new apps from a template repo. They can be modified manually from that point. Or you can start over by deleting the app folder and running the update process again.

