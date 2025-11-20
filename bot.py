import os
import time
import requests
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

# Конфигурация
VK_TOKEN = os.getenv("VK_ACCESS_TOKEN")
VK_GROUP_ID = os.getenv("VK_GROUP_ID")
MAX_TOKEN = os.getenv("MAX_BOT_TOKEN")
MAX_CHAT_ID = os.getenv("MAX_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))

# URLs API
VK_API_URL = "https://api.vk.com/method/wall.get"
MAX_API_URL = f"https://api.max.messenger/bot{MAX_TOKEN}/sendMessage"

def get_latest_vk_post():
    """Получает последний пост из ВК"""
    params = {
        "access_token": VK_TOKEN,
        "v": "5.131",
        "owner_id": VK_GROUP_ID,
        "count": 1,
        "filter": "owner"
    }
    try:
        response = requests.get(VK_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if "response" in data and len(data["response"]["items"]) > 0:
            post = data["response"]["items"][0]
            return {
                "id": post["id"],
                "text": post.get("text", ""),
                "url": f"https://vk.com/wall{VK_GROUP_ID}_{post['id']}"
            }
    except Exception as e:
        print(f"Ошибка при получении поста из ВК: {e}")
    return None

def send_to_max(post):
    """Отправляет пост в MAX"""
    message = f"{post['text']}\n\nИсточник: {post['url']}"
    payload = {
        "chat_id": MAX_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(MAX_API_URL, json=payload)
        response.raise_for_status()
        print(f"Пост отправлен в MAX: {post['id']}")
        return True
    except Exception as e:
        print(f"Ошибка при отправке в MAX: {e}")
        return False

def main():
    print("Бот запущен. Ожидание новых постов...")
    last_sent_id = None  # Для предотвращения дублирования

    while True:
        post = get_latest_vk_post()
        if post and post["id"] != last_sent_id:
            if send_to_max(post):
                last_sent_id = post["id"]
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
