import os
from tqdm import *
from lxml import etree
from time import strptime, strftime
import shutil

metadata_directory = os.path.join("reel_to_reel_deepblue_xml")
target_directory = os.path.join("R:", "MLibrary Drop", "reel-to-reel") # WILL NEED TO CHANGE THIS

already_done = [
    "02115", 
]    

batch_one = [
    "9940", 
    "85164", 
    "85746", 
    "86746", 
    "95107", 
    "851100", 
    "851981", 
    "2008043", 
    "2012151", 
    "00135", 
    "0434", 
    "0580", 
    "0606", 
    "850", 
    "03171", 
    "8654", 
    "8667", 
    "8738"
]

batch_two = [
    "85530", 
    "85624", 
    "85874", 
    "86393", 
    "86734", 
    "87250", 
    "87278", 
    "88142", 
    "851326", 
    "851510", 
    "851649", 
    "851843", 
    "851917", 
    "0080", 
    "0445", 
    "0475", 
    "8635", 
    "8730", 
    "9580", 
    "9588", 
    "9594", 
    "9616", 
    "85177", 
    "85187", 
    "85193", 
    "85444", 
    "85529"
]

batch_three = [
    "90139", 
    "93268", 
    "851378", 
    "851647", 
    "851732", 
    "852178", 
    "852228", 
    "2009039", 
    "0601", 
    "0648", 
    # "02115", 
    "06100", 
    "8514", 
    "8740", 
    "8742", 
    "9859", 
    "9997", 
    "85232", 
    "85287", 
    "85519", 
    "85686", 
    "85816", 
    "86314", 
    "86996", 
    "87140", 
    "87209", 
    "87245", 
    "87296", 
    "87334"
]

batch_four = [
    "85199", 
    "85506", 
    "85817", 
    "851077", 
    "921506", 
    "2009045", 
    "2010191", 
    "2010215", 
    "0732", 
    "8634", 
    "85188"
]

metadata = [filename for filename in os.listdir(metadata_directory)]

for metadatum in metadata:

    tree = etree.parse(os.path.join(metadata_directory, metadatum))
    
    # collection id
    item = tree.xpath("//dc.identifier.other")[0].text
    collection_id = item.split("-")[0]
    
    if collection_id in batch_three and collection_id not in already_done: # LET'S GO THROUGH BATCHES ONE-BY-ONE
        source_directory = os.path.join("R:", "digitization", "Audio", "Vendor Digitization", "Reel-to-Reel Project", "Batch 3", "20140117") # DON'T FORGET TO CHANGE THIS
    
        print "Collection: " + collection_id
    
        # make collection
        collection = "archive_dir_2027-42_" + tree.xpath("//parent_collection")[0].text.split("/")[1] + "-BentleyStaff"
        
        if collection not in os.listdir(target_directory):
            os.makedirs(os.path.join(target_directory, collection))
        
        # make item
        os.makedirs(os.path.join(target_directory, collection, item))
        
        # license
        with open(os.path.join(target_directory, collection, item, "license.txt"), mode="w") as f:
            
            f.write("As the designated coordinator for this Deep Blue Collection, I am authorized by the Community members to serve as their representative in all dealings with the Repository. As the designee, I ensure that I have read the Deep Blue policies. Furthermore, I have conveyed to the community the terms and conditions outlined in those policies, including the language of the standard deposit license quoted below and that the community members have granted me the authority to deposit content on their behalf.\n")
            
        # contents
        bitstreams = tree.xpath("//bitstream")
        with open(os.path.join(target_directory, collection, item, "contents"), mode="w") as f:
            f.write("license.txt\n")
            
            print "Item: " + item
            
            for bitstream in bitstreams:
                filename = bitstream.xpath("dc.title.filename")[0].text
                f.write(filename)
                f.write("\tdescription:" + bitstream.xpath("dc.description.filename")[0].text.encode("utf-8") + ". Access restricted to Bentley staff.")
                f.write("\tpermissions:-r 'BentleyStaff'\n")
                
                # copy files

                shutil.copyfile(os.path.join(source_directory, collection_id, item, filename), os.path.join(target_directory, collection, item, filename))
        
        # dublin core
        dublin_core = tree
        
        dublin_core.xpath("//audio_item")[0].tag = "dublin_core"
        
        # this is no longer useful
        parent_collection = dublin_core.xpath("//parent_collection")[0]
        parent_collection.getparent().remove(parent_collection)
        
        # don't need these since they are restricted pretty much indefinitely
        dc_date_open = dublin_core.xpath("//dc.date.open")[0]
        dc_date_open.getparent().remove(dc_date_open)
        
        # needs to be iso format
        dc_date_created = dublin_core.xpath("//dc.date.created")[0]
        dc_date_created.text = strftime("%Y-%m-%d", strptime(dc_date_created.text, "%m/%d/%Y"))
        
        # gets added automatically
        dc_owningcollname = dublin_core.xpath("//dc.owningcollname")[0]
        dc_owningcollname.getparent().remove(dc_owningcollname)
        
        # jim prefers it if handles are added this way
        dc_description = dublin_core.xpath("//dc.description")[0]
        dc_description.text = dc_description.text.replace("http://deepblue.lib.umich.edu/handle/2027.42/108126", "http://hdl.handle.net/2027.42/108126")
        
        videostreams = dublin_core.xpath("//dc.identifier.videostream")
        for videostream in videostreams:
            dc_identifier_videostream = etree.Element("dc.identifier.videostream")
            dc_identifier_videostream.text = videostream.text
            dublin_core.xpath("//dublin_core")[0].append(dc_identifier_videostream)
            
        bitstreams = dublin_core.xpath("//bitstream")
        for bitstream in bitstreams:
            bitstream.getparent().remove(bitstream)
            
        dc_elements = dublin_core.xpath("//dublin_core/*")
        for dc_element in dc_elements:
            dc_element.attrib["element"] = dc_element.tag.split(".")[1]
            
            if dc_element.tag == "dc.abstract":
                dc_element.attrib["element"] = "description"
                dc_element.attrib["qualifier"] = "abstract"
                
            elif len(dc_element.tag.split(".")) == 3:
                dc_element.attrib["qualifier"] = dc_element.tag.split(".")[2]
            else:
                dc_element.attrib["qualifier"] = "none"
            dc_element.tag = "dcvalue"
        
        with open(os.path.join(target_directory, collection, item, "dublin_core.xml"), mode="w") as f:
            f.write(etree.tostring(dublin_core, pretty_print=True, xml_declaration=True, encoding='utf-8', standalone=False))
            
        print "\n"
