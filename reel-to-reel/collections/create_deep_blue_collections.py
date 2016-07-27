import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

collections_in_deepblue = ["0080", "0601", "02115"]

results = []

count = 1

with open("collections_not_in_deepblue-2.csv", mode="rb") as collections_not_in_deepblue:
    reader = csv.DictReader(collections_not_in_deepblue)
    for row in reader:
        
        id = str(row.get("id", "").strip())
        ead = row.get("ead", "").strip()
        
        if id not in collections_in_deepblue and id != "2012151":
            with open(os.path.join("deepblue_html", id + ".html"), mode = "rb") as deepblue_html:
                read_data = deepblue_html.read().replace("</p>\r\n\t\t<h2>Please note:</h2>", "\r\n\t\t<h2>Please note:</h2>").replace("\t", "")
                
                title = read_data.split("<h2>")[1].split("</h2>")[0].strip()
                print "(" + str(count) + "/48) " + title + "..."
                            
                introductory_text = read_data.split("<h2>Please note:</h2>")[0].encode("utf-8")
                copyright_text = "<h2>Please note:</h2>" + read_data.split("<h2>Please note:</h2>")[1]
                
                driver = webdriver.Firefox()

                driver.get("https://deepblue.lib.umich.edu/admin/collection?createNew&communityID=4")
                # driver.get("https://dev.deepblue.lib.umich.edu/admin/collection?createNew&communityID=34")
                
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "loginSubmit")))
                driver.find_element_by_id("login").send_keys("username")
                driver.find_element_by_id("password").send_keys("password")
                driver.find_element_by_id("loginSubmit").click()

                driver.get("https://deepblue.lib.umich.edu/admin/collection?createNew&communityID=4")
                # driver.get("https://dev.deepblue.lib.umich.edu/admin/collection?createNew&communityID=34")

                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "submit_save")))
                capatalized_title = title.replace("papers", "Papers").replace("sound recordings", "Sound Recordings").replace("records", "Records").replace("Papers.", "Papers").replace("collection", "Collection").replace("sound recording", "Sound Recording") # DON'T FORGET TO GET RID OF THE TEST!
                driver.find_element_by_name("name").send_keys(capatalized_title)
                driver.find_element_by_name("copyright_text").send_keys(copyright_text)
                driver.find_element_by_name("license").send_keys("As the designated coordinator for this Deep Blue Collection, I am authorized by the Community members to serve as their representative in all dealings with the Repository. As the designee, I ensure that I have read the Deep Blue policies. Furthermore, I have conveyed to the community the terms and conditions outlined in those policies, including the language of the standard deposit license quoted below and that the community members have granted me the authority to deposit content on their behalf.")
                driver.find_element_by_name("submit_save").click()
                
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "submit_create_admin")))
                driver.find_element_by_name("submit_create_admin").click()
                
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "aspect_administrative_group_EditGroupForm_field_submit_save")))
                driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_query").send_keys("shallcro")
                driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_submit_search_epeople").click()
                # driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_submit_add_eperson_366").click()
                driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_submit_add_eperson_7132").click()
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "aspect_administrative_group_EditGroupForm_field_submit_save")))
                driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_query").clear()
                driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_query").send_keys("eckardm")
                driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_submit_search_epeople").click()
                # driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_submit_add_eperson_4864").click()
                driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_submit_add_eperson_9927").click()
                driver.find_element_by_id("aspect_administrative_group_EditGroupForm_field_submit_save").click()
                
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "submit_return")))
                driver.find_element_by_name("submit_return").click()
                
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, capatalized_title)))
                driver.find_element_by_link_text(capatalized_title).click()
                
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "aspect_discovery_CollectionSearch_div_collection-search")))
                handle = driver.find_element_by_id("aspect_discovery_CollectionSearch_div_collection-search").get_attribute("action").split("/")[5]
                
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Edit Collection")))
                driver.find_element_by_link_text("Edit Collection").click()
                
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "aspect_administrative_collection_EditCollectionMetadataForm_field_submit_save")))
                introductory_text = introductory_text.replace("XXXXXX", handle)
                driver.find_element_by_name("introductory_text").send_keys(introductory_text)
                driver.find_element_by_id("aspect_administrative_collection_EditCollectionMetadataForm_field_submit_save").click()
                
                driver.close()
                
                count += 1

                result = [id, title, ead, "2027.42/" + handle]
                results.append(result)

with open("collections_not_not_in_deepblue_with_handle-2.csv", mode="wb") as collections_not_not_in_deepblue_with_handle:
    writer = csv.writer(collections_not_not_in_deepblue_with_handle)
    writer.writerow(["id", "title", "ead", "handle"])
    writer.writerows(results)
    # writer.writerow(["0080", "National Housewives League of America Records", "nathwive.xml", "2027.42/117671"])
    # writer.writerow(["0601", "Leslie Bassett Papers", "bassettl.xml", "2027.42/117672"])
    # writer.writerow(["2012151", "Tommy Good collection.", "", "2027.42/117673"])
    # writer.writerow(["02115", "Andrew S. Watson", "watsonas.xml", "2027.42/120433"])

