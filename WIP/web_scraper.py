import requests
from bs4 import BeautifulSoup


def scrape_webpage(url: str) -> dict:
    response = requests.get(url)
    status_code = response.status_code
    soup = BeautifulSoup(response.text, 'html.parser')
    page_title = soup.title.string
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    description = meta_tag.get('content') if meta_tag else 'null'
    return {
        "status_code": status_code,
        "title": page_title,
        "description": description,
    }


if __name__ == "__main__":
    data = scrape_webpage(
        'https://realpython.github.io'
        '/fake-jobs/jobs/senior-python-developer-0.html')
    print(data)
