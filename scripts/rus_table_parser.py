import pandas as pd
from html.parser import HTMLParser
import datetime
import requests

# Parsing script for https://coronavirus-monitor.ru/coronavirus-v-rossii/
class Parser(HTMLParser):
    def __init__(self, verbose=False):
        super().__init__()
        self.verbose = verbose

        # Parsed data
        self.rus_df = pd.DataFrame()
        self._col_lst = ['Date', 'Region/City', 'Confirmed', 'Deaths', 'Recovered']
        # self.rus_df.columns = self._col_lst

        # Parser parameters
        self._start_str = 'Статистика случаев заражения коронавирусом в Роcсии'
        self._stop_str = 'Итого'
        self._reg_class = 'country'
        self._href_class = 'region-link'
        self._cel_class = 'cell'
        self._last_cel_class = 'cell only-desktop'
        self._col_n = 5
        self._reg_exclude = ['Заражений', 'Смертей', 'Выздоровлений', '% Смертей', '1']

        # Parser state
        self._run = False
        self._col = 2
        self._line = 0
        self._is_reg = False  # Region value
        self._is_val = False  # Data value
        self._is_data = False  # Row handling
        self._cur_reg = ''
        self._date = datetime.datetime.now().strftime("%Y-%m-%d")

    def handle_starttag(self, tag, attrs):
        # print("tag:", tag)

        if not self._run:
            return

        if self.verbose:
            print("start tag:", tag)
            for attr in attrs:
                print('    attr:', attr)

        if tag == 'div' and len(attrs) > 0 and attrs[0][1] == self._reg_class:
            self._is_reg = True
            self._is_data = False
            self._col = 2

        if self._is_data and tag == 'div' and self._col < self._col_n:
            if len(attrs) > 0 and attrs[0][1] == self._cel_class or attrs[0][1] == self._last_cel_class:
                self._is_val = True

    def handle_data(self, data):
        data = data.strip()
        # print("    data:", data)

        if data == self._start_str:
            self._run = True
            if self.verbose:
                print('Start parsing')
            return

        if not self._run or data == '':
            return

        if data == self._stop_str:
            self._run = False
            if self.verbose:
                print('Stop parsing')
            return

        if self.verbose:
            print("    data:", data)

        if self._is_reg and data not in self._reg_exclude:
            self.rus_df = self.rus_df.append({'Date': self._date,
                                              'Region/City': data,
                                              'Confirmed': 0,
                                              'Deaths': 0,
                                              'Recovered': 0}, ignore_index=True)
            self._cur_reg = data
            self._is_reg = False
            self._is_data = True

            if self.verbose:
                print('Add region:', data)
                # print(self.rus_df.head())

        if self._is_val:
            val = int(data.replace('.', ''))
            self.rus_df.loc[self.rus_df['Region/City'] == self._cur_reg, self._col_lst[self._col]] = val
            self._col += 1
            self._is_val = False

            if self.verbose:
                print('    Add val:', int(val))


def run_parsing(file_name='../html_data/16-4/Коронавирус в России. Онлайн карта распространения коронавируса в России..html'):
    page = open(file_name, 'r', encoding='utf-8').read()

    # Fix page data
    page = page.replace(',="" ', '')

    parser = Parser(verbose=False)
    # parser = Parser(verbose=True)
    parser.feed(page)

    # print('parser pos:', parser.getpos())
    # print(parser.rus_df)

    return parser.rus_df


# run_parsing()
