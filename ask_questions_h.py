import streamlit as st
import re
import json
from scikitlearncosine import generate_recommendations

import time

with open('questions.json', 'r') as file:
    questions = json.load(file)

with open('users.json', 'r') as file:
    users = json.load(file)

def get_response(user_input):
    split_message = re.split(r'\s+|[,;?!.-]\s*', user_input.lower())
    response = check_all_messages(split_message)
    return response

# Soru listesi
question = [
    {"genre": "horror", "question": "The thrill of creepy and eerie atmospheres excites me."},
    {"genre": "fantasy", "question": "Immersing in worlds with magic and supernatural beings fascinates me."},
    {"genre": "thriller", "question": "I enjoy exploring unsolved mysteries or investigations."},
    {"genre": "sciencefiction", "question": "Future technologies and space travel are intriguing concepts."},
    {"genre": "history", "question": "Past eras and historical events captivate my interest."},
    {"genre": "child", "question": "Simple language and child-friendly themes are enjoyable."},
    {"genre": "young", "question": "Stories focusing on young people's experiences and challenges are exciting."},
    {"genre": "philosophy", "question": "Big questions about life and human existence intrigue me."}
]

# Kullanıcı karakteristiklerini tutmak için dictionary
user_character = {}

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

# JSON dosyasına kullanıcı karakteristiklerini kaydeden fonksiyon
def save_to_json(data, filename='usercharacter.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Streamlit session_state başlatma
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
    st.session_state.user_responses = {}
    st.session_state.is_done = False
    st.session_state.messages = []
    st.session_state.is_asking_questions = False
    st.session_state.current_book = 0
    st.session_state.is_asking_ratings = False

# Mevcut soruyu soran fonksiyon
def ask_question():
    current_index = st.session_state.current_question
    if current_index < len(question):
        current_q = question[current_index]
        st.chat_message("assistant").markdown(current_q["question"])
        st.session_state.messages.append({"role": "assistant", "content": current_q["question"]})
    else:
        st.chat_message("assistant").markdown("Thank you! You've answered all the questions.")
        st.session_state.is_asking_questions = False
        st.session_state.is_asking_ratings = True  # Kitap puanlamasına geç
        ask_for_book_ratings()

# Kitap puanlaması soruları soran fonksiyon
def ask_for_book_ratings():
    user = "User"
    books = users.get(user, {})
    current_book_index = st.session_state.current_book

    if current_book_index < len(books):
        book = list(books.keys())[current_book_index]
        st.chat_message("assistant").markdown(f"Have you read '{book}'? If yes, please rate it (1-5). If not, type 'skip'.")
        st.session_state.messages.append({"role": "assistant", "content": f"Have you read '{book}'? If yes, please rate it (1-5). If not, type 'skip'."})
    else:
        st.session_state.is_asking_ratings = False
        strongly_recommended_books, recommended_books = generate_recommendations(user)
        with st.spinner("Bot is typing..."):
            time.sleep(2)  
        st.chat_message("assistant").markdown(f"Thank you, Here are the book recommendations I have prepared for you! \n **Strongly Recommended Books:**\n {strongly_recommended_books}\n **Recommended Books:**\n {recommended_books}")
        st.session_state.messages.append({"role": "assistant", "content": f"Thank you, Here are the book recommendations I have prepared for you! \n **Strongly Recommended Books:**\n {strongly_recommended_books}\n **Recommended Books:**\n {recommended_books}"})
        st.chat_message("assistant").markdown(f"Would you like more recommendations, or are you looking for a book in a specific genre or topic?")
        st.session_state.messages.append({"role": "assistant", "content": f"Would you like more recommendations, or are you looking for a book in a specific genre or topic?"})

    with open('users.json', 'w') as file:
        json.dump(users, file, indent=4)

# Chatbot loop
def chatbot_loop():
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

        if user_input.lower() == 'quit':
            st.chat_message("assistant").markdown("Good Bye!")
            st.session_state.messages.append({"role": "assistant", "content": "Good Bye!"})
        elif 'suggest' in user_input.lower() or 'book' in user_input.lower():
            st.chat_message("assistant").markdown("I can suggest books for you. Let me ask you some questions first.")
            st.session_state.messages.append({"role": "assistant", "content": "I can suggest books for you. Let me ask you some questions first."})
            st.session_state.is_asking_questions = True
            ask_question()  # İlk soruyu sor
        else:
            # Eğer sorular soruluyorsa cevapları işleyelim
            if st.session_state.is_asking_questions:
                if user_input.isdigit() and 1 <= int(user_input) <= 5:
                    current_q = question[st.session_state.current_question]
                    st.session_state.user_responses[current_q["genre"]] = int(user_input)
                    st.session_state.current_question += 1  # Bir sonraki soruya geç
                    save_to_json(st.session_state.user_responses)  # Her cevap sonrası kaydet
                    ask_question()  # Sonraki soruyu sor
                else:
                    st.chat_message("assistant").markdown("Please enter a valid number between 1 and 5.")
            # Kitap puanlama aşamasına geçtiyse
            elif st.session_state.is_asking_ratings:
                books = users["User"]
                current_book = list(books.keys())[st.session_state.current_book]
                if user_input.lower() == 'skip':
                    users["User"][current_book]["rating"] = None
                    st.session_state.current_book += 1
                    ask_for_book_ratings()  # Sonraki kitabı sor
                else:
                    try:
                        rating = int(user_input)
                        if 1 <= rating <= 5:
                            users["User"][current_book]["rating"] = rating
                            st.session_state.current_book += 1
                            ask_for_book_ratings()  # Sonraki kitabı sor
                        else:
                            st.chat_message("assistant").markdown("Please enter a valid number between 1 and 5.")
                    except ValueError:
                        st.chat_message("assistant").markdown("Please enter a valid number or type 'skip'.")
            else:
                response = get_response(user_input)
                st.chat_message("assistant").markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# Streamlit başlat
st.title("ChatBot")
chatbot_loop()
