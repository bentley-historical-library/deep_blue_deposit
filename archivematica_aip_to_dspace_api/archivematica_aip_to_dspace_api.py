import os
import subprocess
from lxml import etree
import shutil
import requests
from lxml.builder import E
from slacker import Slacker

from credentials import *

# `\media\sf_DeepBlue` is auto-mounted
deep_blue_saf_staging = os.path.join(
    os.path.sep,
    "media", "sf_DeepBlue", "deepblue_saf_staging")
deep_blue_saf_temp = os.path.join(
    os.path.sep,
    "media", "sf_DeepBlue", "deepblue_saf_temp")
deep_blue_saf_transfer = os.path.join(
    os.path.sep,
    "media", "sf_DeepBlue", "deepblue_saf_transfer")

aip_dirs = []

for root, _, files in os.walk(deep_blue_saf_staging):
    for name in files:

        aip = os.path.join(root, name)

        print "unarchiving " + aip

        # command = ["unar",
            # "-force-overwrite",
            # "-output-directory", deep_blue_saf_temp,
            # aip]
        # subprocess.call(command)

        aip_dir = os.path.join(deep_blue_saf_temp, os.path.splitext(name)[0])
        aip_dirs.append(aip_dir)

for aip_dir in aip_dirs:

    print "\nprocessing " + aip_dir

    print "  * getting metadata"

    mets_dir = os.path.join(aip_dir, "data", [name for name in os.listdir(os.path.join(aip_dir, "data")) if name.startswith("METS")][0])

    tree = etree.parse(mets_dir)
    namespaces = {
        "premis": "info:lc/xmlns/premis-v2",
        "dc": "http://purl.org/dc/elements/1.1/"
    }

    user = [agent.xpath("./premis:agentName", namespaces=namespaces)[0].text for agent in tree.xpath("//premis:agent", namespaces=namespaces) if agent.xpath("./premis:agentType", namespaces=namespaces)[0].text == "Archivematica user"][0]
    username = user.split(", ")[0].split('"')[1].split('"')[0]
    first_name = user.split(", ")[1].split('"')[1].split('"')[0]
    last_name = user.split(", ")[2].split('"')[1].split('"')[0]

    print "\nUsername | First Name | Last Name"
    print "--- | --- | ---"
    print " | ".join([username, first_name, last_name])

    accession_no = [event.xpath("./premis:eventOutcomeInformation/premis:eventOutcomeDetail/premis:eventOutcomeDetailNote", namespaces=namespaces)[0].text.split("#")[1] for event in tree.xpath("//premis:event", namespaces=namespaces) if event.xpath("./premis:eventType", namespaces=namespaces)[0].text == "registration"][0]

    dcterms_title = tree.xpath(".//dc:title", namespaces=namespaces)[0].text
    dcterms_description_abstract = ""
    dcterms_contributor_author =  tree.xpath(".//dc:creator", namespaces=namespaces)[0].text
    dcterms_date_issued = tree.xpath(".//dc:date", namespaces=namespaces)[0].text
    dcterms_rights_copyright = tree.xpath(".//dc:rights", namespaces=namespaces)[0].text
    dcterms_relation_ispartofseries = ""

    print "\ndc.title | dc.description.abstract | dc.contributor.author | dc.date.issued | dc.rights.copyright | dc.relation.ispartofseries"
    print "--- | --- | --- | --- | --- | ---"
    print " | ".join([dcterms_title, dcterms_description_abstract, dcterms_contributor_author, dcterms_date_issued, dcterms_rights_copyright, dcterms_relation_ispartofseries])

    print "\n  * getting rights statements"

    act = tree.xpath(".//premis:act", namespaces=namespaces)[0].text
    restriction = tree.xpath(".//premis:restriction", namespaces=namespaces)[0].text
    start_date = tree.xpath(".//premis:startDate", namespaces=namespaces)[0].text
    end_date = tree.xpath(".//premis:endDate", namespaces=namespaces)[0].text
    rights_granted_note = tree.xpath(".//premis:rightsGrantedNote", namespaces=namespaces)[0].text

    print "\nAct | Restriction | Start | End | Grant/restriction Note"
    print "--- | --- | --- | --- | ---"
    print " | ".join([act, restriction, start_date, end_date, rights_granted_note])

    print "\n  * splitting package into objects and metadata zips"

    # objects_dir = os.path.join(aip_dir, "data", "objects", [name for name in os.listdir(os.path.join(aip_dir, "data", "objects")) if name.startswith("digital_object_component")][0])
    # objects_zip = os.path.join(aip_dir + "-temp", "objects.7z")
    # command = [
        # "7z", "a",  # add
        # "-bd",  # disable percentage indicator
        # "-t7z",  # type of archive
        # "-y",  # assume yes on all queries
        # "-m0=bzip2",  # compression method
        # "-mtc=on", "-mtm=on", "-mta=on",  # keep timestamps (create, mod, access)
        # "-mmt=on",  # multithreaded
        # objects_zip,  # destination
        # objects_dir  # source
    # ]
    # subprocess.call(command)

    # shutil.rmtree(objects_dir)

    # metadata_zip = os.path.join(aip_dir + "-temp", "metadata.7z")
    # command = [
        # "7z", "a",  # add
        # "-bd",  # disable percentage indicator
        # "-t7z",  # type of archive
        # "-y",  # assume yes on all queries
        # "-m0=bzip2",  # compression method
        # "-mtc=on", "-mtm=on", "-mta=on",  # keep timestamps (create, mod, access)
        # "-mmt=on",  # multithreaded
        # "-x!" + objects_zip,  # exclude objects.7z
        # metadata_zip,  # destination
        # aip_dir  # source
    # ]
    # subprocess.call(command)

    # shutil.rmtree(aip_dir)

    # os.rename(aip_dir + "-temp", aip_dir)

    print "  * depositing to deep blue"

    dspace_url = "https://dev.deepblue.lib.umich.edu"

    url = dspace_url + "/RESTapi/login"
    body = {"email": dspace_username, "password": dspace_password}
    response = requests.post(url, json=body)

    dspace_token = response.text

    request = E.request(
        E.collectionId("1047"),
        E.metadata(
            E.field(
                E.name("dc.title"),
                E.value(dcterms_title)
            ),
            E.field(
                E.name("dc.description.abstract"),
                E.value(dcterms_description_abstract)
            ),
            E.field(
                E.name("dc.contributor.author"),
                E.value(dcterms_contributor_author)
            ),
            E.field(
                E.name("dc.date.issued"),
                E.value(dcterms_date_issued)
            ),
            E.field(
                E.name("dc.rights.copyright"),
                E.value(dcterms_rights_copyright)
            ),
            E.field(
                E.name("dc.relation.ispartofseries"),
                E.value(dcterms_relation_ispartofseries)
            ),
        ),
        E.bundles(
            E.bundle(
                E.name("ORIGINAL"),
                E.bitstreams(
                    E.bitstream(
                        E.name("objects.7z"),
                        E.mimeType("application/zip"),
                        E.description("Archival material.")
                    ),
                    E.bitstream(
                        E.name("metadata.7z"),
                        E.mimeType("application/zip"),
                        E.description("Administrative information. Access restricted to Bentley staff")
                    )
                )
            )
        )
    )

    package = etree.tostring(request, pretty_print=True, xml_declaration=True, encoding="utf-8")
    with open(os.path.join(aip_dir, "package.xml"), mode="w") as f:
        f.write(package)

    print "  * notifying processor"

    slack = Slacker(slack_token)
    slack.chat.post_message("#digital-processing",
        "@" + username + ": check out this item in Deep Blue dev!",
        username="Deep Blue Bot",
        icon_url="http://www.infodocket.com/wp-content/uploads/2016/09/2016-09-20_10-00-21.jpeg",
        attachments=[
            {
                "author_name": dcterms_contributor_author,
                "title": dcterms_title,
                "title_link": "",
                "text": dcterms_description_abstract
            }
        ]
    )