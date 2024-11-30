import nltk 
import stanza
import os

#NLTK,Stanzaがそれぞれダウンロードされるか、確認する

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
  print("Downloading NLTK punt")
  nltk.download('punkt')

if not os.path.exists(/home/manager/English-Education-test/venv/lib/python3.10/site-packages/stanza/__init__.py + '/en'):
    print("Downloading Stanza model")
    stanza.download('en')
