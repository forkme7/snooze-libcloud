from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import time
import json
import unittest
from subprocess import Popen, PIPE

"""
(Not Unit) Tests 
Test Snooze drivers V0
"""

class TestSnooze(unittest.TestCase):

    def setUp(self):
        time.sleep(10)
        Snooze = get_driver(Provider.SNOOZE)
        """
        Address of the bootstrap node
        """
        self.driver = Snooze("127.0.0.1","5000");        
        self.n1 = self.driver.create_node(libvirt_template="/home/msimonin/Images-VM/Snooze-images/vmtemplates/debian1.xml",
                   tx=12800,
                   rx=12800
                   )
        self.extra = self.n1.extra

    def _test_metadata(self):
        self.assertIsNotNone(self.n1.extra, msg="metadata are null!")
        self.assertIsNotNone(self.extra.get("virtualMachineLocation"), msg="location is not set correctly")
        
        self.assertIsNotNone(self.extra.get("virtualMachineLocation").get("virtualMachineId"), msg="virtual machine id is not set correctly")
        self.assertIsNot(self.extra.get("virtualMachineLocation").get("virtualMachineId"),"UNKNOWN", msg="virtual machine id is UNKNOWN")
        
        self.assertIsNotNone(self.extra.get("virtualMachineLocation").get("localControllerId"), msg="local controller id is not set correctly")
        self.assertIsNot(self.extra.get("virtualMachineLocation").get("localControllerId"), "UNKNOWN", msg="local controller id is UNKNOWN")
        
        self.assertIsNotNone(self.extra.get("virtualMachineLocation").get("localControllerControlDataAddress"), msg="local controller address is not set correctly")
        self.assertIsNot(self.extra.get("virtualMachineLocation").get("localControllerControlDataAddress").get("address"), "UNKNOWN", msg="local controller address is UNKNOWN")
        self.assertIsNot(self.extra.get("virtualMachineLocation").get("localControllerControlDataAddress").get("port"), -1, msg="local controller port is UNKNOWN")

        self.assertIsNotNone(self.extra.get("groupManagerControlDataAddress"), msg="group manager controller address is not set correctly")
        self.assertIsNot(self.extra.get("groupManagerControlDataAddress").get("address"), "UNKNOWN", msg="local controller address is UNKNOWN")
        self.assertIsNot(self.extra.get("groupManagerControlDataAddress").get("port"), -1, msg="local controller port is UNKNOWN")

    """
    These properties may not change during the vm life cycle.
    (unless under migration)
    """
    def _test_info_metadata(self,metadata):
        self.assertIsNotNone(metadata, msg="metadata are null!")
        self.assertIsNotNone(metadata.get("virtualMachineLocation"), msg="location is not set correctly")
        
        self.assertIsNotNone(metadata.get("virtualMachineLocation").get("virtualMachineId"), msg="virtual machine id is not set correctly")
        self.assertIsNot(metadata.get("virtualMachineLocation").get("virtualMachineId"),"UNKNOWN", msg="virtual machine id is UNKNOWN")
        
        self.assertIsNotNone(metadata.get("virtualMachineLocation").get("localControllerId"), msg="local controller id is not set correctly")
        self.assertIsNot(metadata.get("virtualMachineLocation").get("localControllerId"), "UNKNOWN", msg="local controller id is UNKNOWN")
        
        self.assertIsNotNone(metadata.get("virtualMachineLocation").get("localControllerControlDataAddress"), msg="local controller address is not set correctly")
        self.assertIsNot(metadata.get("virtualMachineLocation").get("localControllerControlDataAddress").get("address"), "UNKNOWN", msg="local controller address is UNKNOWN")
        self.assertIsNot(metadata.get("virtualMachineLocation").get("localControllerControlDataAddress").get("port"), "UNKNOWN", msg="local controller port is UNKNOWN")

    """
    These may be change on gm failure but must be set properly
    """
    def _test_info_metadata_groupmanager(self,metadata):
        self.assertIsNotNone(metadata.get("groupManagerControlDataAddress"), msg="group manager controller address is not set correctly")
        self.assertIsNot(metadata.get("groupManagerControlDataAddress").get("address"), "UNKNOWN", msg="group manager address is UNKNOWN")
        self.assertIsNot(metadata.get("groupManagerControlDataAddress").get("port"), -1, msg="group manager port is UNKNOWN")
        
    def test_create_node(self):
        self.assertEqual(self.n1.name,"debian1", msg="the name is not set correctly")
        self.assertEqual(self.n1.state,"RUNNING", msg="the state is not set correctly" )
        
        self._test_metadata()           
        #clean
        time.sleep(5)
        
    def test_created_node(self):
        time.sleep(10)
        info = self.driver.get_info(self.n1)
        # it is running
        self.assertEqual(info.get("status"),"RUNNING")
        # on the same location than before
        self.assertEqual(info.get("virtualMachineLocation"),self.extra.get("virtualMachineLocation"))
        
        self._test_info_metadata_groupmanager(info)
        
    def test_suspend_node(self):
        time.sleep(10)
        self.driver.suspend(self.n1)
        time.sleep(10)
        info = self.driver.get_info(self.n1)
        # it is paused
        self.assertEqual(info.get("status"),"PAUSED", msg="status is not PAUSED")
        # on the same location that was given
        self.assertIsNotNone(info.get("virtualMachineLocation"))
        self.assertEqual(info.get("virtualMachineLocation"),self.extra.get("virtualMachineLocation"))
        self._test_info_metadata_groupmanager(info)


    def test_resume_node(self):
        self.test_suspend_node()
        self.driver.resume(self.n1)
        time.sleep(10)
        info = self.driver.get_info(self.n1)
        # it is paused
        self.assertEqual(info.get("status"),"RUNNING", msg="status is not RUNNING")
        # on the same location that was given
        self.assertIsNotNone(info.get("virtualMachineLocation"))
        self.assertEqual(info.get("virtualMachineLocation"),self.extra.get("virtualMachineLocation"))
        self._test_info_metadata_groupmanager(info)

     
    def test_shutdown_node(self):
        time.sleep(10)
        self.driver.shutdown(self.n1)
        info = self.driver.get_info(self.n1)
        self.assertEqual(info.get("status"),"SHUTDOWN_PENDING")
        time.sleep(10)
        info = self.driver.get_info(self.n1)
        self.assertEqual(info.get("status"),"OFFLINE")
        
        time.sleep(5)

    def tearDown(self):
        #print "end"
        #hard clean !
        virsh = Popen(["virsh destroy debian1"],shell=True, stdout=PIPE)
        stdout, stderr = virsh.communicate()




if __name__ == '__main__':
    unittest.main()
    
