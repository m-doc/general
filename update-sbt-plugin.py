#!/usr/bin/env python

import json
import os
import os.path
import subprocess

credentials = {}
fh = open(os.path.expanduser("~/.bintray/.credentials"))
for line in fh:
    line = line.strip().split(" = ")
    credentials[line[0]] = line[1]

curl_cmd = [
  "curl", "-s", "-u", credentials["user"] + ":" + credentials["password"],
  "https://api.bintray.com/packages/m-doc/sbt-plugins/sbt-mdoc/versions/_latest"
]

out = subprocess.check_output(curl_cmd)
parsed = json.loads(out)
version = parsed["name"]

def sbt_mdoc_plugin(version):
    content = """
resolvers += Resolver.url("m-doc/sbt-plugins",
  url("http://dl.bintray.com/content/m-doc/sbt-plugins"))(Resolver.ivyStylePatterns)

addSbtPlugin("org.m-doc" % "sbt-mdoc" % "{0}"
""".format(version).lstrip()
    return content

sbt_mdoc = sbt_mdoc_plugin(version)
for d in next(os.walk("."))[1]:
    plugin = d + "/project/plugin-mdoc.sbt"
    if os.path.isfile(plugin):
        fh = open(plugin, "w")
        fh.write(sbt_mdoc)
