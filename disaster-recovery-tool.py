import npyscreen
import json
import time

from ovirtsdk.api import API
from ovirtsdk.xml import params

class connectForm(npyscreen.ActionForm):
    def on_ok(self):
        try:
            self.connect()
            self.parentApp.setNextForm('import_storage')
        except Exception as e:
            if hasattr(e, 'reason'):
            	self.error.value = 'Connection Error: ' + e.reason
	    else:
		self.error.value = 'Error: %s' % e

    def on_cancel(self):
        self.parentApp.setNextForm(None)

    def create(self):       
        self.restapi = self.add(npyscreen.FixedText, value='REST-API Configuration:', editable=False)
        self.url = self.add(npyscreen.TitleText, name='Address', value='http://127.0.0.1:8080/ovirt-engine/api')
        self.username = self.add(npyscreen.TitleText, name='Username', value='admin@internal')
        self.password = self.add(npyscreen.TitlePassword, name='Password', value='')
        self.error = self.add(npyscreen.FixedText, value='', color='CRITICAL', editable=False)

    def connect(self):
       self.parentApp.api = API(url=self.url.value, username=self.username.value, password=self.password.value)

class importStorageForm(npyscreen.ActionForm):
    def create(self):
        self.FileStorageTypes = ['NFS', 'POSIXFS', 'GLUSTERFS', 'LOCALFS']
        self.BlockStorageType = ['ISCSI', 'FCP']

        self.importTitle = self.add(npyscreen.FixedText, value='Import Storage Domain:', editable=False)
        self.storageName = self.add(npyscreen.TitleText, name='Domain Name')
        self.datacenters = self.add(self.DCsTitleSelectOne, scroll_exit=True, name='Data Center', max_height=3)
        self.hosts = self.add(self.HostsTitleSelectOne, scroll_exit=True, name='Hosts', max_height=3, rely=8)
        self.storageTypes = self.add(self.StorageTypeSelectOne, scroll_exit=True, name='Storage Type', max_height=4, rely=12,
                                    values=self.FileStorageTypes+self.BlockStorageType, hidden=True)
        self.url = self.add(npyscreen.TitleText, name='Export Path', hidden=True, value='FQDN:/path', rely=17)
        self.warn = self.add(npyscreen.FixedText, value='Please wait. The operation might take several minutes.', hidden=True,
                             rely=20, editable=False, color='CAUTIONHL')

    def beforeEditing(self):
        self.datacenters.values = self.getDCs()

    def getDCs(self):        
        return list(map((lambda dc: dc.name), self.parentApp.api.datacenters.list('status=up')))

    class DCsTitleSelectOne(npyscreen.TitleSelectOne): 
        def when_value_edited(self):
            selectedObjects = self.parent.datacenters.get_selected_objects();
            if len(selectedObjects) != 0:		
	       dcName = selectedObjects[0]
               self.parent.hosts.values = list(map((lambda host: host.name), 
                   self.parent.parentApp.api.hosts.list('datacenter=%s status=up' % dcName)))
            self.parent.hosts.update()

    class HostsTitleSelectOne(npyscreen.TitleSelectOne):
        def when_value_edited(self):
            selectedObjects = self.parent.hosts.get_selected_objects();
            if len(selectedObjects) != 0:
              self.parent.storageTypes.hidden = False
              self.parent.storageTypes.update()


    class StorageTypeSelectOne(npyscreen.TitleSelectOne):
        def when_value_edited(self):
            selectedObjects = self.parent.storageTypes.get_selected_objects();
            if len(selectedObjects) != 0:               
               storageType = selectedObjects[0]
               if (storageType in self.parent.FileStorageTypes):
                   self.parent.url.hidden = False
                   self.parent.url.update()
               else:
                   self.parent.url.hidden = True
                   self.parent.url.update()

    def on_cancel(self):
        self.parentApp.setNextForm('import_entities')        

    def on_ok(self):
        self.warn.hidden=False
        self.display()
        api = self.parentApp.api
        param = params.StorageDomain(name=self.storageName.value,
                     type_='data',
                     host=api.hosts.get(name=self.hosts.get_selected_objects()[0]),
                     storage = params.StorageConnection(type_=self.storageTypes.get_selected_objects()[0],
                                   address=self.url.value.split(':')[0],
                                   path=self.url.value.split(':')[1]))
        try:            
            sd = api.storagedomains.add(param)
            api.datacenters.get(self.datacenters.get_selected_objects()[0]).storagedomains.add(sd)
            self.warn.hidden=True
            self.display()
            self.onImportPopup('Success', 'The storage domain has been imported successfully!', None)
        except Exception as e:
            if hasattr(e, 'detail'):
                error = 'Error: ' + e.detail
            else:
                error = 'Error: %s' % e
            self.onImportPopup('Error', None, error)

    def onImportPopup(self, title, success, error):
        def on_ok():
            pass

        def on_cancel():
            self.parentApp.setNextForm('import_entities')

        form = npyscreen.ActionPopup(name=title, lines=9, columns=80)
        form.show_aty = 7
        form.OK_BUTTON_TEXT = 'Yes'
        form.CANCEL_BUTTON_TEXT = 'No'
        form.on_ok = on_ok
        form.on_cancel = on_cancel

        if (success != None):
            form.success = form.add(npyscreen.FixedText, value=success, color='VERYGOOD', editable=False, rely=2)            
        else:        
	    form.error = form.add(npyscreen.FixedText, value=error, color='CRITICAL', editable=False, rely=2)

        label = form.add_widget(npyscreen.FixedText, value='Do you want to import additional storage domains?',
                                color='CONTROL', editable=0, rely=5)
        action = form.edit()
        return action
	
