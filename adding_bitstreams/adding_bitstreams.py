from collections import defaultdict, Counter
import csv
import os
import shutil

depositid_handle = {}
depositid_depositiditems = defaultdict(list)

do_these_by_hand = []

deposititemids = []

with open("BLItems.csv", mode="r") as BLItems:
    reader = csv.DictReader(BLItems)
    for row in reader:
    
        deposititemids.append(row.get("Identifier_other"))
        
        depositid = ""
        
        # duderstadt types
        if not row.get("Identifier_other"):
            continue
        # semicolon types
        elif ";" in row.get("Identifier_other"):
            do_these_by_hand.append(row.get("Identifier_other"))
            continue
        # wtf!?
        elif "Collected materials - Military documents - Detwiler, Samuel, circa 1945" in row.get("Identifier_other"):
            continue
        
        # reel-to-reel types
        elif "-" in row.get("Identifier_other"):
            depositid = row.get("Identifier_other")
        # digital deposit it and item id types
        elif len(row.get("Identifier_other").split("_")) == 3:
            depositid = "_".join(row.get("Identifier_other").split("_")[:-1])
        # just digital deposit types
        elif len(row.get("Identifier_other").split("_")) == 2:
            depositid = row.get("Identifier_other")
            
        depositid_handle[depositid] = row.get("Handle")
        
        depositid_depositiditems[depositid].append(row.get("Identifier_other"))

deposititemids_that_are_not_unique = []

for deposititemid, count in Counter(deposititemids).most_common():
    if count > 1:
        deposititemids_that_are_not_unique.append(deposititemid)
        
'''
 -A or --addbitstreams  Adds bitstreams listed in the contents file with the bitstream metadata cited there.'''

depositids_not_in_deepblue = []

archive_directory = os.path.join("R:", "MLibrary Drop", "DeepBlue", "adding_bitstreams")
 
for log in os.listdir("logs"):
    for admin_info in os.listdir(os.path.join("logs", log)):
        
        depositid = "_".join([log, admin_info.split(".")[0]])
        
        if depositid not in depositid_depositiditems:
            depositids_not_in_deepblue.append(depositid)
            continue
            
        count = 1
        for depositiditem in depositid_depositiditems.get(depositid):
            if depositiditem in deposititemids_that_are_not_unique:
                item = "_".join([depositiditem + "-" + str(count), "to", depositid_handle.get(depositid).replace(".", "-").replace("/", "-")]) + "-BentleyStaff"
                count += 1
            else:
                item = "_".join([depositiditem, "to", depositid_handle.get(depositid).replace(".", "-").replace("/", "-")]) + "-BentleyStaff"
            
            os.mkdir(os.path.join(archive_directory, item))
            
            shutil.copy(os.path.join("logs", log, admin_info), os.path.join(archive_directory, item))
            
            with open(os.path.join(archive_directory, item, "contents"), mode="w") as contents:
                contents.write("\t".join([admin_info, "description:Administrative information. Access restricted to Bentley staff.", "permissions:-r 'BentleyStaff'"]))

'''
STILL NEED TO ACCOUNT FOR ITEMS THAT ALREADY HAVE ADMINISTRATIVE INFORMATION!!!'''
                