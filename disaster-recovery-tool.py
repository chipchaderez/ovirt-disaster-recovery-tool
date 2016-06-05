import npyscreen
import json
import time

from ovirtsdk.api import API
from ovirtsdk.xml import params

class startForm(npyscreen.Form):
    # This is the welcome page, presenting an ASCII picture. No interesting logic here.
    def create(self):
        self.add(npyscreen.MultiLineEdit, value="888b.    db    88888    db         88888 8    8 888                                                                                                                \n8  .8   dPYb     8     dPYb          8   8    8  8                                                                                                                 \n8wwK'  dPwwYb    8    dPwwYb  wwww   8   8b..d8  8                                                                                                                 \n8  Yb dP    Yb   8   dP    Yb        8   `Y88P' 888                                                                                                                \n                                                                                                                                                                   \n88888              w      8    8                    888        w               d8b                     d8b                     Yb    dP w       w      888b. 888b. \n  8   .d88b Yb dP w8ww    8    8 d88b .d88b 8d8b     8  8d8b. w8ww .d88b 8d8b  8'  .d88 .d8b .d88b     8'  .d8b. 8d8b    .d8b.  Yb  dP  w 8d8b w8ww    8   8 8  .8 \n  8   8.dP'  `8.   8      8b..d8 `Yb. 8.dP' 8P       8  8P Y8  8   8.dP' 8P   w8ww 8  8 8    8.dP'    w8ww 8' .8 8P      8' .8   YbdP   8 8P    8      8   8 8wwK' \n  8   `Y88P dP Yb  Y8P    `Y88P' Y88P `Y88P 8       888 8   8  Y8P `Y88P 8     8   `Y88 `Y8P `Y88P     8   `Y8P' 8       `Y8P'    YP    8 8     Y8P    888P' 8  Yb ", rely=3, relx=10, editable=False)
        self.add(npyscreen.MultiLineEdit, editable=False, value = "                                                                                                   \n                                                                 /((,                              \n                                                                (((((                              \n                                                               .((##(*           ..                \n                                                               .((##(/( ,((##(#/*((//              \n                                                                ,(####((#/,#.#(*.#**,              \n                                                                  ,%##(##(/(%%%%% %*,              \n                                                                 .(%&&&%((#(#####(//*              \n                           /*,                                   *%%&&&&%#####(//////              \n                        *%%##(&*/(((*                           .%%%&&&&#%%%&&%(#%/              \n                        %#.(**(#####%(///.                     *#%%%&&&&&%@/%%&%###(               \n                .****/##&%//(((###%%&%//*                     ,#%%&&&&&&&&&&%%%%%#%*               \n                /****/(%%%#########%%&    ,                  (%%&&&(##&&&&&%%%%%###*               \n                 /****/%%%&&%%%%%%%%.  /***,               .##%%&&%*/%&%&&%%%%%%###(.              \n                    ,/&&&&%&##/      *,(*.              .###%%%,,,#%&&&%%%%#%####.             \n                    .&&&&%%%&&&%/*     //*               ,#%##%%%%%%%######%%########(           \n                     #%&&&%%##(#(((#((((##.               ,%%%%%%%%&&%((#########%%%&%#(/            \n                 /%%%%%%#######(((##%%,                ,##%##%%%%##((########(***/####/            \n               ,%%&%%%#####((((#(/.                    (%#(((########(##((####%*(#((///,           \n              /&&&%%%%%#%###((.                       /#%###########((###((((((((/((//((*          \n             *%%&%%%%#%####((*                       ,%%#%%%%%#%##%####(/(((((/(**/(/(((##         \n            #&&&&&&&%%/*###(//                       #%%%%%%&%%%%%%%%%#####((/(((((/((####(.       \n           ,&&&&&&&&%%(**#(((*                      *%%%&%&&&%%%&%%%#%#%###(#(((/((#(/#####/       \n           /&&&&&%%%#((((((/(/                      *%%&&%&&%&&&&%&%%%#%%###(#######(((####(,      \n           ,&&&%%%%%(((((((///.                     #%&&&%%%&%&&&&&&&&&&%%%%%#%##%%%%/&/*###/      \n           .%&%%%###(((((/(///*                     *%%&&%%%&&%%(*&(*&&&&&&&&&%&%%&&&(/#(#/#(      \n            (&%%%#((/(((((((((*             ,(#%#(/**#%&%&&%&&&&%(*#/&&&&&&&&&&&&&&&@/((##,      \n       .*(((#&&%##((/((##(####*           ,/         ./%%&%&&&&/,,/&&&&&&&&&&&&&&@&%(*##%(       \n.,*/*.      ./%&%###%######%#**,......       ,*/.      ,#&&&&&&&&&%,,&&&&&&&&&&&@@@@&(*%%(.....    \n,*,            *#(*(*/,..........                        .*#&%&&&&&%,***,,,,,,,,,,,,#/,,,,,,,,...  ", rely=17, relx=42)

    def adjust_widgets(self):
        self.parentApp.setNextForm('start_page')


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


    def reset(self):
        self.templatesSlider.hidden = True
        self.vmsSlider.hidden = True
        self.disksSlider.hidden = True
        self.template_import.hidden = True
        self.vm_import.hidden = True
        self.disk_import.hidden = True
        self.disk_import.value = ""
        self.vm_import.value = ""
        self.template_import.value = ""
        self.beforeEditing()
        self.clusters.hidden = True

    def onRegisterPopup(self):
        def on_ok():
            self.reset()
            self.display()

        def on_cancel():
            self.parentApp.setNextForm(None)

        form = npyscreen.ActionPopup(name="All the entities for the Data Center has been registered", lines=9, columns=80)
        form.show_aty = 7
        form.show_atx = 45
        form.OK_BUTTON_TEXT = 'Yes'
        form.CANCEL_BUTTON_TEXT = 'No'
        form.on_ok = on_ok
        form.on_cancel = on_cancel
        label = form.add_widget(npyscreen.FixedText, value='Do you want to register entities from another Data Center?',
                                color='CONTROL', editable=0, rely=3)
        action = form.edit()
        return action

    def beforeEditing(self):
        self.datacenters.values = self.getDCs()

    def getDCs(self):
        return list(map((lambda dc: dc.name), self.parentApp.api.datacenters.list('status=up')))

    def on_cancel(self):
        self.parentApp.setNextForm(None)

    def _aggragte_entities(self, slider, slider_text, entity, storage_domain, unreg_entities):
        if (slider.hidden == False):
            slider_text.value="Fetching unregistered %s from Storage Domain %s..." % (entity, storage_domain.name)
            slider_text.update()
            for entity_per_domain in getattr(storage_domain, entity).list(unregistered=True):
                unreg_entities.add(entity_per_domain)
            slider_text.value="Finished fetching unregistered %s from storage domain %s." % (entity, storage_domain.name)
            slider_text.update()

    def _reset_slider_texts(self):
        self.disk_import.value=""
        self.vm_import.value=""
        self.template_import.value=""
        self.display()

    def _update_slider_text(self, slider, slider_text, entity_type, entity, size, ind, prefix):
        slider_text.value="%sRegister %s name: %s" % (prefix, entity_type, entity.name)
        slider_text.color='VERYGOOD'
        slider.value=ind*(100/size)
        self.display()

    def _handle_exception(self, slider_text, entity, e):
        slider_text.value="%s failed to register. Exception is: %s" % (entity.name, e.detail)
        slider_text.color='CRITICAL'
        self.display()
        time.sleep(5)

    def _finish_registration(self, slider, slider_text, entity_type):
        slider_text.value="Finished %ss registration" % entity_type
        slider_text.color='VERYGOOD'
        slider.value=100
        self.display()

    def _register_entities(self, _cluster, entities, slider, slider_text, entity_type):
        if not entities:
            slider_text.value="No %ss to register" % entity_type
            slider_text.color='VERYGOOD'
            slider_text.update()
        else:
            ind=1
            for entity in entities:
                self._update_slider_text(slider, slider_text, entity_type, entity, len(entities), ind, "")
                ind+=1
                try:
                    entity.register(params.Action(cluster=_cluster))
                except Exception as e:
                    self._handle_exception(slider_text, entity, e)
            self._finish_registration(slider, slider_text, entity_type)

    def _register_disks(self, active_sds):
        if (self.disksSlider.hidden == False):
            for storageDomain in active_sds:
                unreg_disks=storageDomain.disks.list(unregistered=True)
                self.disksSlider.value=0
                self.disk_import.value="Storage register disks from storage %s" % storageDomain.name
                self.disksSlider.update()
                self.disk_import.update()
                ind=1
                for disk_per_domain in unreg_disks:
                    self._update_slider_text(self.disksSlider, self.disk_import, "disk", disk_per_domain, len(unreg_disks), ind, "Storage: " + storageDomain.name)
                    ind+=1
                    try:
                        storageDomain.disks.add(disk=params.Disk(id=disk_per_domain.id), unregistered=True)
                    except Exception as e:
                        self._handle_exception(self.disk_import, disk_per_domain, e)
            self._finish_registration(self.disksSlider, self.disk_import, "disk")

    def on_ok(self):
        api = self.parentApp.api
        _cluster_ = api.clusters.get(self.clusters.get_selected_objects()[0])
        active_sds = api.storagedomains.list('datacenter=%s status=active' % self.datacenters.get_selected_objects()[0])
        unreg_templates = set()
        unreg_vms = set()
        for storage_domain in active_sds:
            self._aggragte_entities(self.templatesSlider, self.template_import, 'templates', storage_domain, unreg_templates)
            self._aggragte_entities(self.vmsSlider, self.vm_import, 'vms', storage_domain, unreg_vms)

        self._reset_slider_texts()
        _cluster = api.clusters.get(self.clusters.get_selected_objects()[0])
        self._register_entities(_cluster, unreg_templates, self.templatesSlider, self.template_import, 'template')
        self._register_entities(_cluster, unreg_vms, self.vmsSlider, self.vm_import, 'vm')
        self._register_disks(active_sds)
        self.onRegisterPopup()

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
            self.parent.display()

class MyApplication(npyscreen.NPSAppManaged):
    TITLE = 'oVirt Disaster Recovery Tool'
    api = None

    def onStart(self):
       self.addForm('MAIN', startForm)
       self.addForm('start_page', connectForm, name=self.TITLE)
       self.addForm('import_storage', importStorageForm, name=self.TITLE)
       self.addForm('import_entities', importEntitiesForm, name=self.TITLE)

if __name__ == '__main__':
    TestApp = MyApplication().run()
