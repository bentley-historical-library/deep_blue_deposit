from lxml import etree
import sys

deep_blue_saf_staging = os.path.join("R:", "MLibrary Drop", "DeepBlue", "deepblue_saf_staging")
deep_blue_saf_transfer = os.path.join("R:", "MLibrary Drop", "DeepBlue", "deepblue_saf_transfer")

NAMESPACES = {
    "mets": "http://www.loc.gov/METS/",
    "premis": "info:lc/xmlns/premis-v2",
}

tree = etree.parse("readingRoom.xml")
root = tree.getroot()

rights_statement = root.find('.//premis:rightsStatement', namespaces=NAMESPACES)
if rights_statement is None:
    print "Check this one out--should be open."
    sys.exit()
    
rights_granted = rights_statement.findall("premis:rightsGranted", namespaces=NAMESPACES)
if len(rights_granted) > 1:
    print "Check this one out--more than one rights granted."
    sys.exit()

act = rights_granted[0].find("premis:act", namespaces=NAMESPACES).text
restriction = rights_granted[0].find("premis:restriction", namespaces=NAMESPACES).text
start_date = rights_granted[0].find("premis:termOfRestriction/premis:startDate", namespaces=NAMESPACES).text
end_date = rights_granted[0].find("premis:termOfRestriction/premis:endDate", namespaces=NAMESPACES).text
rights_granted_note = rights_granted[0].find("premis:rightsGrantedNote", namespaces=NAMESPACES).text
