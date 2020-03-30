from selenium import webdriver


def driver_init():
    cd = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
    browser = webdriver.Chrome(cd)
    browser.maximize_window()
    return browser


def open_url(browser, url):
    browser.get(url)