import npyscreen
import json

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
        self.error = self.add(npyscreen.FixedText, value='', color='CRITICAL', editable=False, rely=22)
        self.success = self.add(npyscreen.FixedText, value='', color='VERYGOOD', editable=False, rely=22)
    
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
        self.parentApp.setNextForm(None)

    def on_ok(self):
        api = self.parentApp.api
        param = params.StorageDomain(name=self.storageName.value,
                     type_='data',
                     host=api.hosts.get(name=self.hosts.get_selected_objects()[0]),
                     storage = params.Storage(type_=self.storageTypes.get_selected_objects()[0], 
                                   address=self.url.value.split(':')[0],
                                   path=self.url.value.split(':')[1]))
        try:
            api.storagedomains.add(param)
            self.error.value = ''
            self.success.value = 'The storage domain has been imported successfully!'
        except Exception as e:
            self.success.value = ''
            if hasattr(e, 'detail'):
                self.error.value = 'Error: ' + e.detail
            else:
                self.error.value = 'Error: %s' % e


class MyApplication(npyscreen.NPSAppManaged):
    TITLE = 'oVirt Disaster Recovery Tool'
    api = None

    def onStart(self):
       self.addForm('MAIN', connectForm, name=self.TITLE)
       self.addForm('import_storage', importStorageForm, name=self.TITLE)

if __name__ == '__main__':
    TestApp = MyApplication().run()
