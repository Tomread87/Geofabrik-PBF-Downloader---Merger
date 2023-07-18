import requests
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
from tqdm import tqdm
import os
import csv
import shutil
from datetime import datetime

# function to find the neighbouring countries from an input country (key) from a csv file loaded (data)
def find_neighbours(key, data):
    with open('GEODATASOURCE-COUNTRY-BORDERS.CSV', newline='') as csvfile:
        csv_countries = csv.reader(csvfile, delimiter=',')
        links = []
        for row in csv_countries:
            if (key == row[1] and row[3] in data and row[3] not in links):
                links.append(row[3])
        if len(links)  > 0:
            print(f"Found {len(links)} neighbouring countries for {key}\n{', '.join(links)}\n")
        else:
            print("No neighbouring vountries found")
        return links
    
def merge_pbf(key):               
    # Get a list of all files in the newly created directory
    file_list = os.listdir(os.getcwd())
    files_string = ""
    for file in file_list:
        if file.endswith(".pbf"):
            files_string +=  f" {file}"

    command = f'osmium merge {files_string} -o merged.pbf'
    print(command)
    os.system(f"echo {command} > text.txt")
    os.system(f"start /wait cmd /k {command}")
    
    print("Files downloaded successfully. Osmium script called")

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url, output_path):
    print("downloading ")
    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)


# Send a GET request to the website
url = "https://download.geofabrik.de"
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Find the table with id="subregions"
tables = soup.find_all("table")
table = tables[0]

regions = {}
for t in table.find_all("a"):
    if ('.osm' not in t['href'] and '.shp' not in t['href']):
        regions[t.text] = t['href']
        
index = 0
for key in regions:
    print(f"{index}: {key}")
    index += 1
print("\n######################################################")
chosen_reg = input("select a region, type and choose from 0 to " + str(index-1) + "\n")

while not chosen_reg.isnumeric():
    chosen_reg = input("select a region, choose from 0 to " + str(index-1) + "\n")

reg_key = list(regions.keys())[int(chosen_reg)]
        
        
# Send a GET request to the website
url = f"https://download.geofabrik.de/{regions[reg_key]}"
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Create an empty dictionary to store the data
data_dict = {}

# Find the table with id="subregions"
tables = soup.find_all("table")
if len(tables) > 1:
    table = tables[1]
    
    # Extract the data and store it in the dictionary
    for row in table.find_all("tr"):
        tds = row.find_all("td")
        if len(tds) > 1:
            key = tds[0].find("a").text
            link_element = tds[1].find("a")
            if link_element:
                value = 'https://download.geofabrik.de/' + link_element["href"]
                data_dict[key] = value
else:
    # Find all <a> tags with href ending in ".osm.pbf"
    links = soup.find_all("a", href=lambda href: href.endswith("latest.osm.pbf"))
    data_dict[links[0].text] = 'https://download.geofabrik.de/' + links[0]['href']
                
# check if all counties sub regions from geofabrik are present in CSV file

# for key in data_dict:
#     missing = 1
#     with open('GEODATASOURCE-COUNTRY-BORDERS.CSV', newline='') as csvfile:
#         csv_countries = csv.reader(csvfile, delimiter=',')
#         for row in csv_countries:
#             if (key == row[1]):
#                 missing = 0
#                 break
#         if missing:
#             print(key)

# Print choose a country
count = 0
print("\n")
for key in data_dict:
    print(str(count) + ": " + key)
    count = count + 1

print("\n######################################################")
choice = input("select a country, type and choose from 0 to "+str(count-1)+")\n")

while not choice.isnumeric():
    choice = input("select a country, type and choose from 0 to "+str(count-1)+")\n")

# Get neigbouring countries
countries = []
country_choice = ""
if int(choice) >= 0 and int(choice) <= count-1:
    index = 0
    for key in data_dict:
        if index == int(choice):
            country_choice = key
            countries = find_neighbours(key, data_dict)
            countries.append(key)
            break
        index += 1

# Create folder for downloaded files

# Get the current date
current_date = datetime.now().strftime("%y_%m_%d")

# Create a new folder with the current date
new_folder_name = f"{current_date}_{key}"
new_folder_path = os.path.join(os.getcwd(), new_folder_name)
os.makedirs(new_folder_path, exist_ok=True)

#change directory and do command
root_app_folder = os.getcwd()
os.chdir(new_folder_path)

for country in countries:    
    url = data_dict[country]
    if url.find('/'):
        filename = (url.rsplit('/', 1)[1])
        path = ''
        download_url(url, filename)
        
merge_pbf(country_choice);
os.chdir(root_app_folder)