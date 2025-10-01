import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from openai import OpenAI

# Load local .env if present (for local testing); on GitHub Actions we use Secrets.
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GMAIL_USERNAME = os.getenv("GMAIL_USERNAME")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "farhadmadan@gmail.com")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing. Set it in .env (local) or GitHub Secrets.")

if not (GMAIL_USERNAME and GMAIL_APP_PASSWORD):
    raise RuntimeError("GMAIL_USERNAME or GMAIL_APP_PASSWORD missing. Use a Gmail App Password.")

client = OpenAI(api_key=OPENAI_API_KEY)

prompt = "Please propose a hard, challenging question to assess someone's IQ. Respond only with the question."
messages = [{"role": "user", "content": prompt}]

response = client.chat.completions.create(
    model="gpt-4.1-mini",  # change to a model you have access to if needed (e.g., 'gpt-4o-mini')
    messages=messages,
)

question = response.choices[0].message.content.strip()

subject = "Question for the day"
body_html = f"<h2>Question for Today</h2><p>{question}</p>"

msg = MIMEMultipart()
msg["From"] = GMAIL_USERNAME
msg["To"] = RECEIVER_EMAIL
msg["Subject"] = subject
msg.attach(MIMEText(body_html, "html"))

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
    server.sendmail(GMAIL_USERNAME, RECEIVER_EMAIL, msg.as_string())
    server.quit()
    print("Email sent successfully.")
except Exception as e:
    raise RuntimeError(f"Failed to send email: {e}")