class importEntitiesForm(npyscreen.ActionForm):
    def create(self):
        self.importTitle = self.add(npyscreen.FixedText, value='Import Entites:', editable=False)
        self.datacenters = self.add(self.DCsTitleSelectOne, scroll_exit=True, name='Data Center', max_height=3)
        self.clusters = self.add(self.ClustersTitleSelectOne, scroll_exit=True, name='Clusters', max_height=3, rely=7)
        
        self.label = self.add(npyscreen.FixedText, value='Select entities to import:', editable=False, rely=11)
        self.entities = self.add(self.EntitiesMultiSelect, values=['Templates', 'VMs', 'Disks'],
                                 max_height=4, scroll_exit=True, hidden=True)
        self.templatesSlider = self.add(npyscreen.TitleSlider, name = "Templates", out_of=100, editable=False, label=True, hidden=True, rely=18)
        self.template_import = self.add(npyscreen.FixedText, value='', editable=False, rely=19, hidden=True)
        self.vmsSlider = self.add(npyscreen.TitleSlider, name = "VMs", out_of=100, editable=False, hidden=True, rely=21)
        self.vm_import = self.add(npyscreen.FixedText, value='', editable=False, rely=22, hidden=True)
        self.disksSlider = self.add(npyscreen.TitleSlider, name = "Disks", out_of=100, editable=False, hidden=True, rely=24)
        self.disk_import = self.add(npyscreen.FixedText, value='', editable=False, rely=25, hidden=True)

    def beforeEditing(self):
        self.datacenters.values = self.getDCs()

    def getDCs(self):
        return list(map((lambda dc: dc.name), self.parentApp.api.datacenters.list('status=up')))

    def on_cancel(self):
        self.parentApp.setNextForm(None)

    def on_ok(self):
        api = self.parentApp.api
        cluster_ = api.clusters.get(self.clusters.get_selected_objects()[0])
        dc_name_ = self.datacenters.get_selected_objects()[0]
        unreg_templates = set()
        unreg_vms = set()
        unreg_disks = list()
        for storageDomain in api.storagedomains.list('datacenter=%s status=active' % dc_name_):
            if (self.templatesSlider.hidden == False):
                self.template_import.value="Fetching unregistered templates from storage domain %s..." % storageDomain.name
                self.display()
                for template_per_domain in storageDomain.templates.list(unregistered=True):
                    unreg_templates.add(template_per_domain)
                self.template_import.value="Finished fetcihng unregistered templates from storage domain %s." % storageDomain.name
                self.display()
            if (self.vmsSlider.hidden == False):
                self.vm_import.value="Fetching unregistered VMs from storage domain %s..." % storageDomain.name
                self.display()
                for vm_per_domain in storageDomain.vms.list(unregistered=True):
                    unreg_vms.add(vm_per_domain)
                self.vm_import.value="Finished fetcihng unregistered VMs from storage domain %s." % storageDomain.name
                self.display()
            if (self.disksSlider.hidden == False):
                self.disk_import.value="Fetching unregistered disks from storage domain %s..." % storageDomain.name
                self.display()
                for disk in storageDomain.disks.list(unregistered=True):
                    unreg_disks.append(disk)
                self.vm_import.value="Finished fetcihng unregistered disks from storage domain %s." % storageDomain.name
                self.display()

        self.disk_import.value=""
        self.vm_import.value=""
        self.template_import.value=""
        self.display()
        if len(unreg_templates) == 0:
            self.template_import.value="No Templates to Register"
            self.template_import.color='VERYGOOD'
            self.display()
        else:
            unreg_template_index=1
            for unreg_template in unreg_templates:
                self.template_import.value="Register template name: " + unreg_template.name
                self.templatesSlider.value=unreg_template_index*(100/len(unreg_templates))
                self.template_import.color='VERYGOOD'
                unreg_template_index+=1
                self.display()
                try:
                    unreg_template.register(params.Action(cluster=cluster_))
                except Exception as e:
                    self.template_import.value="%s failed to register. Exception is: %s" % (unreg_template.name, e.detail)
                    self.template_import.color='CRITICAL'
                    self.display()
                    time.sleep(5)
            self.template_import.value="Finished templates registration"
            self.template_import.color='VERYGOOD'
            self.display()

        if len(unreg_vms) == 0:
            self.vm_import.value="No VMs to Register"
            self.vm_import.color='VERYGOOD'
            self.display()
        else:
            unreg_vm_index=1
            for unreg_vm in unreg_vms:
                self.vm_import.value="Register VM name: " + unreg_vm.name
                self.vm_import.color='VERYGOOD'
                self.vmsSlider.value=unreg_vm_index*(100/len(unreg_vms))
                unreg_vm_index+=1
                self.display()
                try:
                    unreg_vm.register(params.Action(cluster=cluster_))
                except Exception as e:
                    self.vm_import.value="%s failed to register. Exception: %s" % (unreg_vm.name, e.detail)
                    self.vm_import.color='CRITICAL'
                    self.display()
                    time.sleep(5)
            self.vm_import.value="Finished VMs registration"
            self.vm_import.color='VERYGOOD'
        unreg_disk_index=1
        for unreg_disk in unreg_disks:
            self.disk_import.value="Register disk name: " + unreg_disk.name
            self.disksSlider.value=unreg_disk_index*(100/len(unreg_disks))
            unreg_disk_index+=1
            self.display()
            unreg_disk.register()


    class DCsTitleSelectOne(npyscreen.TitleSelectOne):
        def when_value_edited(self):
            selectedObjects = self.parent.datacenters.get_selected_objects();
            if len(selectedObjects) != 0:
               dcName = selectedObjects[0]
               self.parent.clusters.values = list(map((lambda cluster: cluster.name),
                   self.parent.parentApp.api.clusters.list('datacenter=%s' % dcName)))
            self.parent.clusters.update()

    class ClustersTitleSelectOne(npyscreen.TitleSelectOne):
        def when_value_edited(self):
            selectedObjects = self.parent.clusters.get_selected_objects();
            if len(selectedObjects) != 0:
              self.parent.entities.hidden = False
              self.parent.entities.update()

    class EntitiesMultiSelect(npyscreen.MultiSelect):
        def when_value_edited(self):
            self.parent.templatesSlider.hidden = True
            self.parent.vmsSlider.hidden = True
            self.parent.disksSlider.hidden = True
            self.parent.template_import.hidden = True
            self.parent.vm_import.hidden = True
            self.parent.disk_import.hidden = True

            selectedObjects = self.parent.entities.get_selected_objects();
            if selectedObjects:
              if ('Templates' in selectedObjects):
                  self.parent.templatesSlider.hidden = False
                  self.parent.template_import.hidden = False
              if ('VMs' in selectedObjects):
                  self.parent.vmsSlider.hidden = False
                  self.parent.vm_import.hidden = False
              if ('Disks' in selectedObjects):
                  self.parent.disksSlider.hidden = False
                  self.parent.disk_import.hidden = False
            self.parent.templatesSlider.update()
            self.parent.vmsSlider.update()
            self.parent.disksSlider.update()

class MyApplication(npyscreen.NPSAppManaged):
    TITLE = 'oVirt Disaster Recovery Tool'
    api = None

    def onStart(self):
       self.addForm('MAIN', connectForm, name=self.TITLE)
       self.addForm('import_storage', importStorageForm, name=self.TITLE)
       self.addForm('import_entities', importEntitiesForm, name=self.TITLE)

if __name__ == '__main__':
    TestApp = MyApplication().run()
