from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import time
import json
import unittest
from subprocess import Popen, PIPE

"""
This is not unit testing ! 
"""

class TestSnooze(unittest.TestCase):

    def setUp(self):
        Snooze = get_driver(Provider.SNOOZE)
        """
        Address of the bootstrap node
        """
        self.driver = Snooze("127.0.0.1","5000");
            
    def test_create_node(self):
        n1 = self.driver.create_node(libvirt_template="/home/msimonin/Images-VM/Snooze-images/vmtemplates/debian1.xml",
                   tx=12800,
                   rx=12800
                   )
        
        self.assertEqual(n1.name,"debian1")
        self.assertEqual(n1.state,"LAUNCHING")
        self.assertIsNotNone(n1.extra)
        #clean
        time.sleep(5)
        
    def test_created_node(self):
        n1 = self.driver.create_node(libvirt_template="/home/msimonin/Images-VM/Snooze-images/vmtemplates/debian1.xml",
                   tx=12800,
                   rx=12800
                   )
        extra = n1.extra
        time.sleep(5)
        info = self.driver.get_info(n1)
        # it is running
        self.assertEqual(info.get("status"),"RUNNING")
        # on the same location that was given
        self.assertIsNotNone(info.get("virtualMachineLocation"))
        self.assertIsNotNone(extra.get("virtualMachineLocation"))        
        self.assertEqual(info.get("virtualMachineLocation"),extra.get("virtualMachineLocation"))
        
    def test_suspend_node(self):
        n1 = self.driver.create_node(libvirt_template="/home/msimonin/Images-VM/Snooze-images/vmtemplates/debian1.xml",
                   tx=12800,
                   rx=12800
                   )
        extra = n1.extra
        time.sleep(5)
        self.driver.suspend(n1)
        time.sleep(5)
        info = self.driver.get_info(n1)
        # it is running
        self.assertEqual(info.get("status"),"PAUSED")
        # on the same location that was given
        self.assertIsNotNone(info.get("virtualMachineLocation"))
        self.assertIsNotNone(extra.get("virtualMachineLocation"))        
        self.assertEqual(info.get("virtualMachineLocation"),extra.get("virtualMachineLocation"))

                
    def tearDown(self):
        #clean
        virsh = Popen(["virsh destroy debian1"],shell=True, stdout=PIPE)
        stdout, stderr = virsh.communicate()

if __name__ == '__main__':
    unittest.main()