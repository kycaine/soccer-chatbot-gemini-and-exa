import streamlit as st
import google.generativeai as genai
from models import BotResponse
from news_manager import NewsManager
from config import GEMINI_MODEL
import re
import logger_config 
import logging

class FootballChatbot:
    def __init__(self, gemini_api_key: str, exa_api_key: str, debug: bool = False):
        self.logger = logging.getLogger(__name__)
        self.debug = debug
        self.logger.info("Initializing FootballChatbot...")
        genai.configure(api_key=gemini_api_key)
        self.news_manager = NewsManager(exa_api_key=exa_api_key)
        self.model = self._initialize_model()
        self.context = self._get_base_context()
        self.logger.info("FootballChatbot initialized successfully.")

    def _initialize_model(self):
        self.logger.info(f"Initializing Gemini Model: {GEMINI_MODEL}")
        try:
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
            model = genai.GenerativeModel(
                GEMINI_MODEL,
                safety_settings=safety_settings,
                generation_config={
                    "temperature": 2,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                },
            )
            self.logger.info("Gemini model initialized successfully.")
            return model
        except Exception as e:
            self.logger.error(f"Error initializing Gemini model: {e}", exc_info=True)
            st.error(f"Error initializing Gemini model: {e}")
            raise

    def _get_base_context(self) -> str:
        return """
        You are an expert, direct football analyst. Your tone is confident and factual. Follow these rules strictly:
        1. NEVER apologize or use words like "I'm sorry" or "unfortunately".
        2. Speak only based on the provided article content.
        3. If articles do not contain the answer, state clearly: 
           "The provided articles do not contain information about [topic]."
        4. Always include a time frame when mentioning statistics or events.
        5. Write in a clear, professional analyst tone — concise, assertive, and accurate.
        """

    def _get_football_keywords(self):
        return [
            # Core football terms
            "football", "soccer", "match", "league", "player", "team", "club",
            "stadium", "goal", "penalty", "referee", "coach", "transfer", "championship",
            "tournament", "fixture", "score", "win", "loss", "draw", "kick", "foul",
            "offside", "corner", "free kick", "yellow card", "red card", "substitution",
            "injury", "training", "lineup", "formation",

            # Competitions
            "premier league", "epl", "la liga", "laliga", "serie a", "bundesliga", "ligue 1",
            "champions league", "europa league", "conference league", "world cup",
            "uefa", "fifa", "afcon", "copa america", "asian cup",

            # Clubs
            "manchester united", "man city", "liverpool", "chelsea", "arsenal",
            "real madrid", "barcelona", "psg", "bayern munich", "juventus", "inter milan",

            # Player roles
            "striker", "forward", "midfielder", "defender", "goalkeeper", "captain",
            "manager", "assistant manager", "scout",

            # Transfers
            "transfer", "loan", "contract", "signing", "deal", "agent", "release clause",

            # Miscellaneous
            "fans", "supporters", "ultras", "crowd", "chant", "kit", "jersey", "VAR",
            "extra time", "penalty shootout", "promotion", "relegation", "news", "today",

            # Common vague football questions
            "who won", "match result", "today’s match", "tonight’s match",
            "yesterday’s match", "live score", "fixture today", "news today", "football news"
        ]

    def _is_football_related(self, query: str, football_keywords: list[str]) -> bool:
        self.logger.info(f"Checking if query is football-related: '{query}'")
        normalized_query = query.lower()
        normalized_query = re.sub(r"[^a-z0-9\s]", " ", normalized_query)
        normalized_query = re.sub(r"\s+", " ", normalized_query).strip()

        merged_query = normalized_query.replace(" ", "")

        for keyword in football_keywords:
            key = keyword.lower().replace(" ", "")
            if key in merged_query:
                self.logger.info(f"Query is football-related. Found keyword: '{keyword}'")
                return True

        vague_patterns = [
            r"who\s+won", r"match\s+(today|tonight|yesterday)",
            r"(live\s+)?score", r"football\s+news", r"news\s+(today|now)"
        ]
        for pattern in vague_patterns:
            if re.search(pattern, normalized_query):
                self.logger.info(f"Query is football-related. Matched vague pattern: '{pattern}'")
                return True
        
        self.logger.info("Query is not football-related.")
        return False


    def generate_response(self, query: str) -> BotResponse:
        self.logger.info(f"--- New Response Generation Started for Query: '{query}' ---")
        
        self.logger.info("Step 1: Filtering context.")
        if not self._is_football_related(query, self._get_football_keywords()):
            self.logger.warning("Query failed football-related check. Returning generic response.")
            return BotResponse(
                message="I can only answer questions about football. Please ask me something related to football.",
                references=[],
            )

        self.logger.info("Step 2: Fetching news articles.")
        articles = self.news_manager.fetch_football_news(query)
        if not articles:
            self.logger.warning("No articles found for the query. Returning empty response.")
            return BotResponse(
                message="I've searched but couldn't find any articles matching your query. Try rephrasing or asking about a different football topic.",
                references=[],
            )
        self.logger.info(f"Found {len(articles)} articles.")

        self.logger.info("Step 3: Constructing prompt for Gemini.")
        article_contents = "\n\n".join(
            f"Article Title: {article.title}\nContent: {article.content}"
            for article in articles
        )
        prompt = f"""
        {self.context}

        Articles to analyze:
        {article_contents}

        User question: {query}

        Based ONLY on the content above, answer confidently and factually.
        """
        self.logger.info("Prompt constructed successfully.")

        self.logger.info("Step 4: Calling Gemini API to generate content.")
        try:
            response = self.model.generate_content(prompt)

            if not response.parts:
                finish_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN"
                self.logger.error(f"Gemini response was empty. Finish Reason: {finish_reason}")
                return BotResponse(
                    message="Gemini has blocked your question.",
                    references=articles
                )
            
            self.logger.info("Gemini API call successful. Response received.")
            return BotResponse(message=response.text, references=articles)

        except Exception as e:
            self.logger.error(f"An unexpected error occurred during Gemini API call: {e}", exc_info=True)
            if self.debug:
                print("\n--- GEMINI API ERROR ---")
                print(e)
                print("-------------------------\n")
            st.error("Error generating response. Check terminal logs for details.")
            return BotResponse(
                message="An error occurred while generating a response. Please check the logs.",
                references=[],
            )
        self.logger.info(f"--- New Response Generation Started for Query: '{query}' ---")
        
        self.logger.info("Step 1: Filtering context.")
        if not self._is_football_related(query, self._get_football_keywords()):
            self.logger.warning("Query failed football-related check. Returning generic response.")
            return BotResponse(
                message="I can only answer questions about football. Please ask me something related to football.",
                references=[],
            )

        self.logger.info("Step 2: Fetching news articles.")
        articles = self.news_manager.fetch_football_news(query)
        if not articles:
            self.logger.warning("No articles found for the query. Returning empty response.")
            return BotResponse(
                message="I've searched but couldn't find any articles matching your query. Try rephrasing or asking about a different football topic.",
                references=[],
            )
        self.logger.info(f"Found {len(articles)} articles.")

        self.logger.info("Step 3: Constructing prompt for Gemini.")
        article_contents = "\n\n".join(
            f"Article Title: {article.title}\nContent: {article.content}"
            for article in articles
        )
        prompt = f"""
        {self.context}

        Articles to analyze:
        {article_contents}

        User question: {query}

        Based ONLY on the content above, answer confidently and factually.
        """
        self.logger.info("Prompt constructed successfully.")

        self.logger.info("Step 4: Calling Gemini API to generate content.")
        try:
            response = self.model.generate_content(prompt)
            self.logger.info("Gemini API call successful. Response received.")
            return BotResponse(message=response.text, references=articles)
        except Exception as e:
            self.logger.error(f"Error during Gemini API call: {e}", exc_info=True)
            if self.debug:
                print("\n--- GEMINI API ERROR ---")
                print(e)
                print("-------------------------\n")
            st.error("Error generating response. Check terminal logs for details.")
            return BotResponse(
                message="An error occurred while generating a response. Please check the logs.",
                references=[],
            )