from requests import get
from html import unescape
from json import dumps

response = (get("https://mapping.littlefreepantry.org/").text.splitlines())
pantries = {}

NAME_END = -5

for line in response:
    if "push" in line:
        line = line.strip()
        location = line.split()
        name_start = line.find("name")
        
        if name_start == -1:
            continue
        name_start += 7
        
        name = line[name_start:NAME_END]
        name = unescape(name)
        latitude = float(location[2].replace(",", ""))
        longitude = float(location[4].replace(",", ""))
        id = location[6].replace(",", "")
        pantries[id] = {}
        pantries[id]["name"] = name
        pantries[id]["latitude"] = latitude
        pantries[id]["longitude"] = longitude
        print(f"Name: {name}, ID: {id}, Latitude: {latitude}, Longitude: {longitude}")

print(dumps(pantries, indent=4))
