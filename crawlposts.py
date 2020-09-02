from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from config import EMAIL, PASSWORD
import random

#config option
option = Options()
option.add_argument("--disable-infobars")
option.add_argument("start-maximized")
option.add_argument("--disable-extensions")
# Pass the argument 1 to allow and 2 to block
option.add_experimental_option("prefs", { 
    "profile.default_content_setting_values.notifications": 1 
})
browser = webdriver.Chrome(chrome_options=option,executable_path="./chromedriver.exe")

#Login Function
def login():
    browser.get("http://facebook.com")
    #Input email
    txtUser = browser.find_element_by_id("email")
    txtUser.send_keys(EMAIL)
    #Input password
    txtPass = browser.find_element_by_id("pass")
    txtPass.send_keys(PASSWORD)
    txtPass.send_keys(Keys.ENTER)
    sleep(5)

def getPostsURL():
    login()
    browser.get("https://www.facebook.com/groups/vieclamCNTTDaNang/")

    sleep(random.randint(5,10))

    # Search JOB
    txtSearch = browser.find_element_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div/div/form/span/span/input")
    txtSearch.send_keys("job")
    txtSearch.send_keys(Keys.ENTER)
    sleep(random.randint(10,20))
    #Tick newest posts
    browser.find_element_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div/div/div[3]/span/div/div/div[3]/div/a[2]").click()
    sleep(random.randint(10,20))
    # Choose Date
    chooseDate = browser.find_element_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div/div/div[3]/span/div/div/div[6]/div/div[1]")
    chooseDate.click()
    # Choose Month
    chooseMonth = browser.find_element_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div/div/div[3]/span/div/div/div[6]/div/div[2]/span/div[1]/input")
    browser.find_element_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div/div/div[3]/span/div/div/div[6]/div/div[2]/span/div[1]/div").click()
    sleep(random.randint(10,20))
    browser.find_element_by_xpath("/html/body/div[1]/div[3]/div[3]/div/div/div/ul/li[9]/a").click()
    sleep(random.randint(5,10))
    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        sleep(3)
        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("Finished...")
            break
        last_height = new_height
    elements = browser.find_elements_by_css_selector("._3084")
    urls = [el.get_attribute("href") for el in elements]
    
    browser.close()
    return urls


