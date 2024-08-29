from requests import get
from html import unescape
from json import dumps, load, dump
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
            pantries[id] = pantries.get(id, {})
            if pantries[id] == {}:
                pantries[id]["name"] = name
                pantries[id]["latitude"] = latitude
                pantries[id]["longitude"] = longitude
                address = get(f"https://geocode.maps.co/reverse?lat={latitude}&lon={longitude}&api_key={GEOCODE_KEY}").json()["address"]
                print(address)
                zipcode = address.get("postcode", "")
                pantries[id]["zipcode"] = zipcode
                sleep(1)
            print(f"Name: {name}, ID: {id}, Latitude: {latitude}, Longitude: {longitude}, Zip Code: {zipcode}")

    print(dumps(pantries, indent=4))
    save(pantries)
    return pantries

@app.get("/faqs")
async def get_faqs():
    return [
        {
            "id": 1,
            "question": "What is PantryFindr?",
            "answer": "PantryFindr is an independently developed app that allows a user to navigate a large, publicly accessible database of Little Free Pantries worldwide."
        },
        {
            "id": 2,
            "question": "How do I get started?",
            "answer": 'You can start by clicking the "Start Exploring" button, which will allow you to view a list of pantries sorted by distance.'
        },
        {
            "id": 3,
            "question": "How do I use the search functionality?",
            "answer": "Simply tap the search bar and type the name of a pantry you'd like to see or enter a zip code."
        }
    ]
