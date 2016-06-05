# rata-TUI: oVirt Disaster Recovery Tool
A text user interface tool designed for [oVirt](https://www.ovirt.org/) to manage disaster recovery scenrios in an easy and intuitive way.

![rata-TUI home scrreen logo](/sources/rata-TUI_home_screen.png)

## SETUP
If you are using a fresh install of a Linux distribution, please make sure you have the
oVirt repository configured:

> yum install [http://resources.ovirt.org/pub/yum-repo/ovirt-release36.rpm](http://resources.ovirt.org/pub/yum-repo/ovirt-release36.rpm)

Then you need to install the ovirt-engine-sdk-python package:

> yum install ovirt-engine-sdk-python

## USAGE

> *Before starting to recover the old oVirt setup, please make sure that your new oVirt engine is up and running
> and it contains an active Data Center.*

After ovirt-engine-sdk-python is installed, run disaster-recovery-tool.py from the project home folder to start:

![run python script](/sources/run_python.png)



rata-TUI is an open source project utility for oVirt Disaster Recovery.
RATATUI is an open source project written with python and integrates with oVirt using ovirt-engine-sdk
The tool should support import of Storage Domains (currently only NFS) to a pre-initialized active Data Center and register all the entities (Templates, VMs and floating disks) using one simple operation.

The following is a link for a demo video:
https://youtu.be/2QoGfYjTNf0
