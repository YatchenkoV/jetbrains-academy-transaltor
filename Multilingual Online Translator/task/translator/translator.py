import requests
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0'
full_lang_names = {'en': 'english', 'fr': 'french'}

print('Type "en" if you want to translate from French into English,'
      ' or "fr" if you want to translate from English into French:')
lang = input()

print('Type the word you want to translate:')
word = input()

print(f'You chose "{lang}" as the language to translate "{word}" to.')

translation_direction = ''
if lang == 'en':
    translation_direction = full_lang_names['en'] + '-' + full_lang_names['fr']
elif lang == 'fr':
    translation_direction = full_lang_names['fr'] + '-' + full_lang_names['en']

resp = requests.get(f'http://context.reverso.net/translation/{translation_direction}/{word}',
                    headers={'User-Agent': user_agent})

print(resp.status_code, 'OK')
soup = BeautifulSoup(resp.content, 'html.parser')
print('Translations')
translations_container = soup.find('div', {'id': 'translations-content'})
print([word.text.strip() for word in translations_container.find_all('a')])

examples_container = soup.find('section', {'id': 'examples-content'})

print([sentence.text.strip() for sentence in examples_container.find_all('span', {'class': 'text'})])

