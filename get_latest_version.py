#!/usr/bin/python

import getopt
import sys
import os
from StringIO import StringIO

import requests
from lxml import etree


def main(argv):
    group_id = ''
    artifact_id = ''
    try:
        opts, args = getopt.getopt(argv, "hg:a:", ["groupId=", "artifactId="])

    except getopt.GetoptError:
        print 'get_latest_version -g <groupId> -a <artifactId>'
        exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'get_latest_version -g <groupId> -a <artifactId>'
            sys.exit()
        elif opt in ("-g", "--groupId"):
            group_id = arg
        elif opt in ("-a", "--artifactId"):
            artifact_id = arg

    print "groupId: ", group_id
    print "artifactId: ", artifact_id

    latest_version = get_latest_version(group_id, artifact_id)
    print latest_version


def get_latest_version(group_id, artifact_id):
    secrete_key = os.environ['MY_SECRETE_KEY']
    header = {"Authorization": "Basic " + secrete_key}

    # Get latest version of given artifact
    params = {
        "g": group_id,
        "a": artifact_id,
    }
    url = "https://nexus.magnolia-cms.com/service/local/lucene/search"

    try:
        r = requests.get(url, headers=header, params=params)

        # parse latest version
        tree = etree.parse(StringIO(r.content))
        latest_version = tree.xpath("//latestRelease")
        return latest_version[0].text
    except requests.exceptions.RequestException as e:
        print "Error response", e.message
        return None

if __name__ == "__main__":
    main(sys.argv[1:])
