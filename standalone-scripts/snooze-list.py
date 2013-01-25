#!/usr/bin/env python

from optparse import OptionParser 
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import json
Snooze = get_driver(Provider.SNOOZE)


def main():
  driver = Snooze("127.0.0.1","5000");

  nodes = driver.list_nodes()
  for n in nodes:
    print n.name, n.state, n.extra.get("ipAddress")

if __name__ == '__main__':
      main()
