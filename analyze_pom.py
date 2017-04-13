#!/usr/bin/python

import sys
import os
import requests
from StringIO import StringIO
from lxml import etree
from get_latest_version import get_latest_version


def main(argv):
    url = "https://git.magnolia-cms.com/projects/OD/repos/now-bundles/browse/magnolia-now-webapp/pom.xml"
    params = {"raw": ""}
    secrete_key = os.environ['MY_SECRETE_KEY']
    header = {
        "Authorization": "Basic " + secrete_key,
        "Content-Type": "application/xml"
    }
    try:
        r = requests.get(url, headers=header, params=params)

        namespaces = {'ns': 'http://maven.apache.org/POM/4.0.0'}
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(StringIO(r.content), parser=parser)
        dependencies = tree.xpath("//ns:dependency", namespaces=namespaces)

        f1 = open('old.txt', 'w')
        f2 = open('new.txt', 'w')

        for d in dependencies:
            group_id = d.find('ns:groupId', namespaces=namespaces).text
            artifact_id = d.find('ns:artifactId', namespaces=namespaces).text
            current_version = get_current_version(tree, d, namespaces)

            f1.write("{}\n".format(group_id))
            f1.write("{}\n".format(artifact_id))
            f1.write("{}\n".format(current_version))
            f1.write("\n")

            latest_version = get_latest_version(group_id=group_id, artifact_id=artifact_id)
            f2.write("{}\n".format(group_id))
            f2.write("{}\n".format(artifact_id))
            f2.write("{}\n".format(latest_version))
            f2.write("\n")

            print "{", group_id, ", ", artifact_id, ", ", latest_version, "}"

    except requests.exceptions.RequestException as e:
        print "Error response", e.message
    finally:
        f1.close()
        f2.close()


def get_current_version(tree, dependency, namespaces):
    current_version = dependency.find('ns:version', namespaces=namespaces).text
    if current_version.startswith('${'):
        prop = tree.xpath("//ns:" + current_version[2:-1], namespaces=namespaces)
        if len(prop) > 0:
            return prop[0].text

    return current_version


if __name__ == '__main__':
    main(sys.argv[1:])
