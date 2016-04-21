# Copyright 2012 OpenStack Foundation
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

import webob

from nova.api.openstack import common
from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova import compute
from nova import exception
from nova.i18n import _

documents = {"documents":[{"id":"1001", "name":"docs1"},
                                     {"id":"1002", "name":"docs2"},
                                     {"id":"1003", "name":"docs3"}]}

authorize = extensions.extension_authorizer('compute', 'documents3')


class Documents3Controller(wsgi.Controller):
    def __init__(self, *args, **kwargs):
        self.compute_api = compute.API()
        super(Documents3Controller, self).__init__(*args, **kwargs)

    
    def index(self, req):
        '''
        GET v2/{tenant_id}/ os-documents
        '''
        return documents

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
        try:
            documents["documents"].append(body["document"])
        except :
            raise webob.exc.HTTPBadRequest(explanation="Document invalid")
        return body["document"]
        

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



class Documents3(extensions.ExtensionDescriptor):
    """Interactive Console support."""
    name = "documents3"
    alias = "os-documents3"
    namespace = "http://docs.openstack.org/compute/ext/os-documents3/api/v2"
    updated = "2016-12-23T00:00:00Z"

    def get_controller_extensions(self):
        controller = Documents3Controller()
        extension = extensions.ControllerExtension(self, 'servers', controller)
        return [extension]
