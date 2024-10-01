import streamlit as st
import re
import json
from scikitlearncosine import generate_recommendations
import time

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

    for word in user_message:
        if word in recognised_words:
            message_certainty += 1

    percentage = float(message_certainty) / float(len(recognised_words))

    for word in required_words:
        if word not in user_message:
            has_required_words = False
            break

    if has_required_words or single_response:
        return int(percentage * 100)
    else:
        return 0

# Function to check all messages and determine the best response
def check_all_messages(message):
    highest_prob_list = {}

    def response(bot_response, list_of_words, single_response=False, required_words=[]):
        nonlocal highest_prob_list
        highest_prob_list[bot_response] = message_probability(message, list_of_words, single_response, required_words)

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

    best_match = max(highest_prob_list, key=highest_prob_list.get)
    return "Sorry, I don't understand." if highest_prob_list[best_match] < 1 else best_match

# Ask questions from the survey and get user input
def ask_question():
    st.chat_message("assistant").markdown(question[0])
    st.session_state.messages.append({"role": "assistant", "content": question_text})

    for question in questions:
        genre = question["genre"]
        question_text = question["question"]
        st.chat_message("assistant").markdown(question_text)
        st.session_state.messages.append({"role": "assistant", "content": question_text})

        while True:
            try:
                user_input = st.text_input("You (1-5):")
                if 1 <= int(user_input) <= 5:
                    user_answers[genre] = int(user_input)
                    break
                elif user_input.lower() == 'quit':
                    st.write(f"Bot: Goodbye!")
                    break
                else:
                    st.write(f"Bot: Please enter a valid number between 1 and 5.")
            except ValueError:
                st.write(f"Bot: Please enter a valid number between 1 and 5.")


def save_user_character():
    with open('usercharacter.json', 'w') as file:
        json.dump(user_answers, file, indent=4)

# Ask for book ratings based on the selected user
def ask_for_book_ratings(user):
    books = users.get(user, {})
    for book, details in books.items():
        if details["read"]:
            st.write(f"Bot: Have you read '{book}'? If yes, please rate it (1-5). If not, type 'skip'.")
            user_input = st.text_input(f"Rate '{book}':", key=book)
            if user_input.lower() == 'skip':
                users[user][book]["rating"] = None
            else:
                try:
                    rating = int(user_input)
                    if 1 <= rating <= 5:
                        users[user][book]["rating"] = rating
                except ValueError:
                    st.write("Bot: Please enter a valid number between 1 and 5 or type 'skip'.")

    with open('users.json', 'w') as file:
        json.dump(users, file, indent=4)

# Main chatbot function
def main(user):    
    if user:
        if user in users:
            st.chat_message("assistant").markdown("I can suggest books for you. Let me ask you some questions first.")
            st.session_state.messages.append({"role": "assistant", "content": "I can suggest books for you. Let me ask you some questions first."})
   
            ask_question()
            save_user_character()
            st.write("Bot: Thank you, I got your answers. For helping me more I'm asking you questions about books")
            ask_for_book_ratings(user)
            strongly_recommended_books, recommended_books = generate_recommendations(user)
            st.write("Strongly Recommended Books:", strongly_recommended_books)
            st.write("Recommended Books:", recommended_books)
            st.write("Bot: Do you have any questions?")
        else:
            st.write("Bot: Sorry, I couldn't find your user information.")  


# Used to get the response for general chat
def get_response(user_input):
    split_message = re.split(r'\s+|[,;?!.-]\s*', user_input.lower())
    response = check_all_messages(split_message)
    return response

# Chatbot loop
def chatbot_loop():
    # Initialize chat history and track interaction stage
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "awaiting_username" not in st.session_state:
        st.session_state.awaiting_username = False

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get user input
    user_input = st.chat_input("You:", key="main_input")
    
    # Display user's message
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        time.sleep(0.3)

        # Check for special keywords or if waiting for username
        if st.session_state.awaiting_username:
            # Handle username input
            main(user_input)
            st.session_state.awaiting_username = False  # Reset awaiting flag

        elif user_input.lower() == 'quit':
            st.chat_message("assistant").markdown("Good Bye!")
            st.session_state.messages.append({"role": "assistant", "content": "Good Bye!"})

        elif 'suggest' in user_input.lower() or 'book' in user_input.lower():
            st.chat_message("assistant").markdown("Please enter your username:")
            st.session_state.messages.append({"role": "assistant", "content": "Please enter your username:"})
            st.session_state.awaiting_username = True  # Set awaiting flag to True

        else:
            # Normal conversation flow
            response = get_response(user_input)
            st.chat_message("assistant").markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
# Streamlit UI
st.title("Chatbot")
chatbot_loop()
