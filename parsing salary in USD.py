import requests
from bs4 import BeautifulSoup
import json

URL = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
url = URL


# Функция для получения списка URL-адресов вакансий
def get_vacancies_urls(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Проверка на ошибки запроса

    soup = BeautifulSoup(response.text, 'lxml')
    links = soup.find_all('a', {'data-qa': 'serp-item__title'})
    urls = [link.get('href') for link in links]
    return urls


# Функция для получения информации о вакансии по URL
def get_vacancy_details(vacancy_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(vacancy_url, headers=headers)
    response.raise_for_status()  # Проверка на ошибки запроса

    soup = BeautifulSoup(response.text, 'lxml')

    # Ищем описание вакансии
    description = soup.find('div', {'data-qa': 'vacancy-description'})
    if description:
        description_text = description.get_text(separator=' ', strip=True)
    else:
        description_text = ""

    # Проверяем наличие ключевых слов
    if 'Django' in description_text and 'Flask' in description_text:
        salary_element = soup.find('span', {'data-qa': 'vacancy-salary-compensation-type-net'}) or \
                         next(
                             (elem for elem in soup.find_all('span', class_='magritte-text___pbpft_3-0-13') if
                              elem.get_text().strip()),
                             None
                         )

        if salary_element:
            # Извлечение текста, удаление HTML-сущностей и пробелов
            salary_text = salary_element.get_text(separator=' ', strip=True)
            # Удаление лишних пробелов и HTML-сущностей (в данном случае, &nbsp;)
            salary_text = ' '.join(salary_text.split())
            salary_text = salary_text.strip()

            # Проверяем, содержит ли текст зарплаты символ $
            if '$' in salary_text:
                company = soup.find('a', {'data-qa': 'vacancy-company-name'})
                company_name = company.get_text(strip=True) if company else 'Не указана'

                city = soup.find('p', {'data-qa': 'vacancy-view-location'})
                city_name = city.get_text(strip=True) if city else 'Не указан'

                # Возвращаем информацию о вакансии
                return {
                    'url': vacancy_url,
                    'salary': salary_text,
                    'company': company_name,
                    'city': city_name
                }
    return None


# Основная функция для сбора информации по всем вакансиям
def collect_vacancies(url):
    # Получаем список ссылок на вакансии
    vacancy_urls = get_vacancies_urls(url)
    vacancies = []
    for vacancy_url in vacancy_urls:
        details = get_vacancy_details(vacancy_url)
        if details:
            vacancies.append(details)

    return vacancies


# Сбор информации о вакансиях
vacancies = collect_vacancies(url)

# Запись информации о вакансиях в файл JSON
with open('vacancies.json', 'w', encoding='utf-8') as f:
    json.dump(vacancies, f, ensure_ascii=False, indent=4)

print("Информация о вакансиях записана в файл vacancies.json")
