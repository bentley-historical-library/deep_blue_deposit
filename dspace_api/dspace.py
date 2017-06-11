import requests
import json
from pprint import pprint

from credentials import username, password

dspace_url = "https://dev.deepblue.lib.umich.edu"

collection = "TEMP-BOGUS/304433"

handle_1 = "TEMP-BOGUS/304434"
handle_2 = "TEMP-BOGUS/304435"
handle_3 = "TEMP-BOGUS/304436"

from django.db import models

# Log in to get DSpace REST API token
url = dspace_url + "/RESTapi/login"
body = {"email": username, "password": password}
response = requests.post(url, json=body)
token = response.text

# Fetch bitstream information for item
url = dspace_url + "/RESTapi/handle/" + handle_3
headers = {
    "Accept": "application/json",
    "rest-dspace-token": token
}
params = {"expand": "bitstreams"}
response = requests.get(url, headers=headers, params=params)

for bitstream in response.json()["bitstreams"]:
    
    # Add bitstream description to objects when depositing to DSpace
    if bitstream["name"] == "objects.7z":
        url = dspace_url + bitstream["link"] 
        body = bitstream
        body["description"] = "Archival materials."
        response = requests.put(url, headers=headers, json=body)
        print "objects.7z", response.status_code

    # Update bitstream policies
    if bitstream["name"] == "metadata.7z":
        url = dspace_url + bitstream["link"]
        body = bitstream
        body["policies"] = [{"action":"READ", "groupId":"1335", "rpType":"TYPE_CUSTOM"}]
        # Add bitstream description to metadata when depositing to DSpace
        body["description"] = "Administrative information."
        response = requests.put(url, headers=headers, json=body)  
        print "metadata.7z", response.status_code

        # # Delete anonymous policy
        # url = dspace_url + bitstream["link"] + "/policy"
        # response = requests.get(url, headers=headers)
        # id = [policy["id"] for policy in response.json() if policy["groupId"] == 0][0]
        # url = dspace_url + bitstream["link"] + "/policy/" + str(id)
        # response = requests.delete(url, headers=headers, json=body)  
        # print "anonymous policy", response.status_code