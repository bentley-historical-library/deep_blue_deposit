import os
from lxml import etree
import shutil

deep_blue_saf_staging = os.path.join("R:", "MLibrary Drop", "DeepBlue", "deepblue_saf_staging")
deep_blue_saf_temp = os.path.join("R:", "MLibrary Drop", "DeepBlue", "deepblue_saf_temp")
deep_blue_saf_transfer = os.path.join("R:", "MLibrary Drop", "DeepBlue", "deepblue_saf_transfer")

for root, dirs, files in os.walk(deep_blue_saf_staging):
    for name in files:
        if name.startswith("METS") and name.endswith("xml") and os.path.split(root)[1] == "data":
            
            aip_path = os.path.split(root)[0]
            aip_name = os.path.split(aip_path)[1]
            mets_path = os.path.join(root, name)
            objects_path = os.path.join(root, "objects")
            logs_path = os.path.join(root, "logs")
            thumbnails_path = os.path.join(root, "thumbnails")
            
            mets_tree = etree.parse(mets_path)
            mets_root = mets_tree.getroot()
            
            rights_statement = mets_root.find('.//premis:rightsStatement', namespaces={"premis": "info:lc/xmlns/premis-v2"})
            if rights_statement is None:
                print aip_name, "Check this one out! It looks like it should be open."
                continue
                
            rights_granted = rights_statement.findall("premis:rightsGranted", namespaces={"premis": "info:lc/xmlns/premis-v2"})
            if len(rights_granted) > 1:
                print aip_name, "Check this one out! It looks like it has more than one rights granted."
                continue

            act = rights_granted[0].find("premis:act", namespaces={"premis": "info:lc/xmlns/premis-v2"}).text
            restriction = rights_granted[0].find("premis:restriction", namespaces={"premis": "info:lc/xmlns/premis-v2"}).text
            start_date = rights_granted[0].find("premis:termOfRestriction/premis:startDate", namespaces={"premis": "info:lc/xmlns/premis-v2"}).text
            end_date = rights_granted[0].find("premis:termOfRestriction/premis:endDate", namespaces={"premis": "info:lc/xmlns/premis-v2"}).text
            rights_granted_note = rights_granted[0].find("premis:rightsGrantedNote", namespaces={"premis": "info:lc/xmlns/premis-v2"}).text
            
            # make working copy
            print "Making working copy of {}...".format(aip_name)
            shutil.copytree(aip_path, os.path.join(deep_blue_saf_temp, aip_name))
            
            