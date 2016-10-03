import os
from lxml import etree
import shutil
from zipfile import ZipFile
import datetime
import pyttsx

mounting = ["sudo", "mount",
    "-t", "cifs",
    "-o", "username=eckardm,domain=umroot,rw,uid=eckardm,gid=eckardm",
    "//bhl-digitalarchive.m.storage.umich.edu/bhl-digitalarchive",
    "/media/Digital_Archive"]
if os.path.isdir(os.path.join(os.path.sep,
"media", "Digital_Archive")) is False:
    os.system(" ".join(mounting))

deep_blue_saf_staging = os.path.join(
    os.path.sep,
    "media", "Digital_Archive",
    "MLibrary Drop", "DeepBlue", "deepblue_saf_staging")
deep_blue_saf_temp = os.path.join(
    os.path.sep,
    "media", "Digital_Archive",
    "MLibrary Drop", "DeepBlue", "deepblue_saf_temp")
deep_blue_saf_transfer = os.path.join(
    os.path.sep,
    "media", "Digital_Archive",
    "MLibrary Drop", "DeepBlue", "deepblue_saf_transfer")

for root, _, files in os.walk(deep_blue_saf_staging):
    for name in files:
        if name.startswith("METS") and \
        name.endswith("xml") and \
        os.path.split(root)[1] == "data":

            aip_path = os.path.split(root)[0]
            aip_name = os.path.split(aip_path)[1]

            # get bag info
            mets_path = os.path.join(root, name)

            mets_tree = etree.parse(mets_path)
            mets_root = mets_tree.getroot()

            # to-do: parse archivesspace info

            # parse rights statements
            rights_statement = mets_root.find(
                ".//premis:rightsStatement",
                namespaces={"premis": "info:lc/xmlns/premis-v2"})
            if rights_statement is None:
                print(("{} should be open".format(aip_name)))
                continue

            rights_granted = rights_statement.findall(
                "premis:rightsGranted",
                namespaces={"premis": "info:lc/xmlns/premis-v2"})
            if len(rights_granted) > 1:
                print(("{0} has {1} acts".format(
                    aip_name, len(rights_granted))))
                continue

            act = rights_granted[0].find(
                "premis:act",
                namespaces={"premis": "info:lc/xmlns/premis-v2"}).text
            restriction = rights_granted[0].find(
                "premis:restriction",
                namespaces={"premis": "info:lc/xmlns/premis-v2"}).text
            start_date = rights_granted[0].find(
                "premis:termOfRestriction/premis:startDate",
                namespaces={"premis": "info:lc/xmlns/premis-v2"}).text
            end_date = rights_granted[0].find(
                "premis:termOfRestriction/premis:endDate",
                namespaces={"premis": "info:lc/xmlns/premis-v2"}).text
            rights_granted_note = rights_granted[0].find(
                "premis:rightsGrantedNote",
                namespaces={"premis": "info:lc/xmlns/premis-v2"}).text

            if not ((restriction == "Conditional" and
            rights_granted_note.split(":")[0] == "Reading-Room Only") or
            (restriction == "Conditional" and
            rights_granted_note.split(":")[0] == "UM Only") or
            (restriction == "Conditional" and
            rights_granted_note.split(":")[0] == "Streaming Only") or
            (restriction == "Disallow" and
            (rights_granted_note.startswith("ER") or
            rights_granted_note.startswith("PR") or
            rights_granted_note.startswith("SR") or
            rights_granted_note.startswith("CR")))):
                print(("{0} has non-standard rights statement: {1}".format(
                    aip_name, rights_granted_note)))
                continue

            # make working copy
            print(("Transforming {} to SAF...".format(aip_name)))
            print("  * Making working copy...")
            shutil.copytree(
                aip_path,
                os.path.join(deep_blue_saf_temp, aip_name))

            # get more bag info
            aip_path = os.path.join(deep_blue_saf_temp, aip_name)

            mets_path = os.path.join(root.replace(
                "deep_blue_saf_staging", "deep_blue_saf_temp"), name)
            logs_path = os.path.join(root.replace(
                "deep_blue_saf_staging", "deep_blue_saf_temp"), "logs")
            thumbnails_path = os.path.join(root.replace(
                "deep_blue_saf_staging", "deep_blue_saf_temp"), "thumbnails")

            objects_path = os.path.join(root.replace(
                "deep_blue_saf_staging", "deep_blue_saf_temp"), "objects")

            # zip stuff
            print("  * AIP repackaging...")
            for root, _, files in os.walk(objects_path):
                for name in files:
                    with ZipFile(os.path.join(aip_path, "objects.zip"),
                    mode="a") as objects_zip:
                        objects_zip.write(os.path.join(
                            os.path.sep, root, name))

            for path in [mets_path, logs_path, thumbnails_path]:
                for root, _, files in os.walk(path):
                    for name in files:
                        with ZipFile(os.path.join(aip_path, "metadata.zip"),
                            mode="a") as metadata_zip:
                            metadata_zip.write(os.path.join(
                                os.path.sep, root, name))

            # clean
            payload = os.path.join(aip_path, "data")
            shutil.rmtree(payload)

            tags = [
                os.path.join(aip_path, "bag-info.txt"),
                os.path.join(aip_path, "bagit.txt"),
                os.path.join(aip_path, "manifest-sha256.txt"),
                os.path.join(aip_path, "tagmanifest-md5.txt")]
            for tag in tags:
                    os.remove(tag)

            # to-do: make the rest of the dublin core
            print("  * Converting to SAF...")
            dublin_core = etree.Element("dublin_core")

            dc_title = mets_root.find(
                ".//dc:title",
                namespaces={"dc": "http://purl.org/dc/elements/1.1/"}).text
            etree.SubElement(
                dublin_core, "dcvalue",
                element="title",
                qualifier="none").text = dc_title

            dc_date_issued = mets_root.find(
                ".//dc:date",
                namespaces={"dc": "http://purl.org/dc/elements/1.1/"}).text
            etree.SubElement(
                dublin_core, "dcvalue",
                element="date",
                qualifer="issued").text = dc_date_issued

            dc_contributor_author = mets_root.find(
                ".//dc:creator",
                namespaces={"dc": "http://purl.org/dc/elements/1.1/"}).text
            etree.SubElement(
                dublin_core, "dcvalue",
                element="contributor",
                qualifer="author").text = dc_contributor_author

            dc_rights_access = rights_granted_note
            etree.SubElement(
                dublin_core, "dcvalue",
                element="rights",
                qualifer="access").text = dc_rights_access

            dc_date_open = ""
            if restriction == "Disallow":
                dc_date_open = end_date
            else:
                dc_date_open == datetime.datetime.today().strftime('%Y-%m-%d')
            etree.SubElement(
                dublin_core, "dcvalue",
                element="date",
                qualifer="open").text = dc_date_open

            if restriction == "Disallow":
                etree.SubElement(
                    dublin_core, "dcvalue",
                    element="description",
                    qualifer="restriction").text = "RESTRICTED"

            dc_rights_copyright = "This content may be under copyright. "
            "Researchers are responsible for determining the appropriate use "
            "or reuse of materials. Please consult the collection finding aid "
            "or catalog record for more information."
            etree.SubElement(
                dublin_core, "dcvalue",
                element="rights",
                qualifier="copyright").text = dc_rights_copyright

            dc_description_abstract = ""
            etree.SubElement(
                dublin_core, "dcvalue",
                element="description",
                qualifier="abstract").text = dc_description_abstract

            dc_relation_ispartof = ""
            etree.SubElement(
                dublin_core, "dcvalue",
                element="relation",
                qualifier="ispartof").text = dc_relation_ispartof

            dublin_core = etree.tostring(dublin_core,
                pretty_print=True,
                xml_declaration=True, encoding="utf-8", standalone=False)

            with open(os.path.join(aip_path, "dublin_core.xml"),
                mode="w") as f:
                f.write(dublin_core)

            # make license
            with open(os.path.join(aip_path, "license.txt"), mode="w") as f:
                f.write("As the designated coordinator for this Deep Blue "
                    "Collection, I am authorized by the Community members to "
                    "serve as their representative in all dealings with the "
                    "Repository. As the designee, I ensure that I have read "
                    "the Deep Blue policies. Furthermore, I have conveyed to "
                    "the community the terms and conditions outlined in those "
                    "policies, including the language of the standart deposit "
                    "license quoted below and that the community members have "
                    "granted me the authority to deposit content on their "
                    "behalf.")
                f.write("\n")

            # make contents
            with open(os.path.join(aip_path, "contents"), mode="w") as f:
                f.write("metadata.zip")
                f.write("\t")
                f.write("description:Administrative information. "
                    "Access restricted to Bentley staff.")
                f.write("\t")
                f.write("permissions:-r 'BentleyStaff'")
                f.write("\n")

                if restriction == "Conditional" and \
                rights_granted_note.split(":")[0] == "Reading-Room Only":
                    f.write("objects.zip")
                    f.write("\t")
                    f.write("description:Access restricted to "
                        "Bentley Reading Room.")
                    f.write("\t")
                    f.write("permissions:-r 'Bentley Only Users'")
                    f.write("\n")

                elif restriction == "Conditional" and \
                rights_granted_note.split(":")[0] == "UM Only":
                    f.write("objects.zip")
                    f.write("\t")
                    f.write("description:Access restricted to "
                        "UM users.")
                    f.write("\t")
                    f.write("permissions:-r 'BentleyStaff'")
                    f.write("\n")

                elif restriction == "Conditional" and \
                rights_granted_note.split(":")[0] == "Streaming Only":
                    f.write("objects.zip")
                    f.write("\t")
                    f.write("description:Download restricted to"
                        "Bentley Staff.")
                    f.write("\t")
                    f.write("permissions:-r 'BentleyStaff'")
                    f.write("\n")

                elif restriction == "Disallow":
                    f.write("objects.zip")
                    f.write("\t")
                    f.write("description:"
                        "Access restricted to Bentley Staff.")
                    f.write("\t")
                    f.write("permissions:-r 'BentleyStaff'")
                    f.write("\n")

            # rename folder to make it more semantic

            # move to saf transfer
            print("  * Moving to transfer location...")
            shutil.copytree(
                aip_path,
                os.path.join(deep_blue_saf_transfer, aip_name))
            shutil.rmtree(aip_path)

# e-mail jose
print(
    "\n"
    "    ,     ,\n"
    "   (\____/) ______________\n"
    "    (_oo_) /              \\\n"
    "      (O) <  E-mail Jose!  )\n"
    "    __||__ \__\)__________/\n"
    " []/______\[] /\n"
    " / \______/ \/\n"
    " /    /_\\\n"
    "(\   /___\\")

engine = pyttsx.init()
engine.setProperty("rate", 70)
engine.say("E-mail Jose!")
engine.runAndWait()

            # to-do: create then update digital object in archivesspace
            # (this might need to be a new script)
