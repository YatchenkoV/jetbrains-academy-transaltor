import requests
from bs4 import BeautifulSoup

USER_AGENT = 'Mozilla/5.0'


class Translator:
    FULL_LANG_NAMES = {'en': 'english', 'fr': 'french'}
    LANGUAGE = {'en': 'french-english', 'fr': 'english-french'}
    LANGUAGES = ['Arabic', 'German', 'English', 'Spanish', 'French', 'Hebrew', 'Japanese', 'Dutch', 'Polish',
                 'Portuguese', 'Romanian', 'Russian', 'Turkish']
    URL = 'https://context.reverso.net/translation'

    @classmethod
    def run(cls):

        src_lang, target_lang, word = cls.get_task()

        translation_direction = src_lang + '-' + target_lang

        resp = cls.fetch_translation(word, translation_direction)

        if resp.status_code != 200:
            print('Error during fetching data')
            exit()

        soup = Parser(resp.content)

        translations = soup.get_translations()
        print('\n')

        print(f'{target_lang.capitalize()} Translations:')
        for translation in zip(range(5), translations):
            print(translation[1])
        print('\n')

        examples = soup.get_examples()
        print(f'{target_lang.capitalize()} Examples:')
        for example in zip(range(5), examples):
            print(example[1]['source'])
            print(example[1]['target'])
            print('\n')

    @classmethod
    def _get_lang_by_index(cls, index) -> str:
        return cls.LANGUAGES[index].lower()

    @classmethod
    def get_task(cls):
        print("Hello, you're welcome to the translator. Translator supports: ")
        for index, language in enumerate(cls.LANGUAGES):
            print(f"{index + 1}. {language.capitalize()}")

        print('Type the number of your language:')

        src_lang = cls._get_lang_by_index(int(input()) - 1)

        print('Type the number of language you want to translate to: ')
        target_lang = cls._get_lang_by_index(int(input()) - 1)

        print('Type the word you want to translate:')
        word = input()

        return src_lang, target_lang, word

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
