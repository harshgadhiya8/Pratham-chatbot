import requests
from bs4 import BeautifulSoup
import json
import spacy
import time

def get_page_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  

        if 'text/html' in response.headers.get('Content-Type', ''):
            soup = BeautifulSoup(response.text, 'html.parser')
            page_content = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'content': ' '.join([p.get_text() for p in soup.find_all('p')])
            }
            if 'author' in page_content['content'].lower() or 'donate' in url.lower():
                page_content['content'] = ''  

            return page_content
        else:
            print(f"Skipping non-HTML content at {url}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None

def scrape_website(base_url):
    visited_urls = set()
    to_visit = [base_url]
    scraped_data = []
    total_requests = 0

    while to_visit:
        current_url = to_visit.pop(0)
        if current_url not in visited_urls:
            print(f'Scraping {current_url} (Total Requests: {total_requests})')
            page_content = get_page_content(current_url)
            if page_content:
                scraped_data.append(page_content)
                visited_urls.add(current_url)
                time.sleep(1)
                total_requests += 1

                try:
                    response = requests.get(current_url)
                    response.raise_for_status()
                    if 'text/html' in response.headers.get('Content-Type', ''):
                        soup = BeautifulSoup(response.text, 'html.parser')
                        for a in soup.find_all('a', href=True):
                            link = a['href']
                            if link.startswith('/'):
                                link = base_url + link
                            if base_url in link and link not in visited_urls and 'donate' not in link.lower():
                                to_visit.append(link)
                except requests.exceptions.RequestException as e:
                    print(f"Failed to fetch links from {current_url}: {e}")

    return scraped_data

def clean_data(data):
    nlp = spacy.load('en_core_web_sm')
    cleaned_data = []

    for item in data:
        if item['content']:
            doc = nlp(item['content'])
            summary = ' '.join([sent.text for sent in doc.sents][:2])
            keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]
            cleaned_data.append({'url': item['url'], 'title': item['title'], 'summary': summary, 'keywords': keywords})

    return cleaned_data

if __name__ == "__main__":
    base_url = 'https://www.pratham.org'
    scraped_data = scrape_website(base_url)

    with open('scraped_data.json', 'w') as f:
        json.dump(scraped_data, f)

    cleaned_data = clean_data(scraped_data)

    with open('cleaned_pratham_data.json', 'w') as f:
        json.dump(cleaned_data, f)
