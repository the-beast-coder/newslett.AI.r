import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from newspaper import Article
import openai
import tiktoken
model = "gpt-3.5-turbo"

import smtplib
from email.message import EmailMessage

app_password = "sbwzokfzvppstvub"
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login('newslett.ai.r@gmail.com', app_password)

from firebase_admin import db
import firebase_admin

cred_obj = firebase_admin.credentials.Certificate('/Users/aadij/Downloads/private-key.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':"https://newslaiter-default-rtdb.firebaseio.com/"
	})

ref = db.reference("people/")
people = ref.get()


def send_email (content, address):
    msg = MIMEMultipart()
    msg['Subject'] = "Weekly AI Newsletter"
    msg["From"] = "newslett.ai.r@gmail.com"
    msg["To"] = address.replace(",", ".")
    msg.attach(MIMEText(content, "html"))

    server.send_message(msg)

def get_summary(URL):
    my_article = Article(URL, language="en")
    my_article.download()
    my_article.parse()

    # Load your API key from an environment variable or secret management service
    openai.api_key = "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"

    prompt = "Summarize the following article in under 100 words: \n:" + my_article.text
    
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(prompt)
    if len(tokens) + 250 <= 4095:
        response = openai.ChatCompletion.create(model=model, messages = [{"role":"user", "content":prompt}], temperature=0, max_tokens=150)
        return my_article.title, response["choices"][0]["message"]["content"]
    else:
        return my_article.title, "Unfortunately the article is too long to summarize"

def unique (arr):
    output = []
    for x in arr:
        if x not in output:
            output.append(x)
    return output
category_names = {"business": "/business", "sport":"/sport", "technology":"/business/tech", "entertaimnet":"/entertainment", "world":"/world"}

def get_links (category_names):
    URL = "https://edition.cnn.com"

    categories = {}
    for category in category_names.values():
        page = requests.get(URL + category)

        soup = BeautifulSoup(page.content, "html.parser")

        links = []
        # special attribute to all newspaper links in site
        for link in soup.find_all('a', {"class": "container__link"}):
            links.append(link['href'])

        # take the first link for now
        links = unique([URL + x for x in links])[:1]
        categories[category] = links
    return categories


def get_summaries (categories):
    summaries = {}

    for name,links in categories.items():
        for link in links:
            article_name, summary = get_summary(link)
            summaries[link] = [article_name, summary]
    return summaries

#for address, interests in [("caporik143@kaudat.com", ["sport", "entertainment"])]:
#    msg = '<a href="google.com">Click here for full article</a>'
#    send_email(msg, address)

for address, interests in people.items():
    categories = get_links(category_names)
    summaries = get_summaries(categories)

    msg = ""

    for interest in interests:
        msg += "<h2>" + interest.capitalize() + "</h2>"
        links = categories[category_names[interest]]
        for link in links:
            article_name, summary = summaries[link]
            msg += "<b>" + article_name + ":</b><br>" + summary + "<br>"
            msg += '<a href="' + link + '">Click here for full article</a><br><br>'
        msg += "<br>"
    send_email(msg, address)
server.close()
