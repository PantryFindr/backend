from requests import get
from html import unescape
from json import dumps
from fastapi import FastAPI

pantries = {}

NAME_END = -5

app = FastAPI()

@app.get("/")
def get_locations():
    if pantries != {}:
        return pantries
    response = (get("https://mapping.littlefreepantry.org/").text.splitlines())
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
