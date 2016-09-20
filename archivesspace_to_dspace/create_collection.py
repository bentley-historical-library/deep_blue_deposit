import getpass
import json
import requests
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


#use dallas' functions to create an archivesspace session
def aspace_credentials():
    aspace_url = "http://141.211.39.87:8089"
    aspace_username = "admin"
    
    print "Connecting to: {}".format(aspace_url)
    print "Username: {}".format(aspace_username)
    
    is_correct = raw_input("Is this information correct? (y/n) ")
    
    if is_correct.lower() == "y":
        aspace_password = getpass.getpass("Enter your ArchivesSpace password: ")
        return aspace_url, aspace_username, aspace_password
    
    elif is_correct.lower() == "n":
        aspace_url = raw_input("Enter the correct ArchivesSpace URL: ")
        aspace_username = raw_input("Enter your ArchivesSpace username: ")
        aspace_password = getpass.getpass("Enter your ArchivesSpace password: ")
        return aspace_url, aspace_username, aspace_password
    
    else:
        print "Quitting"
        sys.exit()

def authenticate(aspace_url, username, password, expiring="true"):
    s = requests.session()
    auth = s.post("{0}/users/{1}/login?password={2}&expiring={3}".format(aspace_url, username, password, expiring)).json()
    session = auth.get("session")
    s.headers.update({"X-ArchivesSpace-Session":session})
    return s
    
aspace_url, username, password = aspace_credentials()
session = authenticate(aspace_url, username, password)


# use the archivesspace api to get information about the resource
resource_number = raw_input("\nEnter the ArchivesSpace resource number: ")
resource = session.get("{0}/repositories/2/resources/{1}".format(aspace_url, resource_number)).json()

resource_title = resource.get("title")
    
resource_abstract = ""
resource_bioghist = ""
for note in resource.get("notes"):
    if note.get("type") == "abstract":
        resource_abstract = note.get("content")[0]
    elif note.get("type") == "bioghist":
        resource_bioghist = note.get("subnotes")[0].get("content")
        
collection_id = resource.get("ead_id").split("-")[2]


# logout
session.post("{}/logout".format(aspace_url))


# create the dspace collection
def dspace_credentials():
    dspace_url = "https://dev.deepblue.lib.umich.edu"
    dspace_username = "eckardm"
    
    print "\nConnecting to: {}".format(dspace_url)
    print "Username: {}".format(dspace_username)
    
    is_correct = raw_input("Is this information correct? (y/n) ")
    
    if is_correct.lower() == "y":
        dspace_password = getpass.getpass("Enter your DSpace password: ")
        return dspace_url, dspace_username, dspace_password
    
    elif is_correct.lower() == "n":
        dspace_url = raw_input("Enter the correct DSpace URL: ")
        dspace_username = raw_input("Enter your DSpace username: ")
        dspace_password = getpass.getpass("Enter your DSpace password: ")
        return dspace_url, dspace_username, dspace_password
    
    else:
        print "Quitting"
        sys.exit()
        
dspace_url, dspace_username, dspace_password = dspace_credentials()

driver = webdriver.Firefox()
if "dev" in dspace_url:
    driver.get("{}/admin/collection?createNew&communityID=34".format(dspace_url))
else:
    driver.get("{}/admin/collection?createNew&communityID=4".format(dspace_url))

element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "loginSubmit")))
driver.find_element_by_id("login").send_keys(dspace_username)
driver.find_element_by_id("password").send_keys(dspace_password)
driver.find_element_by_id("loginSubmit").click()

if "dev" in dspace_url:
    driver.get("{}/admin/collection?createNew&communityID=34".format(dspace_url))
else:
    driver.get("{}/admin/collection?createNew&communityID=4".format(dspace_url))

capitalized_title = ""
if "dev" in dspace_url:
    capitalized_title = "ASpace TEST: " + resource_title.replace("papers", "Papers").replace("sound recordings", "Sound Recordings").replace("records", "Records").replace("collection", "Collection")
else:
    capitalized_title = resource_title.replace("papers", "Papers").replace("sound recordings", "Sound Recordings").replace("records", "Records").replace("collection", "Collection")
driver.find_element_by_name("name").send_keys(capitalized_title)

copyright_text = """
<h2>Please note:</h2>
<p>Copyright has been transferred to the Regents of the University of Michigan.</p>
<br />
<br />

<p>
Access to digitized sound recordings may be limited to the reading room of the <a href="http://bentley.umich.edu/">Bentley Historical Library</a>, located on the Ann Arbor campus of the University of Michigan.</p>"""
driver.find_element_by_name("copyright_text").send_keys(copyright_text)

