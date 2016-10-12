import requests
from bs4 import BeautifulSoup
import csv

results = []

headers = {"user-agent": "DSpace collection Handle scraper"}
data = requests.get("https://deepblue.lib.umich.edu/handle/2027.42/65133", headers=headers)

soup = BeautifulSoup(data.text, "lxml")

collections = [a for a in soup("a") if "handle" in a.get("href", "") and a.find("span", class_="Z3988")]

for collection in collections:
    
    if collection.find("span", class_="Z3988").text == "Faculty Archives":
        continue
    
    collection_url = "https://deepblue.lib.umich.edu/" + collection.get("href")
    collection_handle = collection.get("href").replace("/handle/", "")
    collection_name = collection.find("span", class_="Z3988").text
    
    data = requests.get(collection_url, headers=headers)
    soup = BeautifulSoup(data.text, "lxml")
    
    collection_numbers = [a for a in soup("a") if "bhlead" in a.get("href", "")]
    for collection_number in collection_numbers:

        collection_number = collection_number.get("href", "").split("-")[-1]
        results.append([str(collection_number), collection_handle, collection_name])

with open("collno_handle.csv", mode="wb") as f:
    writer = csv.writer(f)
    headers = ["collno", "handle", "title"]
    
    writer.writerow(headers)
    writer.writerows(results)
