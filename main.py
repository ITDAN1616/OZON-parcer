from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import os
import random
import json
from time import sleep


def main():
    product = ''
    while True:
        product = input("Введите название товара: ")
        if product:
            break

    options = uc.ChromeOptions()
    # Задаём папку с данными о браузере, а также задаём профиль, который мы будем использовать (в нём лежат уже выданные нам куки и кэш для ozon)
    options.add_argument("--user-data-dir=" + os.path.abspath("./ozon_user_profile"))
    options.add_argument("--profile-directory=Default")
    # Это настройка системной функции Chrome
    # goog:loggingPrefs (настройки логирования) в данном случае это инструкция для chromedriver: 
    # Префикс goog говорит что она специфична только для браузера от google, а loggingPrefs - название команды
    # Я передаю ей ключ performance (журнал, отвечающий за логи сети) и его уровень логирования ALL (то есть записывать всё в этот самый журнал)
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})  
    with uc.Chrome(options=options, enable_cdp_events=True, use_subprocess=True, headless=False) as driver:
        sleep(3)
        driver.get('https://www.ozon.ru/')
        sleep(6)
        search_string = driver.find_element(By.NAME, 'text')
        search_string.click()
        for letter in product:
            search_string.send_keys(letter)
            sleep(random.uniform(0.32, 1.02))
        search_string.send_keys(Keys.ENTER)

        sleep(10)

        # Получаем содержимое журнала с логами сети
        logs = driver.get_log('performance')
        print(logs, end='\n\n\n\n')

        for log in logs:
            # Делаем из json-объекта Python словарь и получаем из него нужные данные
            log_data = json.loads(log['message'])['message']
            print(log_data, end='\n\n')
            method = log_data.get('method', '')
            url = log_data.get('url', '')

            # Если это полученный ответ из сети (об этом говрит домен Network, и да, ответ можно получить не только из сети)
            if method == 'Network.responseReceived':
                print(log_data)
                # print(log_data.get('params', {}))
                # id = log_data.get('params', {}).get('requestId')
                # print(id)

        driver.quit()
    os._exit(0)
        

if __name__ == '__main__':
    main()
