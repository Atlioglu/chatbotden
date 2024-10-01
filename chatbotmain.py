import re
import json
import longresponses as long
from scikitlearncosine import generate_recommendations

# Load questions
with open('questions.json', 'r') as file:
    questions = json.load(file)

# Load users data
with open('users.json', 'r') as file:
    users = json.load(file)

# Store user answers
user_answers = {}

# Calculate message probability
def message_probability(user_message, recognised_words, single_response=False, required_words=[]):
    message_certainty = 0
    has_required_words = True

    # Count how many words are present in each predefined message
    for word in user_message:
        if word in recognised_words:
            message_certainty += 1

    # Calculate the percentage of recognised words in a user message
    percentage = float(message_certainty) / float(len(recognised_words))

    # Check that the required words are in the string
    for word in required_words:
        if word not in user_message:
            has_required_words = False
            break

    # Must either have the required words, or be a single response
    if has_required_words or single_response:
        return int(percentage * 100)
    else:
        return 0

# Function to check all messages and determine the best response
def check_all_messages(message):
    highest_prob_list = {}

    # Simplify response creation / add it to the dict
    def response(bot_response, list_of_words, single_response=False, required_words=[]):
        nonlocal highest_prob_list
        highest_prob_list[bot_response] = message_probability(message, list_of_words, single_response, required_words)



    # Responses 
    response('Hello!', ['hello', 'hi', 'hey', 'sup', 'heyo'], single_response=True)
    response('See you!', ['bye', 'goodbye'], single_response=True)
    response('I\'m doing fine, and you?', ['how', 'are', 'you', 'doing'], required_words=['how'])
    response('You\'re welcome!', ['thank', 'thanks'], single_response=True)
    response('What\'s up?', ['what', 'up', 'whats'], required_words=['what'])
    response('I am an AI developed by OpenAI.', ['who', 'are', 'you'], required_words=['who'])
    response('I love helping you out!', ['love', 'you', 'thanks'], required_words=['love', 'you'])
    response('I can help with that!', ['can', 'you', 'help'], required_words=['can', 'help'])
    response('Sorry, I don\'t understand.', ['unknown', 'input'], single_response=True)
    response('That\'s awesome!', ['awesome', 'great', 'cool'], single_response=True)
    response('My name is chaaatboooot.', ['what', 'your', 'name'], required_words=['your', 'name'])
    response('I\'m here to assist you.', ['why', 'you', 'here'], required_words=['why', 'here'])
    response('I like chatting with you!', ['do', 'you', 'like', 'me'], required_words=['like', 'me'])
    response('That\'s interesting!', ['that', 'interesting'], single_response=True)
    response('Yes, I can!', ['can', 'you'], required_words=['can', 'you'])
    response('Sorry, I\'m just a bot.', ['are', 'you', 'real'], required_words=['are', 'real'])

    # Longer responses
    response(long.R_ADVICE, ['give', 'advice'], required_words=['advice'])
    response(long.R_EATING, ['what', 'you', 'eat'], required_words=['you', 'eat'])

    best_match = max(highest_prob_list, key=highest_prob_list.get)
    return long.unknown() if highest_prob_list[best_match] < 1 else best_match

# Ask questions from the survey and get user input
def ask_question():
    for question in questions:
        genre = question["genre"]
        question_text = question["question"]

        # Ask the user the question and get a response
        print(f"Bot: {question_text}")
        while True:
            try:
                user_input = int(input("You (1-5): "))
                if 1 <= user_input <= 5:
                    user_answers[genre] = user_input
                    break
                elif user_input.lower() == 'quit':
                    print("Bot: Goodbye!")
                    break
                else:
                    print("Bot: Please enter a number between 1 and 5.")
            except ValueError:
                print("Bot: Please enter a valid number between 1 and 5.")

def save_user_character():
    with open('usercharacter.json', 'w') as file:
        json.dump(user_answers, file, indent=4)

# Ask for book ratings based on the selected user
def ask_for_book_ratings(user):
    books = users.get(user, {})
    for book, details in books.items():
        if details["read"]:
            print(f"Bot: Have you read '{book}'? If yes, please rate it (1-5). If not, type 'skip'.")
            while True:
                user_input = input("You: ")
                if user_input.lower() == 'skip':
                    users[user][book]["rating"] = None
                    break
                try:
                    rating = int(user_input)
                    if 1 <= rating <= 5:
                        users[user][book]["rating"] = rating
                        break
                    else:
                        print("Bot: Please enter a number between 1 and 5.")
                except ValueError:
                    print("Bot: Please enter a valid number between 1 and 5 or type 'skip'.")

    # Save the updated ratings back to users.json
    with open('users.json', 'w') as file:
        json.dump(users, file, indent=4)

# Main chatbot function
def main():
    # Ask user to username
    user = input("Please enter your username: ")
    if user in users:
        print("Bot: I can suggest books for you. Let me ask you some questions first.")
        ask_question()
        save_user_character()
        print("Bot: Thank you, I got your answers. For helping me more I'm asking you questions about books")
        ask_for_book_ratings(user)
        strongly_recommended_books, recommended_books = generate_recommendations(user)
        print("Strongly Recommended Books:", strongly_recommended_books)
        print("Recommended Books:", recommended_books)
        #generate_recommendations()
        print("Bot: Do you have any questions?")
    else:
        print("Bot: Sorry, I couldn't find your user information.")

# Used to get the response for general chat
def get_response(user_input):
    split_message = re.split(r'\s+|[,;?!.-]\s*', user_input.lower())
    response = check_all_messages(split_message)
    return response

# Chatbot loop
while True:
    user_input = input('You: ')
    if user_input.lower() == 'quit':
        print("Bot: Goodbye!")
        break
    elif 'suggest' in user_input.lower() or 'book' in user_input.lower():
        main()
    else:
        print('Bot: ' + get_response(user_input))

