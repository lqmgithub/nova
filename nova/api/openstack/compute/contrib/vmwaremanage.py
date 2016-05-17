# Copyright (c) 2011 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import webob.exc
from nova.api.openstack import extensions
from nova import objects
from nova import context
from nova import compute
from oslo_vmware import api
from oslo_vmware import vim_util
from nova.network import model as network_model
from nova.compute import flavors
import datetime

documents = {"documents":[{"id":"1001", "name":"docs1"},
                                     {"id":"1002", "name":"docs2"},
                                     {"id":"1003", "name":"docs3"}]}

class VmwaremanageController(object):
    """The Hosts API controller for the OpenStack API."""
    def __init__(self):
        super(VmwaremanageController, self).__init__()
        self.compute_api = compute.API()


    def index(self, req):
        '''
        GET v2/{tenant_id}/os-vmwaremanage
        '''
        context = req.environ['nova.context']
        computeNode = req.GET["cnode"];
        #computeNode="localhost.localdomain"
        result = self.compute_api.get_vmware_vms(context, computeNode)
        return result
        
#         # Get a handle to a vSphere API session
#         session = api.VMwareAPISession(
#             '192.168.103.110',      # vSphere host endpoint
#             'root', # vSphere username
#             'root123',      # vSphere password
#             10,              # Number of retries for connection failures in tasks
#             0.1              # Poll interval for async tasks (in seconds)
#         )
# 
#       
#         vmlist = []
#         def buildList(result):
#             for obj in result.objects:
#                 if not hasattr(obj, 'propSet'):
#                     continue
#                 property_dict = {}
#                 property_dict[obj.obj._type]=obj.obj.value
#                 dynamic_properties = obj.propSet
#                 if dynamic_properties:
#                     for prop in dynamic_properties:
#                         property_dict[prop.name] = prop.val
#                 return property_dict;
# 
#         result = session.invoke_api(vim_util, "get_objects", session.vim,
#                                           #"VirtualMachine",1, ['guest','summary','config.hardware.numCoresPerSocket','config.hardware.numCPU','config.hardware.memoryMB'])
#                                           "VirtualMachine",1, ['name'])
#         while result:
#            print result
#            vmjson = buildList(result)
#            vmlist.append(vmjson)
#            result = session.invoke_api(vim_util, "continue_retrieval", session.vim,result)
#         session.logout();
#         return {"vms":vmlist}

    def show(self, req, id):
        '''
        GET v2/{tenant_id}/ os-documents/{document_id}

        '''
        document = None
        for docu in  documents["documents"]:
            if docu["id"] == id:
                 document = docu                    
        if document == None:
             raise webob.exc.HTTPNotFound(explanation="Document not found")
        else:
             return document
    
    def create(self, req, body):
        '''
        POST v2/{tenant_id}/os-documents 
        '''
#         
#         kwargs = {
#         'memory_mb': 1,
#         'vcpus': 1,
#         'root_gb': 0,
#         'ephemeral_gb': 0,
#         'swap': 0
#         }
#         
#         kwargs['name'] = 'qqq'
#         kwargs['flavorid'] = 9999
# 
#         
#         flavor = objects.Flavor(context=context.get_admin_context(), **kwargs)
#         flavor.create()
        computeNode = req.GET["cnode"];
        context2 = req.environ['nova.context']
        info_cache = objects.InstanceInfoCache()
        info_cache.network_info = network_model.NetworkInfo()
        _get_inst_type = flavors.get_flavor_by_flavor_id
        inst_type = _get_inst_type(451, ctxt=context.get_admin_context(),
                                       read_deleted="no")
        
        kwargs = {
            'user_id': "e4158f2557eb4b828df9a9e5cd05633c",
            'project_id': "83d5b3142395412c99078708f1f82895",  
            'power_state': 1,
            'vm_state': "active",
            'hostname':"addtest",
            'host':"localhost.localdomain",
            'display_name': "qmtest3",
            'launched_on':"localhost.localdomain",
             'memory_mb': 1024,
             'vcpus': 2,
             'root_gb': 0,
             'ephemeral_gb': 0,
             'availability_zone': 'nova',
             'node':'domain-c2516(poolwudong)',
             'launched_at':datetime.datetime.now(),
            'info_cache':info_cache,
            'flavor':inst_type
        }
        
        instance = objects.Instance(context.get_admin_context(), **kwargs)
      
        instance.create();
        
        #vmMap = {instance.uuid:"vm-2519"}
        result = self.compute_api.manage_vmware_vms(context2, computeNode,intanceUuid=instance.uuid,vmMorVal="vm-2523")
        
        return {}
        

    def update(self, req, body, id):
        '''
        PUT v2/{tenant_id}/os-documents/{document_id}
        '''
        document = None
        for docu in  documents["documents"]:
            if docu["id"] == id:
                documents["documents"].remove(docu)
                documents["documents"].append(body["document"])
                document = body["document"]
        if document == None:
             raise webob.exc.HTTPNotFound(explanation="Document not found")
        else:               
            return document

    def delete(self, req, id):
        '''
        DELETE v2/{tenant_id}/ os-documents/{document_id}
        '''
        document = None
        for docu in  documents["documents"]:
            if docu["id"] == id:
                 document = docu
                 documents["documents"].remove(docu)
                 return webob.Response(status_int=202)                
        if document == None:
             raise webob.exc.HTTPNotFound(explanation="Document not found")



class Vmwaremanage(extensions.ExtensionDescriptor):
    """vmware  manage"""

    name = "vmwaremanage"
    alias = "os-vmwaremanage"
    namespace = "http://docs.openstack.org/compute/ext/vmwaremanage/api/v1.1"
    updated = "2016-04-119T00:00:00Z"

    def get_resources(self):
        resources = [extensions.ResourceExtension('os-vmwaremanage',
                VmwaremanageController())]
        return resources
