#!/usr/bin/python

import sys
import os
import requests
from StringIO import StringIO
from lxml import etree


def main(argv):
    # url = "https://git.magnolia-cms.com/projects/OD/repos/now-bundles/raw/magnolia-now-webapp/pom.xml"
    url = "https://git.magnolia-cms.com/projects/OD/repos/now-bundles/browse/magnolia-now-webapp/pom.xml"
    params = {"raw": ""}
    secrete_key = os.environ['MY_SECRETE_KEY']
    header = {
        "Authorization": "Basic " + secrete_key,
        "Content-Type": "application/xml"
    }
    try:
        r = requests.get(url, headers=header, params=params)
        # if r.status_code == 200:
        #     with open('pom.xml', 'w') as f:
        #         f.write(r.content)

        parser = etree.XMLParser(remove_pis=True, ns_clean=True)
        tree = etree.parse(StringIO(r.content), parser=parser)
        dependencies = tree.xpath("//dependency")
        print dependencies
        # for d in dependencies:
        #     print d
    except requests.exceptions.RequestException as e:
        print "Error response", e.message


if __name__ == '__main__':
    main(sys.argv[1:])
