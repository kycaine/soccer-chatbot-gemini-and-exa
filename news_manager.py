import streamlit as st
from exa_py import Exa
from typing import List
from models import NewsArticle
from config import EXA_API_KEY

class NewsManager:
    def __init__(self):
        self.exa_client = Exa(api_key=EXA_API_KEY)

    def fetch_football_news(self, query: str, max_results: int = 2) -> List[NewsArticle]:
        try:
            search_response = self.exa_client.search_and_contents(
                query,
                num_results=max_results,
                text=True,
                highlights=False
            )

            with st.expander("Debug Info: Exa Search", expanded=False):
                st.write(f"Found {len(search_response.results)} results from Exa.")
                for i, result in enumerate(search_response.results):
                    st.write(f"Result {i+1} Title: {result.title}")
                    st.write(f"Result {i+1} has content: {bool(result.text and result.text.strip())}")

            articles = []
            for result in search_response.results:
                content = result.text
                if content and content.strip():
                    articles.append(NewsArticle(
                        title=result.title or 'No Title Available',
                        url=result.url or '#',
                        source=result.url.split('/')[2] if result.url else 'Unknown Source',
                        content=content
                    ))
            return articles

        except Exception as e:
            st.warning(f"Error fetching news from Exa: {e}. No articles could be retrieved.")
            return []