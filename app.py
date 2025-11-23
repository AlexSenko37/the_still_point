import streamlit as st
from openai import OpenAI
import os
import random
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Note: utils/redshift_connection.py was not found in the workspace, 
# so the Redshift integration has been omitted. 
# To add it, create the file and import it here.

def get_poem(day_description):
    # Try to get key from environment variable (e.g. .env file)
    api_key = os.getenv("OPENAI_API_KEY")
    
    # If not found in env, try Streamlit secrets safely
    if not api_key:
        try:
            if "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
        except FileNotFoundError:
            pass
        except Exception:
            pass
            
    if not api_key:
        st.error("OpenAI API Key not found. Please set it in a .env file or Streamlit secrets.")
        return None, None
    
    client = OpenAI(api_key=api_key)
    
    poets = [
        "Emily Dickinson",
        "T.S. Eliot",
        "Langston Hughes",
        "Sylvia Plath",
        "Seamus Heaney",
        "Shel Silverstein",
        "Lewis Carroll",
        "Robert Frost",
        "Ogden Nash",
        "Pablo Neruda",
        "Dr. Seuss"
    ]
    selected_poet = random.choice(poets) if poets else "Unknown Poet"
    
    try:
        # Get system prompt template from env or secrets
        system_prompt_template = os.getenv("POEM_SYSTEM_PROMPT")
        if not system_prompt_template:
            try:
                if "POEM_SYSTEM_PROMPT" in st.secrets:
                    system_prompt_template = st.secrets["POEM_SYSTEM_PROMPT"]
            except:
                pass
        
        # Fallback if secret is missing
        if not system_prompt_template:
            system_prompt_template = "You are {poet}. Write a short poem based on the user's description of their day."

        # Using gpt-5.1 as requested
        response = client.chat.completions.create(
            model="gpt-5.1",  ## please use gpt-5.1 for the best results. it is a real model available now.
            messages=[
                {"role": "system", "content": system_prompt_template.format(poet=selected_poet)},
                {"role": "user", "content": day_description}
            ]
        )
        return response.choices[0].message.content, selected_poet
    except Exception as e:
        st.error(f"Error generating poem: {e}")
        return None, None

def check_password():
    """Returns `True` if the user had the correct password."""
    
    # Get password from env or secrets
    correct_password = os.getenv("APP_PASSWORD")
    # Fallback to secrets if not in env
    if not correct_password:
        try:
            if "APP_PASSWORD" in st.secrets:
                correct_password = st.secrets["APP_PASSWORD"]
        except:
            pass

    # If no password set, default to open (or handle as error)
    # For safety, let's require it if this function is called
    if not correct_password:
        st.warning("App is password protected but APP_PASSWORD is not set.")
        return False

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input
        st.text_input(
            "Enter Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error
        st.text_input(
            "Enter Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct
        return True

def main():
    st.set_page_config(
        page_title="Daily Reflection", 
        page_icon="📜",
        layout="centered"
    )
    
    # Check password before showing the app
    if not check_password():
        st.stop()

    # Kindle/E-ink aesthetic CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&display=swap');

    /* Global App Style */
    .stApp {
        background-color: #121212; /* Dark Slate background */
        background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
        color: #E0E0E0;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6, p, div, span, label, textarea, button {
        font-family: 'Merriweather', serif !important;
    }
    
    h1 {
        font-weight: 300;
        color: #F0F0F0;
        text-align: center;
        margin-bottom: 2.5rem;
        letter-spacing: -0.5px;
    }

    /* Input Text Area */
    .stTextArea textarea {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        color: #E0E0E0;
        border-radius: 2px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
        padding: 1rem;
    }
    
    .stTextArea textarea:focus {
        border-color: #555555;
        box-shadow: none;
    }

    /* Button Styling */
    .stApp [data-testid="stFormSubmitButton"] > button,
    .stApp [data-testid="stButton"] > button {
        background-color: transparent !important;
        color: #E0E0E0 !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 2px !important;
        padding: 0.7rem 2rem;
        width: 100%;
        margin-top: 1.5rem;
        font-weight: 400;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: none !important;
    }
    
    .stApp [data-testid="stFormSubmitButton"] > button:hover,
    .stApp [data-testid="stButton"] > button:hover {
        background-color: #E0E0E0 !important;
        color: #121212 !important;
        border-color: #E0E0E0 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(255,255,255,0.1) !important;
    }
    
    .stApp [data-testid="stFormSubmitButton"] > button:active,
    .stApp [data-testid="stButton"] > button:active {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        transform: translateY(0px);
    }

    /* Poem Display */
    .poem-container {
        background-color: #1E1E1E;
        padding: 0rem 0rem;
        margin-top: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        border: 1px solid #333333;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        position: relative;
    }
    
    .poem-text {
        font-size: 0.8rem;
        line-height: 1.7;
        color: #E0E0E0;
        width: 100%;
        text-align: left;
        letter-spacing: 0.01rem;
    }

    .attribution {
        margin-top: 2.5rem;
        text-align: right;
        font-style: italic;
        font-size: 1rem;
        color: #AAAAAA;
        opacity: 0;
        animation: fadeIn 2s ease forwards;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    st.title("How was your day today?")
    
    with st.form("day_form"):
        day_input = st.text_area(
            "label", 
            height=150, 
            placeholder="Tell me about it...", 
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("Reflect")
        
    if submitted:
        if day_input.strip():
            with st.spinner("Writing..."):
                poem, poet = get_poem(day_input)
                
            if poem and poet:
                poem_placeholder = st.empty()
                
                # Typewriter effect
                full_text = ""
                for char in poem:
                    full_text += char
                    # Update display with current text (converting newlines to breaks)
                    current_html = full_text.replace('\n', '<br>')
                    
                    poem_placeholder.markdown(f"""
                    <div class="poem-container">
                        <div class="poem-text">{current_html}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.03) # Adjust speed here (0.03s per char)
                
                # Final render with attribution
                final_html = poem.replace('\n', '<br>')
                poem_placeholder.markdown(f"""
                <div class="poem-container">
                    <div class="poem-text">{final_html}</div>
                    <div class="attribution">- {poet}</div>
                </div>
                """, unsafe_allow_html=True)
                
        else:
            st.info("Please share a few words first.")

if __name__ == "__main__":
    main()
