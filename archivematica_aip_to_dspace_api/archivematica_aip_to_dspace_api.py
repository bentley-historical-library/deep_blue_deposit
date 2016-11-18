import os
import subprocess
from lxml import etree
import shutil

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

    print "processing " + aip_dir

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

    accession_no = [event.xpath("./premis:eventOutcomeInformation/premis:eventOutcomeDetail/premis:eventOutcomeDetailNote", namespaces=namespaces)[0].text.split("#")[1] for event in tree.xpath("//premis:event", namespaces=namespaces) if event.xpath("./premis:eventType", namespaces=namespaces)[0].text == "registration"][0]

    dcterms_title = tree.xpath(".//dc:title", namespaces=namespaces)[0].text
    dcterms_description_abstract = ""
    dcterms_contributor_author =  tree.xpath(".//dc:creator", namespaces=namespaces)[0].text
    dcterms_date_issued = tree.xpath(".//dc:date", namespaces=namespaces)[0].text
    dcterms_rights_copyright = tree.xpath(".//dc:rights", namespaces=namespaces)[0].text
    dcterms_relation_ispartofseries = ""

    print "  * getting permissions"

    reading_room = False
    university_of_michigan = False
    bentley_digital_media_library = False
    um_records = False  # also need date and DISALLOW, althought the latter not 'till later

    act = tree.xpath(".//premis:act", namespaces=namespaces)[0].text
    restriction = tree.xpath(".//premis:restriction", namespaces=namespaces)[0].text
    start_date = tree.xpath(".//premis:startDate", namespaces=namespaces)[0].text
    end_date = tree.xpath(".//premis:endDate", namespaces=namespaces)[0].text
    rights_granted_note = tree.xpath(".//premis:rightsGrantedNote", namespaces=namespaces)[0].text

    print "  * splitting package into objects and metadata zips"

    objects_dir = os.path.join(aip_dir, "data", "objects", [name for name in os.listdir(os.path.join(aip_dir, "data", "objects")) if name.startswith("digital_object_component")][0])

    objects_zip = os.path.join(aip_dir, "objects.7z")

    command = [
        "7z", "a",  # add
        "-bd",  # disable percentage indicator
        "-t7z",  # type of archive
        "-y",  # assume yes on all queries
        "-m0=bzip2",  # compression method
        "-mtc=on", "-mtm=on", "-mta=on",  # keep timestamps (create, mod, access)
        "mmt=on",  # multithreaded
        objects_zip,  # destination
        objects_dir  # source
    ]
    subprocess.call(command)

    # shutil.rmtree(objects_dir)

    metadata_zip = os.path.join(aip_dir, "metadata.7z")
    command = [
        "7z", "a",  # add
        "-bd",  # disable percentage indicator
        "-t7z",  # type of archive
        "-y",  # assume yes on all queries
        "-m0=bzip2",  # compression method
        "-mtc=on", "-mtm=on", "-mta=on",  # keep timestamps (create, mod, access)
        "mmt=on",  # multithreaded
        "-x!objects.7z",  # exclude objects.7z
        metadata_zip,  # destination
        aip_dir  # source
    ]
    subprocess.call(command)
