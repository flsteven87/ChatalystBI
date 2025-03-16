import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API configuration
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
BASE_URL = API_URL.replace("/api/v1", "")

# Configure page settings
st.set_page_config(
    page_title="ChatalystBI",
    page_icon="📊",
    layout="wide"
)

# Page title and description
st.title("ChatalystBI - Intelligent Business Analytics Platform")
st.markdown("Chat with your data using natural language to get insights and visualizations")

def initialize_session_state():
    """Initialize the application session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def display_chat_history():
    """Display the chat history with text and images"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display images if available
            if "images" in message and message["images"]:
                for img in message["images"]:
                    st.image(img["url"])

def handle_user_input(user_input):
    """
    Process user input and get AI response
    
    Args:
        user_input: The user's query text
    """
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Display thinking indicator
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Send request to API
            response = requests.post(
                f"{API_URL}/chat/query",
                json={"query": user_input},
                timeout=60  # Set a reasonable timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Update message and add to history
                message_placeholder.markdown(result["response"])
                
                # Process images
                if "images" in result and result["images"]:
                    for img in result["images"]:
                        st.image(img["url"])
                
                # Add response to history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": result["response"],
                    "images": result.get("images", [])
                })
            else:
                error_msg = f"Error: API returned status code {response.status_code}"
                message_placeholder.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                logger.error(f"API error: {response.status_code}, {response.text}")
                
        except requests.RequestException as e:
            error_msg = f"Error connecting to API: {str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            logger.error(f"Request exception: {str(e)}")
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)

def create_sidebar():
    """Create and populate the sidebar"""
    with st.sidebar:
        st.header("About")
        st.markdown("""
        ChatalystBI is an intelligent business analytics platform that combines large language models with data visualization capabilities.
        
        Users can analyze data, generate insights, and create visualizations through simple conversation, without requiring technical expertise.
        """)
        
        st.header("Usage Guide")
        st.markdown("""
        1. Enter your question in the chat box
        2. The system will analyze your question and generate a response
        3. If applicable, the system will automatically create data visualizations
        4. Continue asking questions to explore your data further
        """)
        
        # Add health check
        try:
            health_response = requests.get(f"{BASE_URL}/health", timeout=5)
            if health_response.status_code == 200:
                st.success("API connection: OK")
            else:
                st.error("API connection: Failed")
        except:
            st.error("Cannot connect to API")

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Display chat history
    display_chat_history()
    
    # Create sidebar
    create_sidebar()
    
    # Chat input
    user_input = st.chat_input("Enter your question...")
    if user_input:
        handle_user_input(user_input)

if __name__ == "__main__":
    main() 