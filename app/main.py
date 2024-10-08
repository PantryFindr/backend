from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from requests import get
from html import unescape
from json import load, dump
from os import path, getenv
from time import sleep

pantries = {}
NAME_END = -5
DATABASE_PATH = "/code/pantries.json"
SITE_URL = "https://mapping.littlefreepantry.org/"
GEOCODE_KEY = getenv("GEOCODE_KEY")

app = FastAPI()

if not path.exists(DATABASE_PATH):
    with open(DATABASE_PATH, "w") as file:
        file.write('{}')
        
with open(DATABASE_PATH) as file:
    pantries = load(file)
file.close()

def save(pantries):
    with open(DATABASE_PATH, "w") as file:
        dump(pantries, file, indent=4)
    file.close()

@app.get("/", response_class=RedirectResponse)
async def redirect():
    return "https://pantryfindr.com"

@app.get("/locations")
async def get_locations():
    response = get(SITE_URL).text.splitlines()
    
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
            
            if pantries.get(id) == None:
                reverse_geocode = get(f"https://geocode.maps.co/reverse?lat={latitude}&lon={longitude}&api_key={GEOCODE_KEY}").json()
                sleep(1)
                zipcode = reverse_geocode["address"].get("postcode", "")
                pantries[id] = {
                    "name": name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "zipcode": zipcode
                }

    save(pantries)
    return pantries

@app.get("/faqs")
async def get_faqs():
    return [
        {
            "id": 1,
            "question": "Why was PantryFindr created?",
            "answer": "PantryFindr is an app created by a high school student to address a need in his community and others: allowing people to find an anonymous source of food safely."
        },
        {
            "id": 2,
            "question": "What does PantryFindr do?",
            "answer": "PantryFindr allows users to navigate a large, publicly accessible database of Little Free Pantries worldwide. These include pantries listed on the Little Free Pantry website and others that were added manually."
        },
        {
            "id": 3,
            "question": "Does PantryFindr collect my data?",
            "answer": "PantryFindr does not collect any data whatsoever. The optional location is stored and processed only on your device and is only used to sort the list of pantries."
        },
        {
            "id": 4,
            "question": "Why does PantryFindr ask for my location?",
            "answer": "PantryFindr asks for your location to sort the list of pantries by proximity. This is always optional and you can change this setting at any time in the Settings app."
        },
        {
            "id": 5,
            "question": "How can I request new pantries?",
            "answer": "You can visit pantryfindr.com/support or email support@pantryfindr.com!"
        }
    ]
