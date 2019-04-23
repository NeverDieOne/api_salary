import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv
import os

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


def print_table(stat_by_language, title):
    table_data = (
        ('Язык программирования', 'Найдено вакансий', 'Вакансий обработано', 'Средняя зарплата'),
    )
    for name, info in stat_by_language.items():
        table_data += (name, info['vacancies_found'], info['vacancies_processed'], info['average_salary']),
    table_instance = AsciiTable(table_data, title)
    print(table_instance.table)


def get_hh_stat(languages, city_code_for_hh=1, vacancy_period=30):
    stat_for_hh = {}
    for language in languages:
        stat_for_hh[language] = {}
        api_url_hh = 'https://api.hh.ru/vacancies'

        language_result_hh = []
        page = 0
        pages_number = 1

        while page < pages_number:
            params_hh = {
                'text': f'Программист {language}',
                'area': city_code_for_hh,
                'only_with_salary': True,
                'period': vacancy_period,
                'page': page
            }
            page_data = requests.get(api_url_hh, params=params_hh).json()
            pages_number = page_data['pages']
            page += 1
            language_result_hh += page_data['items']
            stat_for_hh[language]['vacancies_found'] = page_data['found']

        stat_for_hh[language]['vacancies_processed'] = 0

        total_salary_for_lang_hh = 0
        for vacancy in language_result_hh:
            salary = get_predict_rub_salary_hh(vacancy)
            if salary:
                stat_for_hh[language]['vacancies_processed'] += 1
                total_salary_for_lang_hh += salary
        try:
            number_of_vacancy = stat_for_hh[language]['vacancies_processed']
            stat_for_hh[language]['average_salary'] = int(total_salary_for_lang_hh / number_of_vacancy)
        except ZeroDivisionError:
            stat_for_hh[language]['average_salary'] = 0
    return stat_for_hh


def get_sj_stat(languages, city_code_for_sj=4, vacancy_catalogue_for_sj=48):
    stat_for_sj = {}
    for language in languages:
        stat_for_sj[language] = {}
        api_url_sj = 'https://api.superjob.ru/2.0/vacancies'

        language_result_sj = []
        page = 0
        more_page = True

        while more_page:
            params_sj = {
                'keyword': f'Программист {language}',
                't': city_code_for_sj,
                'catalogues': vacancy_catalogue_for_sj,
                'count': 100,
                'page': page
            }
            headers = {
                'X-Api-App-Id': os.getenv('TOKEN')
            }
            page_data = requests.get(api_url_sj, headers=headers, params=params_sj).json()
            more_page = page_data['more']
            page += 1
            language_result_sj += page_data['objects']
            stat_for_sj[language]['vacancies_found'] = page_data['total']

        stat_for_sj[language]['vacancies_processed'] = 0

        total_salary_for_lang_sj = 0
        for vacancy in language_result_sj:
            salary = get_predict_rub_salary_sj(vacancy)
            if salary:
                stat_for_sj[language]['vacancies_processed'] += 1
                total_salary_for_lang_sj += salary
        try:
            number_of_vacancy = stat_for_sj[language]['vacancies_processed']
            stat_for_sj[language]['average_salary'] = int(total_salary_for_lang_sj / number_of_vacancy)
        except ZeroDivisionError:
            stat_for_sj[language]['average_salary'] = 0
    return stat_for_sj


if __name__ == '__main__':
    load_dotenv()
    print_table(get_sj_stat(LANGUAGES), 'SuperJob Moscow')
    print_table(get_hh_stat(LANGUAGES), 'HeadHunter Moscow')
