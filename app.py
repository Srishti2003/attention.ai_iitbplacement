import streamlit as st
import requests

# Initialize session states
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "itinerary" not in st.session_state:
    st.session_state["itinerary"] = None
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Sidebar for login
with st.sidebar:
    st.title("TripPlanner Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Simple authentication logic
        if username and password:
            st.session_state["logged_in"] = True
            st.session_state["messages"].append({"sender": "Bot", "text": "Logged in successfully!"})
            st.success("Logged in successfully!")
        else:
            st.error("Please enter a valid username and password.")

# Main chat interface
if st.session_state["logged_in"]:
    st.title("One-Day Trip Planner Chat")
    st.write("Welcome to your personal trip planner! Start by typing your message below.")
    
    # Display previous messages
    for message in st.session_state["messages"]:
        if message['sender'] == 'You':
            st.write(f"You: {message['text']}")
        else:
            st.write(f"Bot: {message['text']}")

    # User input for chat
    user_input = st.text_input("You:", "")
    if st.button("Send"):
        if user_input:
            # Display user message in chat
            st.session_state["messages"].append({"sender": "You", "text": user_input})

            # Debug print statements before sending the request
            print(f"User input: {user_input}")
            print("Sending request to backend...")

            # Send user input to backend chatbot and get response
            try:
                response = requests.post("http://localhost:8000/chat", json={"user_id": username, "message": user_input})

                # Debug print statements after receiving the response
                if response.status_code == 200:
                    bot_response = response.json().get("reply", "No reply received.")
                    print(f"Received bot response: {bot_response}")
                    st.session_state["messages"].append({"sender": "Bot", "text": bot_response})
                    st.write("Bot:", bot_response)
                else:
                    print("Backend service error:", response.status_code)
                    st.error("Error from backend service.")
            except requests.exceptions.RequestException as e:
                print(f"Request exception: {e}")
                st.error(f"Error: {e}")

    # Button to view itinerary
    if st.button("View Itinerary"):
        itinerary_response = requests.get(f"http://localhost:8000/get_itinerary?user_id={username}")
        if itinerary_response.status_code == 200:
            st.session_state["itinerary"] = itinerary_response.json()["itinerary"]
        else:
            st.error("Itinerary not available.")

    # Display itinerary if available
    if st.session_state["itinerary"]:
        st.write("## Your Itinerary")
        for item in st.session_state["itinerary"]:
            st.write(f"- **{item['name']}**: {item['time']} ({item['transport']})")
else:
    st.warning("Please log in to use the chat interface.")
