import streamlit as st
from exa_py import Exa
from typing import List
from models import NewsArticle
import logger_config # Impor untuk mengaktifkan konfigurasi
import logging

class NewsManager:
    def __init__(self, exa_api_key: str):
        self.logger = logging.getLogger(__name__)
        self.logger.info("NewsManager initialized.")
        self.exa_client = Exa(api_key=exa_api_key)

    def fetch_football_news(self, query: str, max_results: int = 2) -> List[NewsArticle]:
        self.logger.info(f"Fetching football news for query: '{query}'")
        try:
            search_response = self.exa_client.search_and_contents(
                query,
                num_results=max_results,
                text=True,
                highlights=False
            )
            self.logger.info(f"Exa API call successful. Found {len(search_response.results)} potential articles.")

            with st.expander("Analyzing...", expanded=False):
                st.write(f"Found {len(search_response.results)} results from Exa.")
                for i, result in enumerate(search_response.results):
                    st.write(f"Result {i+1} Title: {result.title}")
                    st.write(f"Result {i+1} has content: {bool(result.text and result.text.strip())}")

            articles = []
            for i, result in enumerate(search_response.results):
                self.logger.info(f"Processing article {i+1}/{len(search_response.results)}: '{result.title}'")
                content = result.text
                if content and content.strip():
                    articles.append(NewsArticle(
                        title=result.title or 'No Title Available',
                        url=result.url or '#',
                        source=result.url.split('/')[2] if result.url else 'Unknown Source',
                        content=content
                    ))
                    self.logger.info(f"Article '{result.title}' is valid and has been added.")
                else:
                    self.logger.warning(f"Article '{result.title}' skipped due to empty content.")
            
            self.logger.info(f"Finished processing. Total valid articles: {len(articles)}")
            return articles

        except Exception as e:
            self.logger.error(f"Error fetching news from Exa: {e}", exc_info=True)
            st.warning(f"Error fetching news from Exa: {e}. No articles could be retrieved.")
            return []