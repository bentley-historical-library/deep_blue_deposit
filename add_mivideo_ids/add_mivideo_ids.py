import os
from collections import defaultdict
import csv
from lxml import etree

deposit_id = ""
path_to_deposit = ""
while True:
    deposit_id = raw_input("Deposit ID: ")
    for name in os.listdir(os.path.join("R:", "MLibrary Drop", "DeepBlue")):
        if name.startswith(deposit_id):
            path_to_deposit = os.path.join("R:", "MLibrary Drop", "DeepBlue", name)
            break
        else:
            continue
    else:
        print "Enter a valid Deposit ID."
        continue
    break
    
path_to_mivideo_ids_csv = ""
while True:
    path_to_mivideo_ids_csv = raw_input("\nPath to MiVideo IDs CSV: ")
    if os.path.isfile(path_to_mivideo_ids_csv) is True or os.path.isfile(path_to_mivideo_ids_csv[1:-1]) is True:
        break
    print "Enter a valid path."
    
print "  * Generating dictionary of MiVideo IDs... "
identifier_mivideo_ids = defaultdict(list)
with open(path_to_mivideo_ids_csv, mode="r") as mivideo_ids_csv:
    reader = csv.DictReader(mivideo_ids_csv)
    for row in reader:
        identifier = row.get("IDENTIFIER.OTHER")
        mivideo_ids = row.get("MiVideo_IDs")
        for mivideo_id in mivideo_ids.split("; "):
            identifier_mivideo_ids[identifier].append(mivideo_id)

print "\nUpdating SAF"

print "  * Checking to make sure items cannot be downloaded in DeepBlue... "
for root, _, files in os.walk(path_to_deposit):
    for name in files:
        if name == "contents":
            f = open(os.path.join(root, name), mode="r")
            old_data = f.read()
            f.close()
            
            new_data = old_data.replace("Access restricted to Bentley Reading Room.", "Access restricted to Bentley staff.")
            new_data = new_data.replace("-r 'Anonymous'", "-r 'BentleyStaff'").replace("-r 'Bentley Only Users'", "-r 'BentleyStaff'")
                            
            f = open(os.path.join(root, name), mode="w")
            f.write(new_data)
            f.close()
            
print "  * Checking to make sure rights are correct in DeepBlue metadata... "
print "  * Adding MiVideo IDs to items in DeepBlue... "
for root, _, files in os.walk(path_to_deposit):
    for name in files:
        if name == "dublin_core.xml":
            tree = etree.parse(os.path.join(root, name))
            dc_rights_access = tree.xpath('//dcvalue[@element="rights"][@qualifier="access"]')[0]
            parent = dc_rights_access.getparent()
            parent.remove(dc_rights_access)
            dc_rights_access = etree.Element("dcvalue")
            dc_rights_access.attrib["element"] = "rights"
            dc_rights_access.attrib["qualifier"] = "access"
            dc_rights_access.text = "Permanently restricted."
            parent.append(dc_rights_access)
            
            dc_date_open = tree.xpath("//dcvalue[@element='date'][@qualifier='open']")[0]
            parent = dc_date_open.getparent()
            parent.remove(dc_date_open)
            dc_date_open = etree.Element("dcvalue")
            dc_date_open.attrib["element"] = "date"
            dc_date_open.attrib["qualifier"] = "open"
            dc_date_open.text = "9999-07-01"
            parent.append(dc_date_open)
            
            dublin_core = tree.xpath("//dublin_core")[0]
            dc_identifier_other = tree.xpath("//dcvalue[@element='identifier'][@qualifier='other']")[0].text
            player_id = 1455309471
            for mivideo_id in identifier_mivideo_ids.get(dc_identifier_other):
                dc_identifier_videostream = etree.Element("dcvalue")
                dc_identifier_videostream.attrib["element"] = "identifier"
                dc_identifier_videostream.attrib["qualifier"] = "videostream"
                dc_identifier_videostream.text = "https://cdnapisec.kaltura.com/p/1758271/sp/175827100/embedIframeJs/uiconf_id/29300931/partner_id/1758271?autoembed=true&entry_id={0}&playerId=kaltura_player_{1}&cache_st=1455309475&width=400&height=330&flashvars[streamerType]=auto".format(mivideo_id, player_id)
                player_id += 1
                dublin_core.append(dc_identifier_videostream)
             
            with open(os.path.join(root, name), mode="w") as ead_out:
                ead_out.write(etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding="utf-8", standalone=False))
                
print "  * Checking to make sure metadata is visible in DeepBlue... "
if path_to_deposit.endswith("-BentleyStaff"):
    os.rename(path_to_deposit, path_to_deposit.replace("-BentleyStaff", ""))
