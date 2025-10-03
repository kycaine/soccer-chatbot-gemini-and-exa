import streamlit as st
from chatbot import FootballChatbot 

INPUT_KEY = "user_input"
FORM_PROMPT_KEY = "form_submitted_prompt" 


CARD_DATA = {
    "Analysis Match": "Provide a detailed **tactical analysis** for the most recent match involving {team_a} and {team_b}. Focus specifically on the **Winning Team's Formation or a Key Player's Role** and the key **Moment or Statistic** that defined the outcome.",
    "Prediction Match": "Give a detailed **match prediction** for the game between **{team_a}** and **{team_b}**. Specify the **Date or Tournament Name** to narrow the search, and include historical results and key player statistics to support the prediction.",

    "Match Schedule": "What is the **full schedule of the next three matchdays** for the **{league}**? Include all competing teams, dates, and times.",
    "News": "Provide me a comprehensive **summary of all recent news** regarding **{name}**'s performance and transfer situation, specifically covering **Competition Name**.",
}


def quick_start_cards():
    """Renders the four centered cards and handles the click actions."""
    st.markdown("## Quick Actions")

    col_spacer_left, col_cards_area, col_spacer_right = st.columns([1, 4, 1])

    with col_cards_area:
        cols = st.columns(4)
        
        # --- CARD 1 ---
        with cols[0]:
            if st.button("Analysis Match", key=f"card_Analysis Match", use_container_width=True):
                st.session_state["active_form"] = "analysis"
                
        # --- CARD 2 ---
        with cols[1]:
            if st.button("Match Schedule", key=f"card_Match Schedule", use_container_width=True):
                st.session_state["active_form"] = "schedule"

        # --- CARD 3 ---
        with cols[2]:
            if st.button("News", key=f"card_News", use_container_width=True):
                st.session_state["active_form"] = "news"

        # --- CARD 4 ---
        with cols[3]:
            if st.button("Prediction Match", key=f"card_Prediction Match", use_container_width=True):
                st.session_state["active_form"] = "prediction"

def clear_active_form():
    st.session_state["active_form"] = None


def render_conditional_form():
    active_form = st.session_state.get("active_form")
    
    if active_form:
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
                input_label = "League Name"
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
                        "Club 1 (e.g., Manchester City)", 
                        key="team_a_input"
                    )
                    st.text_input( 
                        "Club 2 (e.g., Liverpool)", 
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
                base_prompt = CARD_DATA[prompt_key]
                full_prompt = None

                if is_two_inputs:
                    if st.session_state.get("team_a_input") and st.session_state.get("team_b_input"):
                        full_prompt = base_prompt.format(
                            team_a=st.session_state["team_a_input"].strip(), 
                            team_b=st.session_state["team_b_input"].strip()
                        )
                    else:
                        st.error("Please enter both club names to proceed.")
                        return 
                
                else:
                    if st.session_state.get("single_input_name"):
                        single_input_val = st.session_state["single_input_name"].strip()
                        if active_form == "schedule":
                            full_prompt = base_prompt.format(league=single_input_val)
                        else:
                            full_prompt = base_prompt.format(name=single_input_val)
                    else:
                        st.error("Please enter a value to proceed.")
                        return 

                if full_prompt:
                    st.session_state[FORM_PROMPT_KEY] = full_prompt # Store the generated prompt
                    st.session_state["active_form"] = None         # Hide the form
                    st.rerun()                                     # Trigger immediate processing in main()


def main():
    st.set_page_config(
        page_title="SocChat - Football News Chatbot ⚽",
        page_icon="⚽",
        layout="wide"
    )
    
    st.markdown("""
        <style>
        /* ... (General styling for stApp and Quick Action Cards remains the same) ... */
        
        /* 1. Styling for the SUBMIT button (Custom Blue) */
        div.stFormSubmitButton > button {
            background-color: #007bff !important; /* Bright Blue */
            border-color: #007bff !important;
            color: white;
            font-size: 1.1em;
            font-weight: bold;
            height: 50px; 
            border-radius: 10px;
            margin-top: 15px; 
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.4);
            transition: all 0.2s ease-in-out;
        }
        div.stFormSubmitButton > button:hover {
            background-color: #0056b3 !important; /* Darker Blue on hover */
            border-color: #0056b3 !important;
            transform: scale(1.02);
        }

        /* 2. Styling for the TOP-RIGHT "❌" button (Red/Maroon on hover) */
        /* Targets the container holding the '❌' button */
        div[data-testid="stVerticalBlock"] > div:first-child div[data-testid="column"]:nth-child(2) button {
            background-color: transparent !important;
            border: none !important;
            color: #AAAAAA !important; 
            font-size: 20px;
            padding: 0;
            margin: 0;
            line-height: 1;
            height: 30px;
            width: 30px;
            box-shadow: none !important;
            float: right; 
        }
        
        /* Hover effect: Red for the Cancel/X button */
        div[data-testid="stVerticalBlock"] > div:first-child div[data-testid="column"]:nth-child(2) button:hover {
            color: #FF4B4B !important; /* Turn red on hover */
            background-color: transparent !important;
            transform: scale(1.1);
        }

        /* Adjust margin for the title to align with the button */
        div[data-testid="stVerticalBlock"] > div:first-child div[data-testid="column"]:nth-child(1) {
            padding-top: 0px; 
        }
        
        /* Custom styles for references */
        .reference-section {
            margin-top: 10px;
            margin-bottom: 5px;
            font-size: 0.9em;
            color: #6c757d;
        }
        .reference-link {
            display: block;
            font-size: 0.85em;
            color: #007bff;
            text-decoration: none;
            margin-bottom: 3px;
            padding-left: 15px;
        }
        .reference-link:hover {
            text-decoration: underline;
            color: #0056b3;
        }

        </style>
    """, unsafe_allow_html=True)
    
    st.title("SocChat - Football News Chatbot ⚽")
    st.write("This chatbot is powered by Gemini and Exa.")

    if "chatbot" not in st.session_state:
        try:
            st.session_state.chatbot = FootballChatbot()
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {e}")
            return
            
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    if "active_form" not in st.session_state:
        st.session_state["active_form"] = None

    for message in st.session_state.messages:
        avatar = "🧑" if message["role"] == "user" else "⚽"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if "references" in message and message["references"]:
                st.markdown("<div class='reference-section'><b>Sources:</b></div>", unsafe_allow_html=True)
                for ref in message["references"]:
                    if hasattr(ref, 'url') and hasattr(ref, 'title'):
                        st.markdown(f"""<a href='{ref.url}' target='_blank' class='reference-link'>📰 {ref.title}</a>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<a href='{ref['url']}' target='_blank' class='reference-link'>📰 {ref['title']}</a>""", unsafe_allow_html=True)


    quick_start_cards()
    
    render_conditional_form()
        
    st.markdown("---") 

    prompt_to_process = None
    
    if st.session_state.get(FORM_PROMPT_KEY):
        prompt_to_process = st.session_state.pop(FORM_PROMPT_KEY) 

    elif chat_input_value := st.chat_input("Ask me about the latest football news...", key=INPUT_KEY):
        prompt_to_process = chat_input_value

    if prompt_to_process:
        prompt = prompt_to_process 

        st.chat_message("user", avatar="🧑").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="⚽"):
            with st.spinner("Searching news and generating response..."):
                try:
                    response = st.session_state.chatbot.generate_response(prompt)
                    st.write(response.message)
                    
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
                    st.error(f"An error occurred during response generation: {e}")

        st.rerun()

if __name__ == "__main__":
    main()
