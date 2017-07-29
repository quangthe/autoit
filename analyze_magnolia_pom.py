#!/usr/bin/python

import sys
import os
import requests
from StringIO import StringIO
from lxml import etree

pom_version = ""


class PomAnalyzer(object):
    """ Extract dependency information from pom files of Magnolia CORE """

    def __init__(self):
        self.magnoliaVersion = ''

    def get_artifacts(self, url, outfile=None):

        params = {"raw": ""}
        secrete_key = os.environ['MY_SECRETE_KEY']
        header = {
            "Authorization": "Basic " + secrete_key,
            "Content-Type": "application/xml"
        }

        #print "Processing ", url
        result = {}

        try:
            r = requests.get(url, headers=header, params=params)

            namespaces = {'ns': 'http://maven.apache.org/POM/4.0.0'}
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(StringIO(r.content), parser=parser)
            dependencies = tree.xpath("//ns:dependency", namespaces=namespaces)

            if outfile is not None:
                file = open(outfile, 'w')

            project_version = tree.xpath("/ns:project/ns:version", namespaces=namespaces)

            self.magnoliaVersion = project_version[0].text

            if outfile is not None:
                file.write("Magnolia version: {}\n\n".format(pom_version))

            for d in dependencies:
                group_id = d.find('ns:groupId', namespaces=namespaces).text
                artifact_id = d.find('ns:artifactId', namespaces=namespaces).text
                current_version = self.__get_artifact_version(tree, d, namespaces)

                result["{}:{}".format(group_id, artifact_id)] = current_version

                if outfile is not None:
                    file.write("{}\n".format(group_id))
                    file.write("{}\n".format(artifact_id))
                    file.write("{}\n".format(current_version))
                    file.write("\n")

                #print "{", group_id, ", ", artifact_id, ", ", current_version, "}"

        except requests.exceptions.RequestException as e:
            print "Error response", e.message
        finally:
            if outfile is not None:
                file.close()

        #print "Found ", len(result), " artifacts in ", url, "\n\n"
        return result

    def __get_artifact_version(self, tree, dependency, namespaces):
        """ Helper method to get version of the given dependency """
        version = dependency.find('ns:version', namespaces=namespaces).text
        if version == '${project.version}':
            return self.magnoliaVersion

        if version.startswith('${'):
            prop = tree.xpath("//ns:" + version[2:-1], namespaces=namespaces)
            if len(prop) > 0:
                return prop[0].text

        return version


def main(argv):
    meta = {}

    analyzer = PomAnalyzer()

    url = "https://git.magnolia-cms.com/projects/PLATFORM/repos/ee/browse/pom.xml"
    artifacts = analyzer.get_artifacts(url=url, outfile="ee_pom.txt")
    meta.update(artifacts)

    url = "https://git.magnolia-cms.com/projects/PLATFORM/repos/ce/browse/pom.xml"
    artifacts = analyzer.get_artifacts(url=url, outfile="ce_pom.txt")
    meta.update(artifacts)

    print "Total artifacts found ", len(meta)

    print meta


if __name__ == '__main__':
    main(sys.argv[1:])
