import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

def collaborative_filtering_with_sklearn(json_file='users.json', target_user='User'):
    with open(json_file, 'r') as file:
        users = json.load(file)

    all_books = list({book for books in users.values() for book in books})

    user_ratings = []
    user_names = list(users.keys())
    for user in user_names:
        ratings = [users[user].get(book, {}).get('rating', None) for book in all_books]
        user_ratings.append(ratings)

    user_ratings = np.array(user_ratings, dtype=np.float64)

    means = np.nanmean(user_ratings, axis=1)

    adjusted_ratings = user_ratings - means[:, np.newaxis]

    adjusted_ratings = np.nan_to_num(adjusted_ratings)

    similarity_matrix = cosine_similarity(adjusted_ratings)

    target_index = user_names.index(target_user)
    most_similar_user_index = np.argmax(similarity_matrix[target_index, :target_index].tolist() + similarity_matrix[target_index, target_index+1:].tolist())
    
    if most_similar_user_index >= target_index:
        most_similar_user_index += 1

    most_similar_user = user_names[most_similar_user_index]
    highest_similarity = similarity_matrix[target_index, most_similar_user_index]

    for i, book in enumerate(all_books):
        if np.isnan(user_ratings[target_index, i]) and not np.isnan(user_ratings[most_similar_user_index, i]):
            predicted_value = np.ceil(1.2*highest_similarity * user_ratings[most_similar_user_index, i])
            user_ratings[target_index, i] = predicted_value

            if book in users[target_user]:
                users[target_user][book]['rating'] = predicted_value
                users[target_user][book]['read'] = False


    with open(json_file, 'w') as file:
        json.dump(users, file, indent=4)

    '''return {
        "means": means,
        "adjusted_ratings": adjusted_ratings,
        "similarity_matrix": similarity_matrix,
        "most_similar_user": most_similar_user,
        "highest_similarity": highest_similarity,
        "updated_ratings": users[target_user]
    }
    '''

# result = collaborative_filtering_with_sklearn(json_file='users.json', target_user='User')
