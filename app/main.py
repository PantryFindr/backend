from requests import get
from html import unescape
from json import load, dump
from fastapi import FastAPI
from os import path, getenv
from time import sleep
from dotenv import load_dotenv

pantries = {}

load_dotenv()
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

@app.get("/")
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
            "answer": "PantryFindr is an app created by a high school student to address a need in his community: allowing people to find an anonymous source of food safely."
        },
        {
            "id": 2,
            "question": "What does PantryFindr do?",
            "answer": "PantryFindr allows users to navigate a large, publicly accessible database of Little Free Pantries worldwide. These include pantries listed on the Little Free Pantry website and others that were added manually."
        },
        {
            "id": 3,
            "question": "How do I get started?",
            "answer": 'You can start by clicking the "Continue" button, which will allow you to view a list of pantries sorted by distance. From there, simply click on a location to view it on the map, and click on the pin or the "Open in Maps" text to open it in Apple Maps and start navigation.'
        },
        {
            "id": 4,
            "question": "How do I use the search functionality?",
            "answer": "Simply tap the search bar and type the name of a pantry you'd like to see or enter a zip code."
        }
    ]
