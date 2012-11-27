from libcloud.compute.base import NodeDriver, Node, NodeSize
from libcloud.compute.base import NodeState, NodeImage
from libcloud.compute.types import Provider

from libcloud.common.base import Connection

from xml.dom.minidom import parseString
import json

import time

class SnoozeConnection(Connection):
    """
    Dummy connection class
    """
    def __init__(self,host,port):
        super(SnoozeConnection, self).__init__(False, host, port)
        
           
           
class SnoozeNodeDriver(NodeDriver):
    """
    Snooze (http://snooze.inria.fr) node driver.

    """
    type = Provider.SNOOZE
    name = 'Snooze'
    website = 'http://snooze.inria.fr'
    

    
    def __init__(self,host,port):
        """
        
        """
        self.connection_bs = SnoozeConnection(host,port)
        self.connection_bs.driver = self 
        
        self.connection_gl = SnoozeConnection(host,port)
        self.connection_gl.driver = self 
        
        self.connection_gm = SnoozeConnection(host,port)
        self.connection_gl.driver = self
        #self.connection.host = "http://localhost"
        #self.connection.port = "5000"
        
    def get_and_set_groupleader(self):
        """
        Gets the group leader
        """
        resp = self.connection_bs.request("/bootstrap?getGroupLeaderDescription",method='GET') 
        json_data = resp.body
        data = json.loads(json_data)
        host = data["listenSettings"]["controlDataAddress"]["address"]
        port = data["listenSettings"]["controlDataAddress"]["port"]
        self.connection_gl = SnoozeConnection(host,port)
        self.connection_gl.driver = self 
        
        return data["listenSettings"]["controlDataAddress"] 

    def get_and_set_assigned_groupmanager(self,node):
        """
        Gets the assigned group manager 
        """
        metadata = node.extra ;
        group_manager_address = metadata.get("groupManagerControlDataAddress")
        host = group_manager_address.get("address")
        port = group_manager_address.get("port")
        self.connection_gm = SnoozeConnection(host,port)
        self.connection_gm.driver = self
        
    def polling_for_response(self,task_id):
        server_object = None 
        i = 1  
        time.sleep(2)
        while i <= 10 :
            resp = self.connection_gl.request("groupmanager?getVirtualClusterResponse",method='POST',data=task_id)
            if not resp.object:
                i=i+1
                time.sleep(2)
            else :
                server_object = resp.object
                break 
        server_object = json.loads(server_object)
        return server_object

    
        
    def get_info(self,node):
        """
        Get info for a node.
        """      
        metadata = node.extra ;
        self.get_and_set_assigned_groupmanager(node)
        
        metadata_request = {"virtualMachineLocation": metadata.get("virtualMachineLocation"),
                            "numberOfMonitoringEntries" : 10
                            }
        resp = self.connection_gm.request('/groupmanager?getVirtualMachineMetaData',method='POST',data=json.dumps(metadata_request))
        return json.loads(resp.object)


    def _to_node(self,api_node):
        meta_data = api_node.get("virtualMachineMetaData",None)
        if meta_data is None:
            return None
        else:
            meta_data = meta_data[0] 
            return Node(
                id=meta_data.get("virtualMachineLocation").get("virtualMachineId",None),
                name=meta_data.get("virtualMachineLocation").get("virtualMachineId",None),
                state=meta_data.get("status","UNKNOWN"),
                public_ips=meta_data.get("ip_address","UNKNOWN"),
                private_ips=None,
                driver=self,
                extra = meta_data
            )
          
    def get_name_from_template(self,template):
        dom = parseString(template)
        xmlTag = dom.getElementsByTagName('name')[0].toxml()
        xmlData=xmlTag.replace('<name>','').replace('</name>','')
        return xmlData
     
    def shutdown(self,node):
        metadata = node.extra ;
        self.get_and_set_assigned_groupmanager(node)
        location = node.extra.get("virtualMachineLocation")
        resp = self.connection_gm.request("groupmanager?shutdownVirtualMachine",method='POST',data=json.dumps(location))
        
    def suspend(self,node):
        metadata = node.extra ;
        self.get_and_set_assigned_groupmanager(node)
        location = node.extra.get("virtualMachineLocation")
        resp = self.connection_gm.request("groupmanager?suspendVirtualMachine",method='POST',data=json.dumps(location))
        
