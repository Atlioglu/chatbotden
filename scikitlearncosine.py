import json
from collabrativefiltring import collaborative_filtering_with_sklearn
from aipartbackend import favCategory, getData, writeData 

def generate_recommendations(user):
    collaborative_filtering_with_sklearn('users.json', user)
    writeData(getData(favCategory('usercharacter.json')), favCategory('usercharacter.json'))

    with open('usercharacter.json', 'r') as f:
        usercharacter = json.load(f)

    with open('users.json', 'r') as f:
        users = json.load(f)

    with open('suggestedbooks.json', 'r') as f:
        suggested_books = json.load(f)

    recommendations = []

    user = "User"
    if user in users:
        books = users[user]
        for book, details in books.items():
            rating = details.get("rating")
            category = details.get("category")
            read = details.get("read")

            if rating is not None and rating > 3 and not read:
                category_score = usercharacter.get(category, 0)
                if category_score != "" and int(category_score) > 3:
                    recommendations.append({"title": book, "recommendation": "strongly recommended"})
                else:
                    recommendations.append({"title": book, "recommendation": "recommended"})

    for book in suggested_books:
        recommendations.append({"title": book["title"], "recommendation": "recommended"})

    with open('suggestedbooks.json', 'w') as f:
        json.dump(recommendations, f, indent=4)

    strongly_recommended = [rec["title"] for rec in recommendations if rec["recommendation"] == "strongly recommended"]
    recommended = [rec["title"] for rec in recommendations if rec["recommendation"] == "recommended"]
    return strongly_recommended,recommended

''' 
strongly_recommended_books, recommended_books = generate_recommendations()

print("Strongly Recommended Books:", strongly_recommended_books)
print("Recommended Books:", recommended_books)
'''