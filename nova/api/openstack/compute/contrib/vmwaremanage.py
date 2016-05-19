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
from nova.compute import flavors, power_state, vm_states
import datetime
import uuid

documents = {"documents":[{"id":"1001", "name":"docs1"},
                                     {"id":"1002", "name":"docs2"},
                                     {"id":"1003", "name":"docs3"}]}

powerStateMap = {"poweredOff":power_state.SHUTDOWN,"poweredOn":power_state.RUNNING,"suspended":power_state.SUSPENDED}
vmStateMap = {"poweredOff":vm_states.STOPPED,"poweredOn":vm_states.ACTIVE,"suspended":vm_states.SUSPENDED}

class VmwaremanageController(object):
    """The VMware management API controller for the OpenStack API."""
    def __init__(self):
        super(VmwaremanageController, self).__init__()
        self.compute_api = compute.API()


    def index(self, req):
        '''GET v2/{tenant_id}/os-vmwaremanage'''
        context = req.environ['nova.context']
        computeNode = req.GET["cnode"];
        
#         _context = context.to_dict()
#         userid = _context.get("user_id")
#         projectid = _context.get("project_id")
#         projectid = _context.get("user_domain")
#         for k,v in _context.items():
#             print k,v
#         return _context

        #computeNode="localhost.localdomain"
        result = self.compute_api.get_vmware_vms(context, computeNode)
        return result
        

    def show(self, req, id):
        '''
        GET v2/{tenant_id}/ os-vmwaremanage/{vm_ref}

        '''
        context = req.environ['nova.context']
        computeNode = req.GET["cnode"];
        result = self.compute_api.get_vmware_vminfo(context, computeNode,id)
        return result
    
    def create(self, req, body):
        '''
        POST v2/{tenant_id}/os-vmwaremanage 
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
        _context = context2.to_dict()
        userid = _context.get("user_id")
        projectid = _context.get("project_id")
        
        
        vm_ref = body["vm_ref"]
        vminfo = self.compute_api.get_vmware_vminfo(context2, computeNode,vm_ref)
 
        
        powerState = powerStateMap.get(vminfo.get("runtime.powerState"),power_state.NOSTATE)
        vmState = vmStateMap.get(vminfo.get("runtime.powerState"),vm_states.ERROR);
        hostname = vminfo.get("summary.guest.hostName")
        vmName = vminfo.get("name")
        memoryMB = vminfo.get("config.hardware.memoryMB")
        numCoresPerSocket = vminfo.get("config.hardware.numCoresPerSocket")
        numCPU = vminfo.get("config.hardware.numCPU")
        vcpus = int(numCoresPerSocket)*int(numCPU)
         
        devcieVo = vminfo.get("config.hardware.device") 
        rootGb = 0l
        for diskvo in devcieVo.get("disk"):
            rootGb = rootGb + diskvo.get("capacityInKB",0)
        rootGb = rootGb/1024/1024
        
        limited_flavors = flavors.get_all_flavors_sorted_list(context2,{'is_public':True})
        
        
        matchFlavor = None
        for flavor in limited_flavors:
            if  long(flavor.get("memory_mb")) == memoryMB  and  long(flavor.get("vcpus")) == vcpus  and long(flavor.get("root_gb")) == rootGb :
                matchFlavor = flavor
                break
        
        if not matchFlavor:
            flavorKwargs = {
                'memory_mb': memoryMB,
                'vcpus': vcpus,
                'root_gb': rootGb,
                'ephemeral_gb': 0,
                'swap': 0,
                'name':vmName,
                'flavorid':str(uuid.uuid4())
            }
            flavor = objects.Flavor(context=context2, **flavorKwargs)
            flavor.create()
            matchFlavor = flavor
       
        
        info_cache = objects.InstanceInfoCache()
        info_cache.network_info = network_model.NetworkInfo()
        _get_inst_type = flavors.get_flavor_by_flavor_id
        inst_type = _get_inst_type(matchFlavor.flavorid, ctxt=context2,
                                       read_deleted="no")
        kwargs = {
            'user_id': userid,
            'project_id': projectid,  
            'power_state': powerState,
            'vm_state': vmState,
            'hostname':hostname,
            'host':computeNode,
            'display_name': vmName,
            'launched_on':computeNode,
             'memory_mb': memoryMB,
             'vcpus': vcpus,
             'root_gb': rootGb,
             'ephemeral_gb': 0,
             'availability_zone': 'nova',
             'node':'domain-c2516(poolwudong)',
             'launched_at':datetime.datetime.now(),
            'info_cache':info_cache,
            'flavor':inst_type
        }
        
        instance = objects.Instance(context2, **kwargs)
      
        instance.create();
        
        #vmMap = {instance.uuid:"vm-2519"}
        result = self.compute_api.manage_vmware_vms(context2, computeNode,intanceUuid=instance.uuid,vmMorVal=vm_ref)
        
        return result
        

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
