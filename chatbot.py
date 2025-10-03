import streamlit as st
import google.generativeai as genai
from models import BotResponse
from news_manager import NewsManager
from config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)

class FootballChatbot:
    def __init__(self):
        self.news_manager = NewsManager()
        self.model = self._initialize_model()
        self.context = """
        You are an expert, direct football analyst. Your tone is confident and factual. Follow these rules absolutely:
        1.  **NEVER apologize.** Do not use phrases like "I'm sorry," "I apologize," "unfortunately," or similar expressions of regret.
        2.  **State the facts directly.** Base your answer ONLY on the provided article content.
        3.  **If the articles do not contain the answer, state that clearly and concisely.** For example, say: "The provided articles do not contain information about [user's topic]." or "The source material does not cover the top scorer for that period."
        4.  **Always cite the time frame.** If an article provides a statistic from a past season, state "According to the article, in the 2023-24 season..."

        Your responses should:
        - Start with the most relevant information you find
        - Clearly indicate time periods for any statistics
        - Be direct and confident about what you know
        - Acknowledge limitations without apologizing
        """

    def _initialize_model(self):
        try:
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
            return genai.GenerativeModel(
                GEMINI_MODEL,
                safety_settings=safety_settings,
                generation_config={
                    "temperature": 1, 
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )
        except Exception as e:
            st.error(f"Error initializing Gemini model: {e}")
            raise

    def generate_response(self, query: str) -> BotResponse:
        articles = self.news_manager.fetch_football_news(query)

        if not articles:
            return BotResponse(
                message="I've searched but couldn't find any articles matching your query. Try rephrasing or asking about a different topic.",
                references=[]
            )

        article_contents = "\n\n".join(
            [f"Article Title: {article.title}\nContent: {article.content}" for article in articles]
        )

        prompt = f"""{self.context}

        Articles to analyze:
        {article_contents}

        User question: {query}

        Based on the ACTUAL CONTENT of these articles, answer the user's question.
        """

        try:
            response = self.model.generate_content(prompt)
            return BotResponse(
                message=response.text,
                references=articles
            )
        except Exception as e:
                print("--- DETAILED GEMINI API ERROR ---")
                print(e)
                print("---------------------------------")
                
                st.error(f"Error generating response. Check the terminal for details.") 
                return BotResponse(
                    message="An error occurred while generating a response. Please check the terminal logs for the specific error.",
                    references=[]
                )