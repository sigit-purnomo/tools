# Function to scrape Google search results
from seleniumbase import Driver
import time
import pandas as pd
import streamlit as st
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from newspaper import Article


from requests_html import HTMLSession

# Function to get Google search results without Selenium
def get_urls_from_google(query, publisher, num_results):
    session = HTMLSession()
    search_url = f"https://www.google.com/search?q={query}+site:{publisher}"
    response = session.get(search_url)

    urls = []
    for link in response.html.find("a"):
        href = link.attrs.get("href", "")
        if "http" in href and not href.startswith("/"):
            urls.append(href)
        if len(urls) >= num_results:
            break

    return urls

# Function to scrape articles from URLs
def scrape_articles(urls):
    articles = []
    for url in urls:
        try:
            article = Article(url)
            article.download()
            article.parse()
            articles.append({"URL": url, "Title": article.title, "Text": article.text})
        except Exception as e:
            articles.append({"URL": url, "Title": "Failed to fetch", "Text": str(e)})
    
    return pd.DataFrame(articles)

# Streamlit UI
st.title("🔎 Google Search & Article Scraper")

# User inputs
query = st.text_input("Enter Search Query", "selenium python")
publisher = st.text_input("Enter Publisher (e.g., wikipedia.org)", "wikipedia.org")
num_results = st.number_input("Enter Number of Articles", min_value=1, max_value=50, value=10, step=1)

if st.button("Scrape Articles"):
    with st.spinner("Scraping Google... Please wait"):
        urls = get_urls_from_google(query, publisher, num_results)
        if not urls:
            st.error("No URLs found. Try a different query.")
        else:
            st.success(f"Found {len(urls)} articles. Scraping content...")

            with st.spinner("Extracting article contents..."):
                articles_df = scrape_articles(urls)
                st.dataframe(articles_df)

                # Download button for CSV
                csv = articles_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Articles as CSV",
                    data=csv,
                    file_name="scraped_articles.csv",
                    mime="text/csv",
                )
