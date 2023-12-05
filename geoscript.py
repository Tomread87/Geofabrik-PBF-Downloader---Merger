import sys
import subprocess
from shutil import which

#check if osmium is installed
if which("osmium") is not None:
    print("Osmium is installed correctly, app can merge downloaded files")
else:
    print("Geo app can't find osmium command, Osmium-tool is either not installed or the path is not setup correctly")
    print("\nTo install Osmum-tool you will need anaconda installed and run the following command: \n \n conda install -c conda-forge osmium-tool\n \n")
    print("you may still download all files but the app will not merge the files")
    cont = input("would you like to continue? Y/N: ")
    while cont.lower() != "y" and cont.lower() != "n":
        cont = input("would you like to continue? please type Y or N")
    if cont.lower() == "n":
        print("Exiting app")
        sys.exit()

#check if libraries are installed
try:
    import requests
    print("requests imported")
except:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
    print("installing missing library: requests")
    import requests
    print("requests imported")

try:
    from bs4 import BeautifulSoup
    print("BeautifulSoup imported")
except:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'bs4'])
    print("installing missing library: bs4")
    from bs4 import BeautifulSoup
    print("BeautifulSoup imported")

try:
    from tqdm import tqdm
    print("tqdm imported \n")
except:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'tqdm'])
    print("installing missing library: tqdm")
    from tqdm import tqdm
    print("tqdm imported")

# Import standard python 3 libraries
import urllib.request
import os
import csv
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
            print("No neighbouring countries found")
        return links

# function to check if GEODATASOURCE-COUNTRY-BORDERS.CSV is present in same directory
def check_csv():               
    # Get a list of all files in the newly created directory
    file_list = os.listdir(os.getcwd())
    exists = False
    for file in file_list:
        if file == "GEODATASOURCE-COUNTRY-BORDERS.CSV":
            exists = True
            break
    
    if (not exists):
        print("GEODATASOURCE-COUNTRY-BORDERS.CSV file was not found in the directory. Make sure you have GEODATASOURCE-COUNTRY-BORDERS.CSV file in the same directory from where you are running the script")
    
# script to run the osmium merge command from cmd prompt
def merge_pbf(key):               
    # Get a list of all files in the newly created directory
    file_list = os.listdir(os.getcwd())
    files_string = ""
    for file in file_list:
        if file.endswith(".pbf"):
            files_string +=  f" {file}"

    #command = f'osmium merge {files_string} -o merged.pbf'
    command = f'osmium merge{files_string} -o merged.pbf'
    print(command)
    os.system(f"echo {command} > text.txt")
    subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    #os.system(f"start cmd {command}")
    
    print("\nFiles downloaded successfully. Osmium script called\n")

# shows the preogress bar from dowloading the pbf files of each country
class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

# calls DownloadProgressBar and tells it where to download the files
def download_url(url, output_path):
    print("downloading ")
    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)

# main script to get user input and process it throught the various steps
def geoscript():
    
    print("\n")

    # Send a GET request to the website and collect data
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
    print("\n############### Select Region #####################\n")
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
    choices = []
    print("\n")
    for key in data_dict:
        print(str(count) + ": " + key)
        count = count + 1

    def get_country_choice():
        print("\n############### Select Country #####################\n")
        choice = input("select a country, type and choose from 0 to "+str(count-1)+"\n")

        #check if input is in range
        while (not choice.isnumeric() or not(int(choice) >= 0 and int(choice) <= count-1)):
            choice = input("select a country, type and choose from 0 to "+str(count-1)+")\n")

        choices.append(choice)

        more = ""
        while more.lower() != "y" and more.lower() != "n":
            more = input("Add more countries to selection? please type Y or N\n")
            if more.lower() == "y":
                get_country_choice()

    get_country_choice()

    # Get neigbouring countries
    countries = []
    country_choice = []
    for choice in choices:
        if int(choice) >= 0 and int(choice) <= count-1:
            index = 0
            for key in data_dict:
                if index == int(choice):
                    country_choice.append(key)
                    countries.extend(find_neighbours(key, data_dict))
                    countries.append(key)
                    break
                index += 1

    # Join all relevant chosen countries and their neighbours
    countries = [*set(countries)]
    

    ### Ask user to remove any of the countries ###
    def remove_country():
        print("\n############### Remove Country Choice #####################\n")
        choice = ""
        exitWhile = False


        while choice.lower() != "y" and choice.lower() != "n" or not exitWhile:
            print("Geodata from the following countries will be downloaded and merged:")
            nc = 0
            for c in countries:
                print(str(nc) + " " + c)
                nc += 1
            choice = input("Do you want to remove any countries from? please type Y or N\n")
            if choice.lower() == "y":

                exitChoice = False
                while not exitChoice:
                    number = input("Select the country to remove. Enter a number from 0 to " + str(len(countries) - 1) + " or press c to cancel: ")
                    if number.isdigit():
                        number = int(number)
                        if 0 <= number < len(countries):
                            # Valid number, you can use it to remove the country from the list
                            removed_country = countries.pop(number)
                            print(f"Removed country: {removed_country}")
                            exitChoice = True
                        else:
                            print("Number is out of range.")
                    elif number.lower() == "c":
                        exitChoice = True
                    else:
                        print("Invalid input. Please enter a valid number between 0 and " + str(len(countries) - 1) + " or press c to cancel: ")
            if choice.lower() == "n":
                exitWhile = True

        print("\n############### Starting Downloads #####################\n")

    remove_country()

   

    ### Create folder for downloaded files ###
    country_choice = "_".join([*set(country_choice)])

    # Get the current date
    current_date = datetime.now().strftime("%y_%m_%d")

    # Create a new folder with the current date
    new_folder_name = f"{current_date}_{country_choice}"
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
            
    merge_pbf(country_choice)
    os.chdir(root_app_folder)

    #check if user has finised work
    finished = input("Would you like to merge pbf files from another country? Y/N: ")
    while finished.lower() != "y" and finished.lower() != "n":
        finished = input("please type Y or N")
    if finished.lower() == "y":
        geoscript()
    else:
        return

#check if csv file exists in directory
check_csv()

# run app
geoscript()