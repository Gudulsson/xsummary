import requests
import openai
from config import TWITTER_BEARER_TOKEN, OPENAI_API_KEY, RECIPIENT_EMAIL
from mailer import send_email

# Lista på inflytelserika krypto-X-konton
ACCOUNTS = [
    "CryptoCobain", "TheCryptoLark", "cz_binance", "saylor",
    "WhaleChart", "CryptoHayes", "punk6529", "0xfoobar"
]

def fetch_latest_tweets(username, count=5):
    url = f"https://api.twitter.com/2/tweets/search/recent?query=from:{username}&tweet.fields=text&max_results={count}"
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tweets = response.json().get("data", [])
        return [t["text"] for t in tweets]
    else:
        print(f"Fel vid hämtning från {username}: {response.text}")
        return []

def summarize_with_openai(tweets):
    openai.api_key = OPENAI_API_KEY
    joined = "\n\n".join(tweets)
    prompt = f"Summarize the following crypto tweets into a crisp, insightful daily newsletter:\n\n{joined}"
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a crypto newsletter assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def build_html(summary):
    return f"""
    <html>
    <body>
        <h2>📰 Daily Crypto Digest</h2>
        <p>{summary.replace('\n', '<br>')}</p>
    </body>
    </html>
    """

def main():
    all_tweets = []
    for account in ACCOUNTS:
        tweets = fetch_latest_tweets(account)
        all_tweets.extend(tweets)

    if not all_tweets:
        print("Inga tweets hämtade.")
        return

    summary = summarize_with_openai(all_tweets)
    html = build_html(summary)
    send_email(RECIPIENT_EMAIL, "🚀 Dagens Krypto Digest", html)
    print("Nyhetsbrev skickat!")

if __name__ == "__main__":
    main()
