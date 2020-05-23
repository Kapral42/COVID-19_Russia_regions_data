import pandas as pd
import datetime
import requests

# Parser of page https://mash.ru/letter/coronavirus-2/
def run_parsing(file_name='html_data/moscow/Откуда в Москве забирали с диагнозом коронавирус — Mash Letter.html'):
    page = open(file_name, 'r', encoding='utf-8').readlines()

    col_list = ['Address', 'Latitude', 'Longitude']
    mos_addr_df = pd.DataFrame(columns=col_list)

    flag = 0
    name = ''
    geo = []
    for line in page:
        if line.find('ymaps.Placemark') != -1:
            geo = line.split('[')[1].split(']')[0].split(',')
            flag += 1
            # print(geo)
        if line.find('hintContent:') != -1:
            name = line.split(': ')[1].strip().strip(',').strip('"').strip()
            flag += 1
            # print(name)
        if flag == 2:
            mos_addr_df = mos_addr_df.append(pd.DataFrame([[name, geo[0], geo[1]]], columns=col_list), ignore_index=True)
            flag = 0

    print(mos_addr_df.head())

    mos_addr_df.to_csv('../release/moscow_addresses.csv', index=False)


run_parsing('../html_data/moscow/Откуда в Москве забирали с диагнозом коронавирус — Mash Letter.html')
