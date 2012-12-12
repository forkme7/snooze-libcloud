# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

Snooze = get_driver(Provider.SNOOZE)

"""
Address of the bootstrap node
"""
driver = Snooze("127.0.0.1","5000");

resp = driver.get_and_set_groupleader() ;
print "group leader address %s : %s" %(resp.get("address"),resp.get("port"))


"""
We create a first VM using the template fashion
"""
n1 = driver.create_node(libvirt_template="/home/msimonin/Images-VM/Snooze-images/vmtemplates/debian1.xml",
                   tx=12800,
                   rx=12800
                   )

n2 = driver.create_node(libvirt_template="/home/msimonin/Images-VM/Snooze-images/vmtemplates/debian2.xml",
                   tx=12800,
                   rx=12800
                   )
print "VM %s status %s"%(n1.name,n1.state)

print driver.list_nodes()
