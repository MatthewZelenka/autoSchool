from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from datetime import time as dttime
import time, json, os, sys, re

print(len(sys.argv))
print(sys.argv)

valURL = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class autoClass:
    def __init__(self, schoolClass, timeStart, timeEnd, url, webDriverPath="./chromedriver", browser=None, browserHide = False):
        self.schoolClass = schoolClass
        self.timeStart = timeStart
        self.timeEnd = timeEnd
        #url of the page we want to run
        self.url = url
        self.webDriverPath = webDriverPath
        self.browser = browser
        self.browserHide = browserHide
    
    def waitUrlChange(self, currentURL):
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.current_url != currentURL)
    
    def getToClass(self):
        inClass = False
        while inClass == False:
            currentUrl = self.driver.current_url
            if currentUrl.find("https://accounts.google.com/signin/v2/identifier?") != -1:
                print("Logging in to google...")
                with open("user.json", "r") as read_file:
                    data = json.load(read_file)
                    login = self.driver.find_element_by_css_selector(".whsOnd.zHQkBf")
                    login.send_keys(data["user"]["email"])
                    # login.send_keys(Keys.RETURN)
                    self.driver.find_element_by_class_name("VfPpkd-dgl2Hf-ppHlrf-sM5MNb").click()
                self.waitUrlChange(currentUrl)
                
            elif currentUrl.find("https://accounts.google.com/signin/v2/challenge/pwd?") != -1:
                print("Putting in password...")
                with open("user.json", "r") as read_file:
                    data = json.load(read_file)
                    login = self.driver.find_element_by_css_selector(".whsOnd.zHQkBf")
                    login.send_keys(data["user"]["password"])
                    # login.send_keys(Keys.RETURN)
                    self.driver.find_element_by_class_name("VfPpkd-dgl2Hf-ppHlrf-sM5MNb").click()
                self.waitUrlChange(currentUrl)
            
            elif currentUrl.find("https://google.yrdsb.ca/LoginFormIdentityProvider/Login.aspx?") != -1:
                print("Logging in to YRDSB...")
                time.sleep(0.5)
                with open("user.json", "r") as read_file:
                    data = json.load(read_file)
                    login = self.driver.find_element_by_id("UserName")
                    login.send_keys(data["user"]["userName"])
                    login = self.driver.find_element_by_id("Password")
                    login.send_keys(data["user"]["password"])
                    self.driver.find_element_by_name("LoginButton").click()
                self.waitUrlChange(currentUrl)

            elif currentUrl.find("https://classroom.google.com/u/") != -1:
                print("Locating Call...")
                try:
                    # meet = self.driver.find_element_by_class_name("tnRfhc etFl5b")
                    meet = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".tnRfhc.etFl5b")))
                    self.driver.get(meet.get_attribute('href'))
                    self.waitUrlChange(currentUrl)
                except:
                    print("Meet not on classroom trying again in 5 seconds")
                    time.sleep(5)
            elif currentUrl.find("https://meet.google.com/lookup/") != -1:
                print("Setting up Call...")
                try: # ---------------------------------------------------------------------------------- can not test yet
                    # print(eeeee)
                    # mute = self.driver.find_element_by_class_name("tnRfhc etFl5b")
                    mute = WebDriverWait(self.driver, 2.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".U26fgb.JRY2Pb.mUbCce.kpROve.yBiuPb.y1zVCf.M9Bg4d.HNeRed")))
                    mute.click()
                    # self.waitUrlChange(currentUrl)
                except:
                    meet = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "VfPpkd-dgl2Hf-ppHlrf-sM5MNb")))
                    meet.click()
                else:
                    print("Meet is broken trying again in 10 seconds")
                    self.driver.refresh()
                    time.sleep(10)
                # search = self.driver.find_element_by_class_name("inputId")
                # search.send_keys(self.crypto)
                # time.sleep(0.5)
                # search.send_keys(Keys.RETURN)
            # elif currentUrl.find("https://accounts.google.com/signin/v2/identifier?") != -1:
            #     print("Login")

    def run(self):
        try:
            # set up
            caps = DesiredCapabilities().CHROME
            # caps["pageLoadStrategy"] = "normal"  #  complete
            caps["pageLoadStrategy"] = "eager"  #  interactive
            # caps["pageLoadStrategy"] = "none"   #  undefined

            chromeOptions = webdriver.chrome.options.Options()
            if self.browserHide ==True:
                chromeOptions.headless = True
            if self.browser != None:
                chromeOptions.binary_location = self.browser
            # Enables camera and mic so they work if needed
            chromeOptions.add_argument("use-fake-ui-for-media-stream")

            # initiating the webdriver. Parameter includes the path of the webdriver.
            self.driver = webdriver.Chrome(desired_capabilities=caps, executable_path=self.webDriverPath, options=chromeOptions)
            self.driver.get(self.url) 
            self.getToClass()
        except:
            print("Driver has stopped working\nShutting down...")


    def quit(self):
        self.driver.quit()

def getClasses():
    try:
        with open("user.json", "r") as read_file:
            data = json.load(read_file)
            return data["classes"].keys()
    except FileNotFoundError:
        print("user.json is not found")



if __name__ == '__main__':
    if len(sys.argv) == 1:
        try:
            for schoolClass in getClasses():
                os.system("start autoSchool.py %s" % schoolClass)
        except json.decoder.JSONDecodeError:
            print("json file does not have classes")
    elif len(sys.argv) == 2 and ((re.match(valURL, sys.argv[1]) is not None) or (sys.argv[1] in getClasses())):
        print("got right amount of info")
        print(sys.argv[1])
        schoolClass = None
        timeStart = None
        timeEnd = None
        url = sys.argv[1]
        if sys.argv[1] in getClasses():
            print("in")
            with open("user.json", "r") as read_file: 
                data = json.load(read_file)
                schoolClass = sys.argv[1]
                timeStart = data["classes"][sys.argv[1]]["startTime"]
                timeEnd = data["classes"][sys.argv[1]]["endTime"]
                url = data["classes"][sys.argv[1]]["url"]
        print(schoolClass, url)
        schoolClass = autoClass(schoolClass = schoolClass, timeStart = timeStart, timeEnd = timeEnd, url = url ,browser = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe" , browserHide = False)
        schoolClass.run()
        time.sleep(5)
        schoolClass.quit()
    else:
        print("incorrect input")