from collections import defaultdict
import csv
import os

depositid_handle = {}
depositid_depositiditems = defaultdict(list)

with open("BLItems.csv", mode="r") as BLItems:
    reader = csv.DictReader(BLItems)
    for row in reader:
        depositid = ""
        # duderstadt types
        if not row.get("Identifier_other"):
            continue
        # semicolon types
        elif ";" in row.get("Identifier_other"):
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
            
    
# do these by hand: 
# 2027.42/93587,87250_0002; 87250_0003,Men's Glee Club (University of Michigan) Records
# 2027.42/106596,2014014_0001_0002; 2014014_0001_0002,Lawrence Witt and Laura Edge Papers
# 2027.42/106529,9577_0002_0004; 9577_0002_0004,Dale Leslie Papers
