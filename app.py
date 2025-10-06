import streamlit as st
import time
from chatbot import FootballChatbot 
import logger_config 
import logging
import os
from rss_manager import fetch_rss_feeds

logger = logging.getLogger(__name__)

INPUT_KEY = "user_input"
FORM_PROMPT_KEY = "form_submitted_prompt" 

CARD_DATA = {
    "Analysis Match": "Provide a detailed **tactical analysis** for the most recent match involving {team_a} as home and {team_b} as away. Focus specifically on the **Winning Team's Formation or a Key Player's Role** and the key **Moment or Statistic** that defined the outcome.",
    "Prediction Match": "Give a detailed **match prediction** for the game between **{team_a}** as home and **{team_b}** as away. Specify the **Date or Tournament Name** to narrow the search, and include historical results and key player statistics to support the prediction.",

    "Match Schedule": "What is the **full schedule of the next three matchdays** for the **{league}**? Include all competing teams, dates, and times.",
    "News": "Provide me a comprehensive **summary of all recent news** regarding **{name}**'s performance and transfer situation, specifically covering **Competition Name**.",
}

RSS_FEEDS = [
    "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.skysports.com/rss/12040",
    "https://www.espn.com/espn/rss/soccer/news"
]


def quick_start_cards():
    st.markdown("### Quick Actions")

    col_spacer_left, col_cards_area, col_spacer_right = st.columns([1, 4, 1])

    with col_cards_area:
        cols = st.columns(4)
        
        # --- CARD 1 ---
        with cols[0]:
            if st.button("Analysis Match", key=f"card_Analysis Match", use_container_width=True):
                logger.info("Quick Action card clicked: Analysis Match")
                st.session_state["active_form"] = "analysis"
                
        # --- CARD 2 ---
        with cols[1]:
            if st.button("Match Schedule", key=f"card_Match Schedule", use_container_width=True):
                logger.info("Quick Action card clicked: Match Schedule")
                st.session_state["active_form"] = "schedule"

        # --- CARD 3 ---
        with cols[2]:
            if st.button("News", key=f"card_News", use_container_width=True):
                logger.info("Quick Action card clicked: News")
                st.session_state["active_form"] = "news"

        # --- CARD 4 ---
        with cols[3]:
            if st.button("Prediction Match", key=f"card_Prediction Match", use_container_width=True):
                logger.info("Quick Action card clicked: Prediction Match")
                st.session_state["active_form"] = "prediction"

def clear_active_form():
    logger.info("Clearing active form.")
    st.session_state["active_form"] = None

