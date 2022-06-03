import bs4
import spacy
import requests
import streamlit as st
from bs4 import BeautifulSoup

# Load English model
# python -m spacy download en_core_web_trf
trf_nlp = spacy.load("en_core_web_trf") # Transformer based model
# or...
# python -m spacy download en_core_web_lg
# nlp_lg = spacy.load("en_core_web_lg")

# options for displaying parts of speach
options = {"compact": True, "color": "black", "font": "Source Sans Pro"}

'''
# Speed **Read** With POS **Highlighting**

Using the [Spacy](https://github.com/connorguy/nlp-with-spaCY/blob/main/guide-to-nlp-with-spacy.ipynb) library, this app will highlight nouns, verbs, and adjectives (different parts of speech) in a text to increase focus durring reading. 
Parsing is setup for NPR articles using beautiful soup.

---
'''

# Get user npr article using streamlit
url = st.text_input('NPR URL:', placeholder='https://www.npr.org/article/...')
url = 'https://www.npr.org/2022/05/30/1102057733/meteor-shower-possible-monday-night' if len(url) == 0 else url
if 'npr' not in url:
    st.error('Please enter a valid npr url')
    exit()
st.markdown('---')

page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

title = soup.find(class_='storytitle')
st.subheader(title.text)

text = soup.find(class_='storytext storylocation linkLocation')

story_text = ''
for i in text:
    if type(i) == bs4.element.Tag and i.name == 'p':
        story_text += " " + i.text

story_doc = trf_nlp(story_text)

# Wrap in markdown/html formatting
def pos_html(text, color='black', size=17) -> str:
    return f'<span style="color:{color};font-weight:bold;font-size:{size}px"> {text}</span>'

mark_down = ''
for token in story_doc:
    t = token.text.strip()
    if token.pos_ == "PROPN":
        mark_down += pos_html(t, 'green', 20)
    elif token.pos_ == "NOUN":
        mark_down += pos_html(t, size=18)
    elif token.pos_ == "VERB":
        mark_down += pos_html(t, color='#283747')
    elif token.pos_ == "NUM":
        mark_down += pos_html(t)
    elif token.pos_ == "ADJ":
        mark_down += pos_html(t, color='purple')
    elif token.pos_ == "PUNCT":
        mark_down += f'{t}'
    else:
        mark_down += f' {t}'

st.markdown(mark_down, unsafe_allow_html=True)


'''
---

#### Tags
Auto generated tags based on named entity recognition.
'''

# Get all unique named entities
net = set([n.text for n in story_doc.ents if n.label_ in ['PERSON', 'ORG', 'GPE', 'LOC']])
tags = ''
for n in net:
    search_term = n.replace(' ', '+').lower()
    tags += f'<a href="https://www.google.com/search?btnI=1&q={search_term}">#{n}</a> '

st.markdown(tags, unsafe_allow_html=True)
