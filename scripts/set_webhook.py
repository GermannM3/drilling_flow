import requests

TOKEN = "7554540052:AAEvde_xL9d85kbJBdxPu8B6Mo4UEMF-qBs"
WEBHOOK_URL = "https://drilling-flow.vercel.app/webhook"

def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    response = requests.get(url, params={"url": WEBHOOK_URL})
    print(response.json())

if __name__ == "__main__":
    set_webhook() 