driver.find_element_by_name("license").send_keys("As the designated coordinator for this Deep Blue Collection, I am authorized by the Community members to serve as their representative in all dealings with the Repository. As the designee, I ensure that I have read the Deep Blue policies. Furthermore, I have conveyed to the community the terms and conditions outlined in those policies, including the language of the standard deposit license quoted below and that the community members have granted me the authority to deposit content on their behalf.")
driver.find_element_by_name("submit_save").click()

element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "submit_create_admin")))
driver.find_element_by_name("submit_create_admin").click()

element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "aspect_administrative_group_EditGroupForm_field_submit_save")))
driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_query").send_keys("shallcro")
driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_submit_search_epeople").click()
if "dev" in dspace_url:
    driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_submit_add_eperson_366").click()
else:
    driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_submit_add_eperson_7132").click()
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "aspect_administrative_group_EditGroupForm_field_submit_save")))
driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_query").clear()
driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_query").send_keys("eckardm")
driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_submit_search_epeople").click()
if "dev" in dspace_url:
    driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_submit_add_eperson_4864").click()
else:
    driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_submit_add_eperson_9927").click()
driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_submit_save").click()

element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "submit_return")))
driver.find_element_by_name("submit_return").click()

element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, capitalized_title)))
driver.find_element_by_link_text(capitalized_title).click()

element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "aspect_discovery_CollectionSearch_div_collection-search")))
handle = driver.find_element_by_id("aspect_discovery_CollectionSearch_div_collection-search").get_attribute("action").split("/")[5]

if "dev" in dspace_url:
    print "\nCreating: TEMP-BOGUS/{}".format(handle)
else:
    print "\nCreating: 2027.42/{}".format(handle)

element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Edit Collection")))
driver.find_element_by_link_text("Edit Collection").click()

element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "aspect_administrative_collection_EditCollectionMetadataForm_field_submit_save")))

introductory_text = '''
<p>
<form style="display:inline" action="http://deepblue.lib.umich.edu/handle/2027.42/''' + handle + '''/browse?">
<input type="submit" value="View all items in this collection"/>
</form>
</p>
<br />


<p><img src="http://deepblue.lib.umich.edu/static/image/bentley-banner.jpg" alt="Bentley Historical Library banner" /></p>

<h2>''' + resource_title + """</h2>

<p>The materials in this online repository form part of a larger """ + resource_title.replace("Papers", "").replace("Sound Recordings", "").replace("Records", "").replace("Collection", "") + '''record group held by the <a href="http://bentley.umich.edu/">Bentley Historical Library</a>.  For a more complete index to the materials, please consult the collection's <a href="http://quod.lib.umich.edu/b/bhlead/umich-bhl-''' + collection_id + '''">online finding aid</a>.
</p>

<p>
For questions or more information, please contact the Bentley Historical Library's <a href="mailto:bentley.ref@umich.edu">Division of Reference and Access Services</a>
</p>

<p>
<b>Abstract:</b><br />''' + resource_abstract.replace("&amp;", "&") + """
</p>

<p>
<b>History / Biography:</b><br />""" + resource_bioghist.replace("\n\n", "\n").replace("\n", "</p><p>").replace("&amp;", "&") + """
</p>"""

driver.find_element_by_name("introductory_text").send_keys(introductory_text)
driver.find_element_by_id("aspect_administrative_collection_EditCollectionMetadataForm_field_submit_save").click()

driver.close()


# create collection level digital object
session = authenticate(aspace_url, username, password)

digital_object = {}
digital_object["title"] = resource_title

digital_object["digital_object_id"] = ""
digital_object["file_versions"] = []
if "dev" in dspace_url:
    digital_object["digital_object_id"] = "http://hdl.handle.net/TEMP-BOGUS/{}".format(handle)
    digital_object["file_versions"].append({"file_uri":"http://hdl.handle.net/TEMP-BOGUS/{}".format(handle), "xlink_show_attribute":"new", "xlink_actuate_attribute":"onRequest"})
else:
    digital_object['digital_object_id'] = "http://hdl.handle.net/TEMP-BOGUS/{}".format(handle)
    digital_object['file_versions'].append({"file_uri":"http://hdl.handle.net/TEMP-BOGUS/{}".format(handle), "xlink_show_attribute":"new", "xlink_actuate_attribute":"onRequest"})

digital_object['publish'] = False

digital_object_post = session.post("{}/repositories/2/digital_objects".format(aspace_url), data=json.dumps(digital_object)).json()
print digital_object_post
print "\nCreating: " + digital_object_post.get("uri")

dig_obj_instance = {'instance_type':'digital_object', 'digital_object':{'ref':digital_object_post.get("uri")}}

resource['instances'].append(dig_obj_instance)
updated_resource = json.dumps(resource)

archival_object_update = session.post("{0}/repositories/2/resources/{1}".format(aspace_url, resource_number), data=updated_resource).json()


# logout
session.post("{}/logout".format(aspace_url))