class SnoozeNodeDriverV0(SnoozeNodeDriver):
    """
    Original version
    """
    def create_node(self, **kwargs):
        """
        startVirtualCluster
        @param       libvirt_template:  libvirt_template
        @type        libvirt_template: C{str}

        @param       tx: network transmission capacity
        @type        tx: C{int}
        
        @param       rx: network receive capacity
        @type        rx: C{int}
        """
        uri = self.get_and_set_groupleader()
        
        libvirt_template = kwargs.get("libvirt_template")
        tx = kwargs.get("tx")
        rx = kwargs.get("rx")
         
        f = open(libvirt_template)
        template = f.read().replace('\n','').replace('\r','') 
        name = self.get_name_from_template(template)
    
        attributes = {"virtualMachineTemplates":
                         [
                             {
                                "libVirtTemplate":template,
                                "networkCapacityDemand" : 
                                   {
                                    "txBytes" : tx,
                                    "rxBytes" : rx,
                                    }
                             }
                          ]
                      }
        resp = self.connection_gl.request("groupmanager?startVirtualCluster",method='POST',data=json.dumps(attributes))
        task_id = resp.object
        
        server_object = self.polling_for_response(task_id)
        return self._to_node(server_object)


class SnoozeNodeDriverV1(SnoozeNodeDriver):
    """
    image repository support
    """
    def create_node(self, **kwargs):
        """
        create a new node
        We have to choose between create_node_raw and create_node_id_based
        """
        #try:
        image = kwargs.get("image",None)
        if image is None:
            return self.create_node_raw(**kwargs)
        else:
            return self.create_node_id_based(**kwargs)
            
        
    def create_node_raw(self, **kwargs):
        """
        startVirtualCluster
        @param       libvirt_template:  libvirt_template
        @type        libvirt_template: C{str}

        @param       tx: network transmission capacity
        @type        tx: C{int}
        
        @param       rx: network receive capacity
        @type        rx: C{int}
        """
        uri = self.get_and_set_groupleader()
        
        libvirt_template = kwargs.get("libvirt_template")
        tx = kwargs.get("tx")
        rx = kwargs.get("rx")
         
        f = open(libvirt_template)
        template = f.read().replace('\n','').replace('\r','') 
        name = self.get_name_from_template(template)
    
        attributes = {"virtualMachineTemplates":
                         [
                             {
                                "type": "raw",
                                "libVirtTemplate":template,
                                "networkCapacityDemand" : 
                                   {
                                    "txBytes" : tx,
                                    "rxBytes" : rx,
                                    }
                             }
                          ]
                      }
        resp = self.connection_gl.request("groupmanager?startVirtualCluster",method='POST',data=json.dumps(attributes))
        task_id = resp.object

        server_object = self.polling_for_response(task_id)
        return self._to_node(server_object)
        
    
    def create_node_id_based(self, **kwargs):
        """
        Create a node.
        """      
        uri = self.get_and_set_groupleader()
        name = kwargs['name']
        image = kwargs['image']
        size = kwargs['size']

        attributes = {"virtualMachineTemplates":
                         [
                             {
                                "type": "id_based",
                                "name": name,
                                "imageIdentifier": str(image.id),
                                "vcpuDemand": "1",
                                "memoryDemand": str(size.ram*1000),
                                "networkCapacityDemand" : 
                                   {
                                    "txBytes" : str(2*size.bandwidth),
                                    "rxBytes" : str(size.bandwidth),
                                    }
                             }
                          ]
                      }
        
        resp = self.connection_gl.request("groupmanager?startVirtualCluster",method='POST',data=json.dumps(attributes))
        task_id = resp.object
        
        
        server_object = self.polling_for_response(task_id)
        return self._to_node(server_object)
        
    def list_sizes(self):
        """
           From Dummy Driver
        """

        return [
            NodeSize(id=1,
                     name="Small",
                     ram=128,
                     disk=4,
                     bandwidth=500,
                     price=4,
                     driver=self),
            NodeSize(id=2,
                     name="Medium",
                     ram=512,
                     disk=16,
                     bandwidth=1500,
                     price=8,
                     driver=self),
            NodeSize(id=3,
                     name="Big",
                     ram=4096,
                     disk=32,
                     bandwidth=2500,
                     price=32,
                     driver=self),
            NodeSize(id=4,
                     name="XXL Big",
                     ram=4096 * 2,
                     disk=32 * 4,
                     bandwidth=2500 * 3,
                     price=32 * 2,
                     driver=self),
        ]    
        
    
    def list_images(self):
        resp = self.connection_bs.request('/images?getList')
        json_data = resp.body
        data = json.loads(json_data)
        return self._to_images(data)    
            
        
    
    
    def _to_images(self, object):
        images = []
        for image in object["images"]:
            images.append(self._to_image(image))

        return images

    def _to_image(self, element):
        return NodeImage(id=element.get('id'),
                         name=element.get('name'),
                         driver=self,
                         extra={}
                         )
        
   
       