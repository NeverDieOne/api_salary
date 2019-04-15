import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv
import os

load_dotenv()

LANGUAGES = [
    'JavaScript',
    'Java',
    'Python',
    'Ruby',
    'PHP',
    'C++',
    'C#',
    'C',
    'Go',
    'Scala'
]


def get_predict_salary(salary_from, salary_to):
    if not salary_from and salary_to:
        return salary_to * 0.8
    elif salary_from and not salary_to:
        return salary_from * 1.2
    return (salary_from + salary_to) / 2


def get_predict_rub_salary_hh(vacancy):
    if vacancy['salary']['currency'] != 'RUR':
        return None
    return get_predict_salary(vacancy['salary']['from'], vacancy['salary']['to'])


def get_predict_rub_salary_sj(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    return get_predict_salary(vacancy['payment_from'], vacancy['payment_to'])


result_for_hh = {}
result_for_sj = {}

for language in LANGUAGES:
    api_url_hh = 'https://api.hh.ru/vacancies'

    params_hh = {
        'text': f'Программист {language}',
        'area': 1,
        'only_with_salary': True,
        'period': 30,
        'page': 1
    }
    language_result_hh = requests.get(api_url_hh, params=params_hh).json()
    pages_number = language_result_hh['pages']

    while params_hh['page'] <= pages_number:
        page_data = requests.get(api_url_hh, params=params_hh).json()
        params_hh['page'] += 1
        language_result_hh['items'] += page_data['items']

    result_for_hh[f'{language}'] = {}
    result_for_hh[f'{language}']['vacancies_found'] = language_result_hh['found']
    result_for_hh[f'{language}']['vacancies_processed'] = 0

    total_salary_for_lang_hh = 0
    for job in language_result_hh['items']:
        salary = get_predict_rub_salary_hh(job)
        if salary:
            result_for_hh[f'{language}']['vacancies_processed'] += 1
            total_salary_for_lang_hh += salary
    try:
        result_for_hh[f'{language}']['average_salary'] = int(total_salary_for_lang_hh / result_for_hh[f'{language}']['vacancies_processed'])
    except ZeroDivisionError:
        result_for_hh[f'{language}']['average_salary'] = 0

    api_url_sj = 'https://api.superjob.ru/2.0/vacancies'

    params_sj = {
        'keyword': f'Программист {language}',
        't': 4,
        'catalogues': 48,
        'count': 100
    }
    headers = {
        'X-Api-App-Id': os.getenv('TOKEN')
    }
    language_result_sj = requests.get(api_url_sj, headers=headers, params=params_sj).json()

    result_for_sj[f'{language}'] = {}
    result_for_sj[f'{language}']['vacancies_found'] = language_result_sj['total']
    result_for_sj[f'{language}']['vacancies_processed'] = 0

    total_salary_for_lang_sj = 0
    for job in language_result_sj['objects']:
        salary = get_predict_rub_salary_sj(job)
        if salary:
            result_for_sj[f'{language}']['vacancies_processed'] += 1
            total_salary_for_lang_sj += salary
    try:
        result_for_sj[f'{language}']['average_salary'] = int(
            total_salary_for_lang_sj / result_for_sj[f'{language}']['vacancies_processed'])
    except ZeroDivisionError:
        result_for_sj[f'{language}']['average_salary'] = 0


TABLE_DATA_SJ = (
    ('Язык программирования', 'Найдено вакансий', 'Вакансий обработано', 'Средняя зарплата'),
)
TABLE_DATA_HH = (
    ('Язык программирования', 'Найдено вакансий', 'Вакансий обработано', 'Средняя зарплата'),
)

for lang in result_for_sj:
    TABLE_DATA_SJ += (lang, result_for_sj[lang]['vacancies_found'], result_for_sj[lang]['vacancies_processed'], result_for_sj[lang]['average_salary']),

for lang in result_for_hh:
    TABLE_DATA_HH += (lang, result_for_hh[lang]['vacancies_found'], result_for_hh[lang]['vacancies_processed'], result_for_hh[lang]['average_salary']),


title_sj = 'SuperJob Moscow'
table_instance = AsciiTable(TABLE_DATA_SJ, title_sj)
print(table_instance.table)
print()
title_hh = 'HeadHunter Moscow'
table_instance = AsciiTable(TABLE_DATA_HH, title_hh)
print(table_instance.table)

