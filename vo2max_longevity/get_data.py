import os
import pandas as pd
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Get username secrets from environment
garmin_username = os.getenv('GARMIN_USERNAME')
garmin_password = os.getenv('GARMIN_PASSWORD')

# Open chrome and wait for login box to load
driver = webdriver.Chrome()
driver.get('https://sso.garmin.com/sso/signin?service=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&webhost=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&source=https%3A%2F%2Fconnect.garmin.com%2Fsignin%2F&redirectAfterAccountLoginUrl=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&redirectAfterAccountCreationUrl=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&gauthHost=https%3A%2F%2Fsso.garmin.com%2Fsso&locale=en_GB&id=gauth-widget&cssUrl=https%3A%2F%2Fconnect.garmin.com%2Fgauth-custom-v1.2-min.css&privacyStatementUrl=https%3A%2F%2Fwww.garmin.com%2Fen-GB%2Fprivacy%2Fconnect%2F&clientId=GarminConnect&rememberMeShown=true&rememberMeChecked=false&createAccountShown=true&openCreateAccount=false&displayNameShown=false&consumeServiceTicket=false&initialFocus=true&embedWidget=false&socialEnabled=false&generateExtraServiceTicket=true&generateTwoExtraServiceTickets=true&generateNoServiceTicket=false&globalOptInShown=true&globalOptInChecked=false&mobile=false&connectLegalTerms=true&showTermsOfUse=false&showPrivacyPolicy=false&showConnectLegalAge=false&locationPromptShown=true&showPassword=true&useCustomHeader=false&mfaRequired=false&performMFACheck=false&rememberMyBrowserShown=true&rememberMyBrowserChecked=false#')

# Wait for username input box to load
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
                if (jQuery) {
                    return true;
                } else {
                    return false;
                }''')
            print(output)
            return output
        except:
            return True

# Once JQuery is loaded, execute the query starting from the 22nd of July 2018 to today
WebDriverWait(driver, 100).until(jquery_is_loaded())

today = date.today()
query_url = ''' 'https://connect.garmin.com/modern/proxy/metrics-service/metrics/maxmet/daily/2018-07-22/''' + str(today) + '''','''
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
df.to_csv('/Users/harveybarnhard/GitHub/vo2max_longevity/data/vo2max.csv', index=False)
