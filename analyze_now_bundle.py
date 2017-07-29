#!/usr/bin/python

import sys
import os
import requests
from StringIO import StringIO
from lxml import etree
from get_latest_version import NexusHelper
from analyze_magnolia_pom import PomAnalyzer


def main(argv):
    # Analyze artifacts in Magnolia core
    meta = {}
    analyzer = PomAnalyzer()
    urls = ["https://git.magnolia-cms.com/projects/PLATFORM/repos/ee/browse/pom.xml",
            "https://git.magnolia-cms.com/projects/PLATFORM/repos/ce/browse/pom.xml"]
    for url in urls:
        artifacts = analyzer.get_artifacts(url)
        meta.update(artifacts)

    url = "https://git.magnolia-cms.com/projects/OD/repos/now-bundles/browse/magnolia-now-webapp/pom.xml"
    params = {"raw": ""}
    secrete_key = os.environ['MY_SECRETE_KEY']
    header = {
        "Authorization": "Basic " + secrete_key,
        "Content-Type": "application/xml"
    }

    try:
        # Analyze NOW bundle pom
        r = requests.get(url, headers=header, params=params)

        namespaces = {'ns': 'http://maven.apache.org/POM/4.0.0'}
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(StringIO(r.content), parser=parser)
        dependencies = tree.xpath("//ns:dependency", namespaces=namespaces)

        file = open('result.txt', 'w')

        nexus_helper = NexusHelper()
        header = "{:<50}{:<80}{:<30}{:<25}{:<25}".format("groupId", "artifactId", "current version", "new version", "latest release")

        file.write(header)
        file.write('\n')
        file.write("-" * 210)
        file.write('\n')

        print header
        print "-" * 210

        for d in dependencies:
            group_id = d.find('ns:groupId', namespaces=namespaces).text
            artifact_id = d.find('ns:artifactId', namespaces=namespaces).text
            current_version = get_current_version(tree, d, namespaces)

            latest_release_version = nexus_helper.get_released_version(group_id, artifact_id)

            new_version = meta.get("{}:{}".format(group_id, artifact_id))

            record = "{:<50}{:<80}{:<30}{:<25}{:<25}".format(group_id, artifact_id, current_version, new_version, latest_release_version)

            file.write(record)
            file.write('\n')
            print record

        file.write("-" * 210)
        file.write('\n')
        print "-" * 210

    except requests.exceptions.RequestException as e:
        print "Error response", e.message
    finally:
        file.close()


def get_current_version(tree, dependency, namespaces):
    current_version = dependency.find('ns:version', namespaces=namespaces).text
    if current_version.startswith('${'):
        prop = tree.xpath("//ns:" + current_version[2:-1], namespaces=namespaces)
        if len(prop) > 0:
            return prop[0].text

    return current_version


if __name__ == '__main__':
    main(sys.argv[1:])
