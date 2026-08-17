from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import undetected_chromedriver as uc
import pandas as pd
import os
import traceback
import random
import json


def main():
    global products
    products = []
    global driver
    product = ''
    while True:
        product = input("Введите название товара: ")
        if product:
            break

    try:
        options = uc.ChromeOptions()
        # Задаём папку с данными о браузере и профиль, который мы будем использовать (в нём лежат уже выданные нам куки и кэш для ozon)
        profile_path = os.path.abspath('./ozon_user_profile')
        options.add_argument('--profile-directory=Default')
        browser_path = r'C:\Program Files\Google\Chrome Beta\Application\chrome.exe'
        driver_path = os.path.abspath('./chromedriver.exe')

        with uc.Chrome(options=options, enable_cdp_events=True, use_subprocess=True, headless=False, user_data_dir=profile_path, browser_executable_path=browser_path,driver_executable_path=driver_path, suppress_welcome=True) as driver:

            driver.add_cdp_listener('Network.responseReceived', res_processing)
            driver.get('https://www.ozon.ru/')
            sleep(4)
            search_string = driver.find_element(By.NAME, 'text')
            search_string.click()
            for letter in product:
                search_string.send_keys(letter)
                sleep(random.uniform(0.28, 0.52))
            search_string.send_keys(Keys.ENTER)
            sleep(100)
   
    except BaseException:
        traceback.print_exc()

    finally:
        print('Дошло до конца')
        print(products)
        save_to_excel(products=products, filename='TABLE')
        driver.quit()
        sleep(2)
        os._exit(0)


def save_to_excel(products, filename):
    tabl = pd.DataFrame(data=products)
    tabl.to_excel(f"{filename}.xlsx", index=False)

        
def res_processing(event_data):
    try:
        log = event_data
        head_res = log['params']['response']
        if head_res['status'] == 200 and 'json' in head_res['mimeType']:
            res_id = log['params']['requestId']
            res = driver.execute_cdp_cmd('Network.getResponseBody',  {'requestId': res_id})

            # Получаем огромное тело ответа в виде обычной строки, но написанной в формате json
            res_body = res.get('body', '')
            if res_body:
                # Делаем из этой строки обычный Python словарь
                data = json.loads(res_body)
                components = data.get('layout', [])

                # Проверяем, что это нужный нам запрос по его компонентам
                if len(components) == 2 and components[1].get('component', '') == 'tileGridDesktop':
                    widget_states = data['widgetStates']

                    # Забираем значение нужного нам ключа, где хранятся все данные, преобразовываем его в обычный словарь и обращаемся к колючу со всеми товарами
                    for key, value in widget_states.items():
                        if key.startswith('tileGridDesktop'):
                            clean_products_data = json.loads(value)
                            items = clean_products_data['items']
                            print(len(items))

                            # Проходимся по каждому товару и собираем данные
                            for item in items:
                                main_info = item['mainState']

                                price = 0
                                orig_price = 0
                                name = ''
                                rating = ''
                                for info in main_info:
                                    print(info, end='\n\n')

                                    print('Дошли до сбора информации')

                                    if info['type'] == 'priceV2':
                                        price = info['priceV2']['price'][0]['text'].replace('\u2009', '').strip(' ₽')

                                    elif info['type'] == 'textDS' and 'id' in info.keys():
                                        name = info['textDS']['text']

                                    elif info['type'] == 'labelListV2':
                                        label_list = info['labelListV2']['items']
                                        for label in label_list:
                                            if label['type'] == 'text' and len(label['text']['text']) == 3:
                                                rating = label['text']['text']

                                products.append({
                                    'Артикул': item['id'],
                                    'Имя': name,
                                    'Ссылка на товар': 'https://ozon.ru' + item['action']['link'],
                                    'Цена': int(price),
                                    'Рейтинг': float(rating),
                                })
    except BaseException:
        traceback.print_exc()
                                


if __name__ == '__main__':
    main()
