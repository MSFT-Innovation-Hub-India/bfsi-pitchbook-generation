"""
News Scraper Function Tool

This module provides a function to scrape news articles from Rediff Money.
Used as a tool for the News Sentiment Agent.
"""

import requests
from bs4 import BeautifulSoup
from typing import Annotated
from pydantic import Field


def scrape_news_articles(
    query: Annotated[str, Field(description="The search keyword or company name to find news articles about.")]
) -> str:
    """
    Scrape news articles from Rediff Money based on a search query.
    Returns a formatted string with article titles, descriptions, and links.
    Fetches up to 15 most recent articles.
    """
    url = f"https://money.rediff.com/news/search?query={query}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Find all headlines (h2 with class 'copycell')
        headlines = soup.find_all('h2', class_='copycell')
        
        if not headlines:
            return f"No news articles found for '{query}'."
        
        # Build result string
        results = []
        results.append(f"Found {len(headlines)} news articles for '{query}':\n")
        
        for idx, headline in enumerate(headlines[:15], 1):  # Limit to 15 articles
            # Get headline text
            title = headline.get_text(strip=True)
            
            # Find the associated link
            link_tag = headline.find('a', href=True)
            link = ''
            if link_tag:
                link = link_tag.get('href', '')
                if link and not link.startswith('http'):
                    link = 'https://money.rediff.com' + link
            
            # Find the associated description
            description_div = headline.find_next_sibling('div', class_='descript')
            description = ''
            if description_div:
                description = description_div.get_text(strip=True)
            
            # Format article
            article = f"\n{idx}. {title}"
            if description:
                article += f"\n   Description: {description}"
            if link:
                article += f"\n   Link: {link}"
            
            results.append(article)
        
        return "\n".join(results)
                
    except requests.exceptions.RequestException as e:
        return f"Error fetching news articles: {e}"
    except Exception as e:
        return f"Error parsing news articles: {e}"

    
