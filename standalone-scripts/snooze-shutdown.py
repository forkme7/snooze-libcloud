#!/usr/bin/env python

from optparse import OptionParser 
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import json
import re
Snooze = get_driver(Provider.SNOOZE)


def main():
  driver = Snooze("127.0.0.1","5050");
  use = "Usage: %prog [options]" 
  parser = OptionParser(usage = use)
  parser.add_option("-n", "--vmn", dest="vmn",  help="shutdown vm")
  parser.add_option("-f", "--force", dest="force",action="store_true", default=False,  help="destroy vm")


  options, args = parser.parse_args()
  nodes = driver.list_nodes()
  print options.force
  for n in nodes:
    if re.match(options.vmn,n.name):
      if options.force: 
        driver.destroy(n)
      else:
        driver.shutdown(n)

if __name__ == '__main__':
    main()


