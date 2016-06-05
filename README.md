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

> *Before starting to recover the old oVirt setup, please make sure that the new oVirt engine is up and running
> and it contains an active data center.*

After ovirt-engine-sdk-python is installed, run disaster-recovery-tool.py from the project home folder to start:
![run python script](/sources/run_python.png)

The first screen after the welcome screen should be the login page.
At this page you should define the address of your engine, the user name to login to it, and the password.
![run python script](/sources/login_page.png)

Once logged in, the first page that will be displayed will be the import storage domain page:
![run python script](/sources/import_storage_domain.png)

At this page, the admin should decide which storage domain to import to the new data center.
The admin should pick the storage domain type, the export path, the host to perform the connect operations as part of the import process, and the name of the imported storage domain in the new data center.
![run python script](/sources/import_sd_on_progress.png)

Once the storage domain will finish to be imported, a pop-up will be performed to the admin, asking if there is another storage domain to import to the new data center.
![run python script](/sources/import_succeeded_any_more_question.png)

Once all the storage domains will finish to be import, the process of registering all the entities (VM/Templates) will start.
![run python script](/sources/Register_all_unregistered_entities.png)

The admin will choose the type of entities to register, it could be disks, Templates or VMs.
Each entity registration, will be performed under the scroll, indicating whether the registration finished with success or failure.
![run python script](/sources/Register_on_progress.png)

__That is it!!__

The new data center should now contain all the imported storage domains and VMs/Templates/Disks from your old setup which was destroyed.

Here is a short video demonstrating the flow which described above:
[![DR_video](/sources/thumb_video.png)](https://www.youtube.com/embed/2QoGfYjTNf0)

## Troubleshoot

* If python fails to run, please make sure ovirt-release repo and ovirt-engine-sdk-python is installed.
* If the data center fails to import a storage domain, please make sure the setup is running and the data center is active with an active SPM host.

## Additional

RATATUI is an open source project written with python and integrates with oVirt using ovirt-engine-sdk
The tool should support import of storage domains (currently only NFS) to a pre-initialized active data center and register all the entities (Templates, VMs and floating disks) using one simple operation.

## Future Work

Support import of block storage domain (iSCSI or FC)

## Contact
Please feel free to contact Maor Lipchuk (mlipchuk@redhat.com) or Daniel Erez (derez@redhat.com) on any question
