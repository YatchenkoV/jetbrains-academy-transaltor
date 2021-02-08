import requests
from bs4 import BeautifulSoup

USER_AGENT = 'Mozilla/5.0'


class Translator:
    FULL_LANG_NAMES = {'en': 'english', 'fr': 'french'}
    LANGUAGE = {'en': 'french-english', 'fr': 'english-french'}
    URL = 'https://context.reverso.net/translation'

    @classmethod
    def run(cls):

        lang, word = cls.get_task()
        print(f'You chose "{lang}" as the language to translate "{word}" to.')

        translation_direction = cls.get_translation_direction(lang)

        resp = cls.fetch_translation(word, translation_direction)

        if resp.status_code != 200:
            print('Error during fetching data')
            exit()

        print(resp.status_code, 'OK')
        print('\n')

        soup = Parser(resp.content)

        translations = soup.get_translations()
        print('Context examples:')
        print('\n')

        print(f'{cls.FULL_LANG_NAMES[lang].capitalize()} Translations:')
        for translation in zip(range(5), translations):
            print(translation[1])
        print('\n')

        examples = soup.get_examples()
        print(f'{cls.FULL_LANG_NAMES[lang].capitalize()} Examples:')
        for example in zip(range(5), examples):
            print(example[1]['source'])
            print(example[1]['target'])
            print('\n')

    @staticmethod
    def get_task():
        print('Type "en" if you want to translate from French into English,'
              ' or "fr" if you want to translate from English into French:')
        lang = input()

        print('Type the word you want to translate:')
        word = input()
        return lang, word

    @classmethod
    def get_translation_direction(cls, lang) -> str:
        return cls.LANGUAGE[lang]

    @classmethod
    def fetch_translation(cls, word, translation_direction):
        resp = requests.get(f'{cls.URL}/{translation_direction}/{word}',
                            headers={'User-Agent': USER_AGENT})
        return resp


class Parser:

    def __init__(self, content):
        self.soup = BeautifulSoup(content, 'html.parser')

    def get_translations(self):
        translations_container = self.soup.find('div', {'id': 'translations-content'})
        return [word.text.strip() for word in translations_container.find_all('a')]

    def get_examples(self):
        examples_list = []
        examples_container = self.soup.find('section', {'id': 'examples-content'}).find_all('div', {'class': 'example'})

        for single_example in examples_container:
            source = single_example.find('div', {'class': 'src'}).find('span', {'class': 'text'}).text.strip()
            target = single_example.find('div', {'class': 'trg'}).find('span', {'class': 'text'}).text.strip()
            examples_list.append({'target': target, 'source': source})

        return examples_list


if __name__ == '__main__':
    Translator.run()
