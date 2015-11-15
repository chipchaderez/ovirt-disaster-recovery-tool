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
                     storage = params.Storage(type_=self.storageTypes.get_selected_objects()[0], 
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
            pass

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
	
    def onImportEntitesPopup(self):
        def on_ok():
            for x in range(0, 12):
	        form.templatesSlider.value += 1
                time.sleep(0.1)
                form.display()
            for x in range(0, 12):
                form.vmsSlider.value += 1
                time.sleep(0.1)
                form.display()
            for x in range(0, 12):
                form.disksSlider.value += 1
                time.sleep(0.1)
                form.display()
            
        def on_cancel():
            self.parentApp.setNextForm(None)

        form = npyscreen.ActionPopup(name='Import Entities', lines=20, columns=80)
        form.show_aty = 2
        form.on_ok = on_ok
        form.on_cancel = on_cancel

        form.error = form.add(npyscreen.FixedText, value='Select entities to import:', color='LABEL', editable=False)
        form.entites = form.add(npyscreen.MultiSelect, values=['Templates', 'VMs', 'Disks'], max_height=4, scroll_exit=True)
        form.templatesSlider = form.add(npyscreen.TitleSlider, out_of=12, name = "Templates", editable=False, rely=7)
        form.vmsSlider = form.add(npyscreen.TitleSlider, out_of=12, name = "VMs", editable=False, rely=9)
        form.disksSlider = form.add(npyscreen.TitleSlider, out_of=12, name = "Disks", editable=False, rely=11)

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
        self.templatesSlider = self.add(npyscreen.TitleSlider, out_of=12, name = "Templates", editable=False, hidden=True)
        self.vmsSlider = self.add(npyscreen.TitleSlider, out_of=12, name = "VMs", editable=False, hidden=True)
        self.disksSlider = self.add(npyscreen.TitleSlider, out_of=12, name = "Disks", editable=False, hidden=True)

    def beforeEditing(self):
        self.datacenters.values = self.getDCs()

    def getDCs(self):
        return list(map((lambda dc: dc.name), self.parentApp.api.datacenters.list('status=up')))

    def on_cancel(self):
        pass

    def on_ok(self):
        pass

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

            selectedObjects = self.parent.entities.get_selected_objects();
            if selectedObjects:
              if ('Templates' in selectedObjects):
                  self.parent.templatesSlider.hidden = False              
              if ('VMs' in selectedObjects):
                  self.parent.vmsSlider.hidden = False        
              if ('Disks' in selectedObjects):
                  self.parent.disksSlider.hidden = False

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
