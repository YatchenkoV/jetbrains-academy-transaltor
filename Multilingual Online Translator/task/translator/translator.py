from abc import abstractmethod

import requests
from bs4 import BeautifulSoup

USER_AGENT = 'Mozilla/5.0'


class UnsuccessfulResponseError(Exception):
    pass


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


class BaseOutput:

    @abstractmethod
    def output(self, data):
        pass


class FileStorage(BaseOutput):

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.file = open(file_name, 'a+', encoding="utf-8")

    def output(self, data):
        self.file.write(data)

    def read(self):
        self.file.seek(0)
        return self.file.read()

    def __del__(self):
        self.file.close()


class SimpleLogger(BaseOutput):

    def output(self, data):
        print(data)


class Translator:
    LANGUAGES = ['Arabic', 'German', 'English', 'Spanish', 'French', 'Hebrew', 'Japanese', 'Dutch', 'Polish',
                     'Portuguese', 'Romanian', 'Russian', 'Turkish']
    URL = 'https://context.reverso.net/translation'


    def __init__(self):
        self.session = requests.Session()

    def run(self):

        src_lang, target_lang, word = self.get_task()

        storage = FileStorage(word + '.txt')
        try:
            if target_lang == 'all':

                for lang in self.LANGUAGES:
                    lang = lang.lower()
                    if lang == src_lang:
                        continue
                    parser = self.handle_translation(src_lang, lang, word)
                    self.output_translation(lang, parser, translations_amount=1, output_service=storage,
                                            last_symbol='\n')
                    # self.output_translation(lang, parser, translations_amount=1, output_service=SimpleLogger())
                print(storage.read())

            else:
                parser = self.handle_translation(src_lang, target_lang, word)

                self.output_translation(target_lang, parser, translations_amount=1, output_service=storage,
                                        last_symbol='\n')
                print(storage.read())
                # self.output_translation(target_lang, parser, translations_amount=5, output_service=SimpleLogger())
        except UnsuccessfulResponseError:
            exit()

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

        print("Type the number of a language you want to translate to or '0' to translate to all languages: ")
        target_lang_index = int(input())
        target_lang = cls._get_lang_by_index(target_lang_index - 1) if target_lang_index != 0 else 'all'

        print('Type the word you want to translate:')
        word = input()

        return src_lang, target_lang, word

    def fetch_translation(self, word, translation_direction):
        resp = self.session.get(f'{self.URL}/{translation_direction}/{word}',
                                headers={'User-Agent': USER_AGENT})

        if resp.status_code != 200:
            print('Error during fetching data')
            raise UnsuccessfulResponseError

        return resp

    def handle_translation(self, src_lang, target_lang, word):

        try:
            resp = self.fetch_translation(word, src_lang + '-' + target_lang)
        except UnsuccessfulResponseError:
            exit()

        soup = Parser(resp.content)
        return soup

    @classmethod
    def output_translation(cls, target_lang: str, parser: Parser, translations_amount: int = 5,
                           output_service: BaseOutput = SimpleLogger(), last_symbol=''):

        output_service.output(f'{target_lang.capitalize()} Translations: {last_symbol}')

        for translation in zip(range(translations_amount), parser.get_translations()):
            output_service.output(translation[1] + last_symbol)

        output_service.output('\n')

        output_service.output(f'{target_lang.capitalize()} Examples: {last_symbol}')
        for example in zip(range(translations_amount), parser.get_examples()):
            output_service.output(example[1]['source'] + last_symbol)
            output_service.output(example[1]['target'])
            output_service.output('\n')

        output_service.output('\n')


if __name__ == '__main__':
    Translator().run()
