from undetected_chromedriver import By
from urllib3.exceptions import ReadTimeoutError
import undetected_chromedriver as uc
from time import sleep



def main():
    product = ''
    while True:
        product = input("Введите название товара: ")
        if product:
            break

    options = uc.ChromeOptions()
    options.binary_location = "C:\\Program Files\\Google\\Chrome Beta\\Application\\chrome.exe"
    driver = uc.Chrome(options=options)
    driver.get(f'https://www.ozon.ru/search/?from_global=true&text={product}')
    sleep(1000)

if __name__ == '__main__':
    main()