def render_conditional_form():
    active_form = st.session_state.get("active_form")
    
    if active_form:
        logger.info(f"Rendering conditional form for: {active_form}")
        if active_form in ["analysis", "prediction"]:
            is_two_inputs = True
            title = "Match Analysis Setup ⚽" if active_form == "analysis" else "Match Prediction Setup 🔮"
            prompt_key = "Analysis Match" if active_form == "analysis" else "Prediction Match"
            submit_button_label = "Analyze Match" if active_form == "analysis" else "Predict Match"
            info_text = "Enter the names of the two competing clubs below."
        elif active_form in ["schedule", "news"]:
            is_two_inputs = False
            if active_form == "schedule":
                title = "Match Schedule Setup 📅"
                prompt_key = "Match Schedule"
                submit_button_label = "Get Schedule"
                info_text = "Enter the name of the league (e.g., 'English Premier League')."
                input_label = "League/Club Name"
                placeholder_text = "e.g., Premier League"
            else: # active_form == "news"
                title = "News Query Setup 🗞️"
                prompt_key = "News"
                submit_button_label = "Get News"
                info_text = "Enter the name of the club or player you are interested in."
                input_label = "Club/Player Name"
                placeholder_text = "e.g., Erling Haaland"
        else:
            return 

        with st.container(border=True): 
            
            col_title, col_cancel_top = st.columns([10, 1])
            
            with col_title:
                st.subheader(title)
                
            with col_cancel_top:
                st.button(
                    "❌", 
                    key="cancel_button_top_right", 
                    on_click=clear_active_form,
                    use_container_width=False
                )
            
            st.info(info_text)
            
            submitted = False 

            with st.form("match_input_form", clear_on_submit=True):
                
                if is_two_inputs:
                    st.text_input( 
                        "Club Home (e.g., Manchester City)", 
                        key="team_a_input"
                    )
                    st.text_input( 
                        "Club Away (e.g., Liverpool)", 
                        key="team_b_input"
                    )
                else: 
                    st.text_input( 
                        input_label, 
                        key="single_input_name", 
                        placeholder=placeholder_text
                    ) 
                
                submitted = st.form_submit_button(
                    submit_button_label, 
                    key="form_submit_button_key", 
                    type="primary" 
                )

            if submitted:
                logger.info(f"Form '{active_form}' submitted.")
                base_prompt = CARD_DATA[prompt_key]
                full_prompt = None

                if is_two_inputs:
                    if st.session_state.get("team_a_input") and st.session_state.get("team_b_input"):
                        full_prompt = base_prompt.format(
                            team_a=st.session_state["team_a_input"].strip(), 
                            team_b=st.session_state["team_b_input"].strip()
                        )
                        logger.info("Generated prompt from two-input form.")
                    else:
                        st.error("Please enter both club names to proceed.")
                        logger.warning("Two-input form submitted with missing values.")
                        return 
                
                else:
                    if st.session_state.get("single_input_name"):
                        single_input_val = st.session_state["single_input_name"].strip()
                        if active_form == "schedule":
                            full_prompt = base_prompt.format(league=single_input_val)
                        else:
                            full_prompt = base_prompt.format(name=single_input_val)
                        logger.info("Generated prompt from single-input form.")
                    else:
                        st.error("Please enter a value to proceed.")
                        logger.warning("Single-input form submitted with missing value.")
                        return 

                if full_prompt:
                    logger.info(f"Storing generated prompt to session state and re-running.")
                    st.session_state[FORM_PROMPT_KEY] = full_prompt # Store the generated prompt
                    st.session_state["active_form"] = None         # Hide the form
                    st.rerun()                                     # Trigger immediate processing in main()

