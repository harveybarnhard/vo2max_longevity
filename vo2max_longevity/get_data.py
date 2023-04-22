import os
import pandas as pd
import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

# Get username secrets from environment
garmin_username = os.getenv('GARMIN_USERNAME')
garmin_password = os.getenv('GARMIN_PASSWORD')

# Set up chromium in headless mode
chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
chrome_options = Options()
options = [
    "--headless",
    "--disable-gpu",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--enable-javascript",
    "--disable-web-security",
    "--window-size=1920,1200",
    "--ignore-certificate-errors"
]
for option in options:
    chrome_options.add_argument(option)

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Go to Garmin Connect and wait for username input box to load
driver.get('https://sso.garmin.com/sso/signin?service=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&webhost=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&source=https%3A%2F%2Fconnect.garmin.com%2Fsignin%2F&redirectAfterAccountLoginUrl=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&redirectAfterAccountCreationUrl=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&gauthHost=https%3A%2F%2Fsso.garmin.com%2Fsso&locale=en_GB&id=gauth-widget&cssUrl=https%3A%2F%2Fconnect.garmin.com%2Fgauth-custom-v1.2-min.css&privacyStatementUrl=https%3A%2F%2Fwww.garmin.com%2Fen-GB%2Fprivacy%2Fconnect%2F&clientId=GarminConnect&rememberMeShown=true&rememberMeChecked=false&createAccountShown=true&openCreateAccount=false&displayNameShown=false&consumeServiceTicket=false&initialFocus=true&embedWidget=false&socialEnabled=false&generateExtraServiceTicket=true&generateTwoExtraServiceTickets=true&generateNoServiceTicket=false&globalOptInShown=true&globalOptInChecked=false&mobile=false&connectLegalTerms=true&showTermsOfUse=false&showPrivacyPolicy=false&showConnectLegalAge=false&locationPromptShown=true&showPassword=true&useCustomHeader=false&mfaRequired=false&performMFACheck=false&rememberMyBrowserShown=true&rememberMyBrowserChecked=false#')
wait = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'username'))
)

# Input username and password and click submit
username = driver.find_element(By.ID,'username')
password = driver.find_element(By.ID,'password')
username.send_keys(garmin_username)
password.send_keys(garmin_password)
driver.find_element('id', 'login-btn-signin').click()

# Helper class to wait until jQuery is loaded
class jquery_is_loaded(object):
    def __call__(self, driver):
        try:
            output = self.driver.execute_script('''return
                if (typeof jQuery == 'undefined') {
                    throw new Error('jQuery is not loaded');
                }''')
            return output
        except:
            return True

# Once JQuery is loaded, execute the query starting from the 22nd of July 2018 to today
#with open('./src/jquery.min.js') as f:
#    driver.execute_script(f.read())
wait = WebDriverWait(driver, 100).until(jquery_is_loaded())
time.sleep(5)

today = date.today()
query_url = ''' 'https://connect.garmin.com/modern/proxy/metrics-service/metrics/maxmet/daily/2018-07-22/2019-07-22','''
query = '''
    function(days)
    {
        days.forEach(
        function(day)
            {
                try {
                    d = day.generic;
                    console.dir(d.calendarDate, d.vo2MaxPreciseValue);
                } catch (e) {}
            }
        );
    }'''
response = driver.execute_script('return jQuery.getJSON(' + query_url  + query + ');')
driver.quit()

# Convert JSON response to dataframe, skipping null entries then save to CSV
d = []
for x in response:
    try:
        d.append(
            {
                'date': x['generic']['calendarDate'],
                'vo2max': x['generic']['vo2MaxPreciseValue']
            }
        )
    except:
        pass

df = pd.DataFrame(d)
df.to_csv('./data/vo2max.csv', index=False)
