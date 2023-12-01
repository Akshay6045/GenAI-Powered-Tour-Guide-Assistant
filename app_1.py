import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.chat_models import ChatOpenAI

# Page configuration
st.set_page_config(page_title='Team-9 | Capstone🤖', layout='wide', page_icon="🤖")

# Initialize session state variables
for key in ["generated", "past", "input", "stored_session"]:
    if key not in st.session_state:
        st.session_state[key] = []

template = '''

Based on the context provided and to ensure a memorable and insightful experience for travelers, integrate the following features in your interactions:
"Note: You need to provide suggestions only for travel to India and its places and not to any other countries."

Personalized Itinerary Suggestions:

Tailor recommendations based on the traveler's interests, previous travel history, and current location.
Examples:
"I noticed you enjoyed the art museums in Paris. You'll love the National Gallery of Modern Art in Delhi!"
"Since you're in Jaipur, don't miss the sunrise view from Nahargarh Fort. It's breathtaking and less crowded in the morning."
Engaging Historical and Cultural Insights:

Offer intriguing facts and stories about landmarks, festivals, and local customs.
Examples:
"Did you know the Taj Mahal changes color throughout the day? It's a symbol of love and an architectural marvel."
"Tonight's Diwali, the festival of lights! Here's where you can witness the most spectacular celebrations."
Easy-to-Follow Navigation and Tips:

Provide concise, clear directions and travel tips to enhance their exploration.
Use bullet points for simplicity.
Example:
"To reach the Varanasi Ghats: Take a cab to Dashashwamedh Ghat, then explore by foot. Tip: Start early to avoid crowds."
Interactive Learning Opportunities:

Suggest workshops or local experiences where travelers can actively participate.
Example:
"Join a pottery class in Dharavi to experience Mumbai's rich artisan culture firsthand."
Safety and Convenience Advice:

Offer real-time updates on weather, local events, or travel advisories.
Example:
"There's a forecast for rain this afternoon in Kerala. Might want to pack an umbrella for your backwater cruise."
Culinary Journey Guidance:

Recommend dishes and eateries based on their taste preferences and dietary restrictions.
Example:
"As a vegan, you'll love the plant-based thali at this award-winning restaurant in Bangalore."



'''

def get_text():
    """
    Get the user input text.
    """
    input_text = st.text_area("Your Message:", st.session_state["input"], key="input",
                              placeholder="Type your message to the AI tour guide for 'India' here...",
                              height=100)
    return str((input_text) + '***' + template)

def new_chat():
    """
    Clears session state and starts a new chat.
    """
    save = ["User:" + past + "\nBot:" + gen for past, gen in zip(reversed(st.session_state["past"]), reversed(st.session_state["generated"]))]
    st.session_state["stored_session"].append(save)
    st.session_state["generated"].clear()
    st.session_state["past"].clear()
    st.session_state["input"] = ""

# Sidebar for settings and API key input
with st.sidebar:
    st.title("Settings 🛠️")
    MODEL = st.selectbox('Model', ['gpt-3.5-turbo','gpt-4'])
    K = st.number_input('Summary of prompts to consider', min_value=3, max_value=600)
    API_O = st.text_input("Enter Your OPENAI API-KEY:", type="password")

    if st.button("New Chat", key="new_chat"):
        new_chat()

# Main app layout
st.title("GenAI 🤖 powered Tour Guide Assistant to India")
st.subheader(' Capstone Theme Presentation Team-9   ')
st.markdown('''> A Conversational AI Chatbot powered by LangChain, OpenAI GPT Models, and Streamlit    ''')

st.image("logo.png", width=800)

try:
    if API_O:
        llm = ChatOpenAI(temperature=0,
                    openai_api_key=API_O, 
                    model_name=MODEL, 
                    verbose=False)
        
        if 'entity_memory' not in st.session_state:
            st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=K)

        Conversation = ConversationChain(
                llm=llm, 
                prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
                memory=st.session_state.entity_memory
            )

    else:
        st.warning('Please enter your OpenAI API key in the sidebar to start.')
except:
    st.warning('Please enter your OpenAI API key in the sidebar to start.')


# Displaying user input and bot output
user_input = get_text()
if user_input:
    try:
        output = Conversation.run(input=user_input)
        display = str(user_input.split('***')[0])  
        st.session_state.past.append(display)
        st.session_state.generated.append(output)
    except Exception as e:
        st.error("Error in generating response: " + str(e))

# Conversation history
with st.expander("Conversation History"):
    for past, gen in zip(reversed(st.session_state["past"]), reversed(st.session_state["generated"])):
        st.markdown(f"**You:** {past}")
        st.markdown(f"**Bot:** {gen}")

# Download conversation
if st.button('Download Conversation'):
    download_str = "\n".join([f"{past}\n{gen}" for past, gen in zip(st.session_state["past"], st.session_state["generated"])])
    st.download_button('Download', download_str, file_name="conversation.txt")

# Display and clear stored sessions
if st.session_state["stored_session"]:
    with st.sidebar.expander("Stored Conversations"):
        for i, session in enumerate(st.session_state["stored_session"], 1):
            st.write(f"Conversation {i}", session)
        if st.button("Clear Stored Conversations"):
            st.session_state["stored_session"].clear()