def load_css():
    css = """
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 1.2rem !important;
        left: 320px !important;
        width: calc(100% - 360px) !important;
        z-index: 9999 !important;
        background-color: rgba(18, 18, 18, 0.9) !important;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.1);
    }

    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    logger.info("Custom CSS for fixed input loaded successfully.")

def main():
    st.set_page_config(
        page_title="SocChat - No.1 Soccer Information by Blumberk ⚽",
        page_icon="⚽",
        layout="wide"
    )
    
    load_css()
        
    st.title("SocChat - No.1 Soccer Information by Blumberk ⚽")
    st.write("Chatbot ini didukung oleh Gemini dan Exa, dirancang khusus untuk informasi sepak bola.")
    logger.info("Main page rendered.")

    with st.sidebar:
        st.title("SocChat \n No.1 Soccer Information by Blumberk")

        st.header("Setup API Keys")
        api_keys_submitted = st.session_state.get("api_keys_submitted", False)

        gemini_api_key = st.text_input("Gemini API Key", type="password", key="gemini_api_key_input", disabled=api_keys_submitted)
        exa_api_key = st.text_input("Exa API Key", type="password", key="exa_api_key_input", disabled=api_keys_submitted)

        if not api_keys_submitted:
            if st.button("Submit"):
                logger.info("API Key submit button clicked.")
                if gemini_api_key and exa_api_key:
                    with st.spinner("Checking API..."):
                        time.sleep(2)
                        try:
                            logger.info("Attempting to initialize chatbot with provided API keys.")
                            st.session_state.chatbot = FootballChatbot(gemini_api_key=gemini_api_key, exa_api_key=exa_api_key, debug=True)
                            st.session_state.api_keys_submitted = True
                            logger.info("Chatbot initialized successfully. Re-running app.")
                            st.rerun()
                        except Exception as e:
                            logger.error(f"Failed to initialize chatbot: {e}", exc_info=True)
                            st.error(f"Failed to initialize chatbot: {e}")
                else:
                    st.warning("Please enter both API keys.")
                    logger.warning("API Key submission failed: Keys were missing.")

    if "api_keys_submitted" not in st.session_state or not st.session_state.api_keys_submitted:
        st.warning("Please enter your API keys in the sidebar and click 'Submit' to start the chatbot.")
        return
    
    tab1, tab2 = st.tabs(["News", "Chatbot"])

    with tab1:
        st.header("Latest Football News")
        articles = fetch_rss_feeds(RSS_FEEDS, limit=10)
        if articles:
            for article in articles:
                with st.container(border=True):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if article.get("image"):
                            st.image(article["image"], use_container_width=True)
                        else:
                            st.image("https://upload.wikimedia.org/wikipedia/commons/7/75/No_image_available.png", use_container_width=True)
                    with col2:
                        st.subheader(article["title"])
                        st.write(f"🕒 {article['published']}")
                        st.markdown(f"[Read more ▶️]({article['link']})")
                st.markdown("---")

        else:
            st.warning("No news articles found.")
            
    with tab2:
        if "messages" not in st.session_state:
            st.session_state.messages = []
            logger.info("Initialized 'messages' in session state.")
            
        if "active_form" not in st.session_state:
            st.session_state["active_form"] = None
            logger.info("Initialized 'active_form' in session state.")

        for message in st.session_state.messages:
            avatar = "https://upload.wikimedia.org/wikipedia/commons/a/aa/Message-icon-white-background.png?20210611024859" if message["role"] == "user" else "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Google-gemini-icon.svg/640px-Google-gemini-icon.svg.png"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
                if "references" in message and message["references"]:
                    st.markdown("<div class='reference-section'><b>Sources:</b></div>", unsafe_allow_html=True)
                    for ref in message["references"]:
                        if hasattr(ref, 'url') and hasattr(ref, 'title'):
                            st.markdown(f"""<a href='{ref.url}' target='_blank' class='reference-link'>📰 {ref.title}</a>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""<a href='{ref.get('url', '#')}' target='_blank' class='reference-link'>📰 {ref.get('title', 'Link')}</a>""", unsafe_allow_html=True)

        quick_start_cards()
        
        render_conditional_form()
                    
        st.markdown("---") 

        prompt_to_process = None
        
        if st.session_state.get(FORM_PROMPT_KEY):
            prompt_to_process = st.session_state.pop(FORM_PROMPT_KEY)
            logger.info(f"Processing prompt from form submission.")
        elif chat_input_value := st.chat_input("Ask me about the latest football news...", key=INPUT_KEY):
            prompt_to_process = chat_input_value
            logger.info(f"Processing prompt from chat input.")

        if prompt_to_process:
            logger.info(f"User prompt: '{prompt_to_process}'")
            st.chat_message("user", avatar="https://upload.wikimedia.org/wikipedia/commons/a/aa/Message-icon-white-background.png?20210611024859").write(prompt_to_process)
            st.session_state.messages.append({"role": "user", "content": prompt_to_process})

            with st.chat_message("assistant", avatar="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Google_Gemini_icon_2025.svg/640px-Google_Gemini_icon_2025.svg.png"):
                with st.spinner("Searching news and generating response..."):
                    try:
                        logger.info("Generating chatbot response...")
                        response = st.session_state.chatbot.generate_response(prompt_to_process)
                        st.write(response.message)
                        logger.info("Response generated and displayed successfully.")
                        
                        if response.references:
                            st.markdown("<div class='reference-section'>Sources:</div>", unsafe_allow_html=True)
                            reference_list = []
                            for ref in response.references:
                                if hasattr(ref, 'url') and hasattr(ref, 'title'):
                                    st.markdown(f"""<a href='{ref.url}' target='_blank' class='reference-link'>📰 {ref.title}</a>""", unsafe_allow_html=True)
                                    reference_list.append({"url": ref.url, "title": ref.title})
                                else:
                                    st.markdown(f"""<a href='{ref.get('url', '#')}' target='_blank' class='reference-link'>📰 {ref.get('title', 'Link')}</a>""", unsafe_allow_html=True)
                                    reference_list.append(ref)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response.message,
                            "references": reference_list if response.references else []
                        })
                    except Exception as e:
                        logger.error(f"An error occurred during response generation: {e}", exc_info=True)
                        st.error(f"An error occurred during response generation: {e}")

            st.rerun()

if __name__ == "__main__":
    logger.info("--- SocChat Application Starting ---")
    main()