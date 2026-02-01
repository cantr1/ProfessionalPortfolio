from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import time
import os


def get_task(server: str) -> dict:
    response = requests.post(server + "/task/next")
    response.raise_for_status()
    payload = response.json()

    print(f"Recieved Payload ({payload})")

    if "id" not in payload:
        raise RuntimeError(f"No task returned: {payload}")

    task_id = payload['id']
    url = payload['value']
    return {
        "task_id": task_id,
        "task": url
    }


def scrape_webpage(url: str) -> dict | None:
    print(f"Processing Webpage [{url}]")
    try:
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
    except AttributeError:
        # Handle failure and report the task as failed
        print(f"Attribute error detected from webpage ({url})")
        return {"test_status": "failed"}


def complete_task(server: str, task_id: str, data: dict) -> None:
    payload = {"task_id": task_id,
               "output": data}

    print(f"Submitting processed data: {payload}")

    response = requests.post(server + "/complete_task", json=payload)

    if response.status_code in (200, 201):
        print("Task completed successfully")
    else:
        print(response.status_code)


def main():
    load_dotenv()
    server_ip = os.getenv("API_SERVER")
    api_port = os.getenv("API_PORT")
    server = f"http://{server_ip}:{api_port}"

    for _ in range(10_000_000):  # effectively forever
        task = get_task(server)

        if not task:
            time.sleep(2)  # nothing to do
            continue

        data = scrape_webpage(task["task"])
        complete_task(server, task["task_id"], data)


if __name__ == "__main__":
    main()
