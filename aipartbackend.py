import json
import requests


def favCategory(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    max_attribute = max(data, key=data.get)
    return max_attribute

attribute = favCategory('usercharacter.json')


def getData(category):
    baseurl = f"https://openlibrary.org/subjects/{category}.json"
    return baseurl


def writeData(url,category):
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        books = data.get('works', [])
    
        book_entries = [
            {"title": book.get('title'), "category": category}
            for book in books
        ]
    
        with open("suggestedbooks.json", "w") as json_file:
            json.dump(book_entries, json_file, indent=4)
    
    else:
        print("Failed to retrieve data:", response.status_code)


