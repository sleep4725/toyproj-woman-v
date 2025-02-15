from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver

'''
@author Teddy
@email sleep4725@naver.com
@date 20250215
'''
class EngineSelenium:
    
    @classmethod
    def get_selenium_client(cls)-> WebDriver:
        '''
        '''    
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # 브라우저 창을 띄우지 않음 (옵션)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)