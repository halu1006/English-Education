import nltk 
import stanza
import os

#NLTK,Stanzaがそれぞれダウンロードされるか、確認する

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
  print("Downloading NLTK punt")
  nltk.download('punkt')

if not os.path.exists(stanza.download_dir + '/en'):
    print("Downloading Stanza model")
    stanza.download('en')