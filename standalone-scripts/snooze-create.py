#!/usr/bin/env python

from optparse import OptionParser 
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import json
Snooze = get_driver(Provider.SNOOZE)


def main():
  driver = Snooze("127.0.0.1","5000");
  use = "Usage: %prog [options] argument1 argument2"
  parser = OptionParser(usage = use)
  parser.add_option("-t", "--template", dest="template",  help="Set the template.")


  options, args = parser.parse_args()
  n1 = driver.create_node(libvirt_template=options.template,
     tx=12800,
     rx=12800)
  if n1==None:
    print "NO_RESPONSE"
  else:
    print n1.name, n1.state,n1.extra.get("ipAddress") 

if __name__ == '__main__':
    main()


