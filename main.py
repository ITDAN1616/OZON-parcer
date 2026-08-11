from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import os
import random
from time import sleep


def main():

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

        with uc.Chrome(options=options, enable_cdp_events=True, use_subprocess=True, headless=False, user_data_dir=profile_path) as driver:

            driver.add_cdp_listener('*', res_processing)
            driver.get('https://www.ozon.ru/')
            sleep(4)
            search_string = driver.find_element(By.NAME, 'text')
            search_string.click()
            for letter in product:
                search_string.send_keys(letter)
                sleep(random.uniform(0.28, 0.52))
            search_string.send_keys(Keys.ENTER)
            sleep(8)
   
    except BaseException as err:
        print(err)

    finally:
        driver.quit()
        sleep(2)
        os._exit(0)

        
def res_processing(event_data):
    log = event_data
    if log['method']== 'Network.responseReceived':
        head_res = log['params']['response']
        if head_res['status'] == 200 and 'json' in head_res['mimeType']:
            res_id = log['params']['requestId']
            res = driver.execute_cdp_cmd('Network.getResponseBody',  {'requestId': res_id})
            print(res, end='\n\n')


if __name__ == '__main__':
    main()
