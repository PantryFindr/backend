from requests import get
from html import unescape
from json import dumps, load, dump
from fastapi import FastAPI
from os import environ, path
from time import sleep

pantries = {}

NAME_END = -5
ENV_PATH = ".env"
DATABASE_PATH = "./app/pantries.json"
SITE_URL = "https://mapping.littlefreepantry.org/"
GEOCODE_KEY = environ.get("GEOCODE_KEY")


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
def get_locations():
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
                print(f"https://geocode.maps.co/reverse?lat={latitude}&lon={longitude}&api_key={GEOCODE_KEY}")
                zipcode = get(f"https://geocode.maps.co/reverse?lat={latitude}&lon={longitude}&api_key={GEOCODE_KEY}").text
                print(zipcode)
                # pantries[id]["zipcode"] = zipcode
                sleep(1)
            # print(f"Name: {name}, ID: {id}, Latitude: {latitude}, Longitude: {longitude}")

    print(dumps(pantries, indent=4))
    save(pantries)
    return pantries

@app.get("/faqs")
def get_faqs():
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
