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

    def output(self, data):
        with open(self.file_name, 'a+', encoding="utf-8") as f:
            f.write(data)


class SimpleLogger(BaseOutput):

    def output(self, data):
        print(data)


class Translator:
    LANGUAGES = ['Arabic', 'German', 'English', 'Spanish', 'French', 'Hebrew', 'Japanese', 'Dutch', 'Polish',
                 'Portuguese', 'Romanian', 'Russian', 'Turkish']
    URL = 'https://context.reverso.net/translation'

    @classmethod
    def run(cls):

        src_lang, target_lang, word = cls.get_task()

        try:
            if target_lang == 'all':
                storage = FileStorage(word + '.txt')
                for lang in cls.LANGUAGES:
                    lang = lang.lower()
                    if lang == src_lang:
                        continue
                    parser = cls.handle_translation(src_lang, lang, word)
                    cls.output_translation(lang, parser, translations_amount=1, output_service=storage)
                    cls.output_translation(lang, parser, translations_amount=1, output_service=SimpleLogger())

            else:
                parser = cls.handle_translation(src_lang, target_lang, word)
                cls.output_translation(target_lang, parser, translations_amount=5, output_service=SimpleLogger())
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

    @classmethod
    def fetch_translation(cls, word, translation_direction):
        resp = requests.get(f'{cls.URL}/{translation_direction}/{word}',
                            headers={'User-Agent': USER_AGENT})

        if resp.status_code != 200:
            print('Error during fetching data')
            raise UnsuccessfulResponseError

        return resp

    @classmethod
    def handle_translation(cls, src_lang, target_lang, word):

        try:
            resp = cls.fetch_translation(word, src_lang + '-' + target_lang)
        except UnsuccessfulResponseError:
            exit()

        soup = Parser(resp.content)
        return soup

    @classmethod
    def output_translation(cls, target_lang: str, parser: Parser, translations_amount: int = 5,
                           output_service: BaseOutput = SimpleLogger()):
        output_service.output('\n')
        output_service.output(f'{target_lang.capitalize()} Translations: \n')

        for translation in zip(range(translations_amount), parser.get_translations()):
            output_service.output(translation[1] + '\n')

        output_service.output('\n')

        output_service.output(f'{target_lang.capitalize()} Examples: \n')
        for example in zip(range(translations_amount), parser.get_examples()):
            output_service.output(example[1]['source'] + '\n')
            output_service.output(example[1]['target'])
            output_service.output('\n')


if __name__ == '__main__':
    Translator.run()
