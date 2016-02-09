#!/usr/bin/env python

import json
import os
import os.path
import subprocess

def read_credentials():
    credentials = {}
    fh = open(os.path.expanduser("~/.bintray/.credentials"))
    for line in fh:
        line = line.strip().split("=")
        credentials[line[0].strip()] = line[1].strip()
    return credentials

credentials = read_credentials()

def latest_version(repo, pkg):
    curl_cmd = [
        "curl", "-s", "-u", credentials["user"] + ":" + credentials["password"],
        "https://api.bintray.com/packages/m-doc/%s/%s/versions/_latest" % (repo, pkg)
    ]
    return json.loads(subprocess.check_output(curl_cmd))

def sbt_mdoc_plugin():
    lv = latest_version("sbt-plugins", "sbt-mdoc")
    content = (
        """resolvers += Resolver.url("m-doc/sbt-plugins",\n"""
        """  url("http://dl.bintray.com/content/m-doc/sbt-plugins"))(Resolver.ivyStylePatterns)\n"""
        """\n"""
        """addSbtPlugin("org.m-doc" % "sbt-mdoc" % "{0}")\n""").format(lv["name"])
    return content

def to_lower_camel(s):
    lc = s.title().replace("-", "")
    return lc[0].lower() + lc[1:]

def mdoc_library(libs):
    content = "import sbt._\n\n"
    content += "object MdocLibrary {\n"
    for name, version in libs.iteritems():
        content += "  val %s = \"org.m-doc\" %%%% \"%s\" %% \"%s\"\n" % (
                to_lower_camel(name), name, version)
    content +=  "}\n"
    return content

libs_version = {}
libs = ["common-model", "fshell", "rendering-engines"]
for lib in libs:
    lv = latest_version("maven", lib)
    libs_version[lib] = lv["name"]

mdoc_lib = mdoc_library(libs_version)
sbt_mdoc = sbt_mdoc_plugin()

for d in next(os.walk("."))[1]:
    plugin = d + "/project/plugin-mdoc.sbt"
    if os.path.isfile(plugin):
        fh = open(plugin, "w")
        fh.write(sbt_mdoc)
        fh.close()

        fh = open(d + "/project/MdocLibrary.scala", "w")
        fh.write(mdoc_lib)
        fh.close()

