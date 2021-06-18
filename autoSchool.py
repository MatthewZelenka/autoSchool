from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from datetime import time as dttime
import time, json, os, sys, re

print(len(sys.argv))
print(sys.argv)

valURL = re.compile( # regex to see if valid url
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def getClasses(): # gets list of school classes you have put in your user.json file
    try:
        with open("user.json", "r") as read_file:
            data = json.load(read_file)
            return data["classes"].keys()
    except FileNotFoundError:
        print("user.json is not found")

def waitUntilTime(startTime = None, overridemsg="Overrieded"): # waits for the time to be passesed or and override to continue
    print("Press Ctrl+C to overide wait timer")
    try:
        while True: # wits for time to pass
            if False if startTime == None else datetime.now().time() >= dttime(int(startTime.split(":")[0]),int(startTime.split(":")[1])):
                return True 
            time.sleep(1)
    except KeyboardInterrupt: # contunues on keyboard interrupt
        print(overridemsg)
        return False

class autoClass: # Auto joining class class
    def __init__(self, schoolClass, timeStart, timeEnd, url, webDriverPath="./chromedriver", browser=None, browserHide = False):
        self.schoolClass = schoolClass
        self.timeStart = timeStart
        self.timeEnd = timeEnd
        #url of the page we want to run
        self.url = url
        self.webDriverPath = webDriverPath
        self.browser = browser
        self.browserHide = browserHide
    
    def waitUrlChange(self, currentURL): # function to wait for next page to load before continuing 
        WebDriverWait(self.driver, 10).until(lambda driver: driver.current_url != currentURL)
    
    def getToClass(self):
        inClass = False
        while inClass == False:
            currentUrl = self.driver.current_url
            if currentUrl.find("https://accounts.google.com/signin/v2/identifier?") != -1: # logs you in to google in order to access the link provided 
                print("Logging in to google...")
                with open("user.json", "r") as read_file: # puts email in to google login from user.json
                    data = json.load(read_file)
                    login = self.driver.find_element_by_css_selector(".whsOnd.zHQkBf")
                    login.send_keys(data["user"]["email"])
                    self.driver.find_element_by_class_name("VfPpkd-dgl2Hf-ppHlrf-sM5MNb").click()
                self.waitUrlChange(currentUrl)
                
            elif currentUrl.find("https://accounts.google.com/signin/v2/challenge/pwd?") != -1: # next step in google log in for password
                print("Putting in password...")
                with open("user.json", "r") as read_file: # puts password in to google login from user.json
                    data = json.load(read_file)
                    login = self.driver.find_element_by_css_selector(".whsOnd.zHQkBf")
                    login.send_keys(data["user"]["password"])
                    self.driver.find_element_by_class_name("VfPpkd-dgl2Hf-ppHlrf-sM5MNb").click()
                self.waitUrlChange(currentUrl)
            
            elif currentUrl.find("https://google.yrdsb.ca/LoginFormIdentityProvider/Login.aspx?") != -1: # YRDSB has stupid special login page for google accounts so it goes through that
                print("Logging in to YRDSB...")
                time.sleep(0.5)
                with open("user.json", "r") as read_file: # gets user and password from user.json and puts it into login page for YRDSB
                    data = json.load(read_file)
                    login = self.driver.find_element_by_id("UserName")
                    login.send_keys(data["user"]["userName"])
                    login = self.driver.find_element_by_id("Password")
                    login.send_keys(data["user"]["password"])
                    self.driver.find_element_by_name("LoginButton").click()
                self.waitUrlChange(currentUrl)

            elif currentUrl.find("https://classroom.google.com/u/") != -1: # Goes into classroom
                print("Locating Call...")
                try:
                    meet = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".tnRfhc.etFl5b"))) # grabs the meet link form the header of the page where a meet link usually is
                    self.driver.get(meet.get_attribute('href'))
                    self.waitUrlChange(currentUrl) # switches webpage to the url from classroom header
                except:
                    print("Meet not on classroom trying again in 5 seconds") # if meet in header not there waits then goes through again
                    time.sleep(5)
            elif currentUrl.find("https://meet.google.com/lookup/") != -1: # once in meet turns off camera and microphone and then joins
                print("Setting up Call...")
                try: # ---------------------------------------------------------------------------------- can not test yet
                    # print(eeeee)
                    # mute = self.driver.find_element_by_class_name("tnRfhc etFl5b")
                    mute = WebDriverWait(self.driver, 2.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".U26fgb.JRY2Pb.mUbCce.kpROve.yBiuPb.y1zVCf.M9Bg4d.HNeRed")))
                    mute.click()
                    disableCam = WebDriverWait(self.driver, 2.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".U26fgb.JRY2Pb.mUbCce.kpROve.yBiuPb.y1zVCf.M9Bg4d.HNeRed")))
                    disableCam.click()
                    joinClass = WebDriverWait(self.driver, 2.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".U26fgb.JRY2Pb.mUbCce.kpROve.yBiuPb.y1zVCf.M9Bg4d.HNeRed")))
                    joinClass.click()
                    # self.waitUrlChange(currentUrl)
                    inClass = True
                except:
                    meet = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "VfPpkd-dgl2Hf-ppHlrf-sM5MNb"))) # if meet is not open yet just keeps refreshing page until it is
                    meet.click()
                else:
                    print("Meet is broken trying again in 10 seconds") # if meet does not load at all refreshes page and trys again after 10 seconds
                    time.sleep(10)
                    self.driver.refresh()

    def run(self):
        try:
            # set up
            caps = DesiredCapabilities().CHROME
            # caps["pageLoadStrategy"] = "normal"  #  complete
            caps["pageLoadStrategy"] = "eager"  #  interactive
            # caps["pageLoadStrategy"] = "none"   #  undefined

            chromeOptions = webdriver.chrome.options.Options()
            if self.browserHide == True: # hides web browser if true
                chromeOptions.headless = True
            try:
                if self.browser != None: # uses chrome by default if put in another browser location trys to use that browser
                    chromeOptions.binary_location = self.browser
            except:
                print("Browser in that location does not exist")
            chromeOptions.add_argument("use-fake-ui-for-media-stream") # enables camera and mic so they work if needed

            # initiating the webdriver. Parameter includes the path of the webdriver.
            self.driver = webdriver.Chrome(desired_capabilities=caps, executable_path=self.webDriverPath, options=chromeOptions)
            self.driver.get(self.url) # goes to starting url
            self.getToClass()
            print("timer Started")
            if self.timeEnd != None:
                if waitUntilTime(startTime=self.timeEnd, overridemsg="") == False:
                    print("Bypassing end time")
                    waitUntilTime()
            else:
                waitUntilTime()
        except:
            print("Driver has stopped working\nShutting down...") # if something fails in the process of logging in to class it shuts down

    def quit(self):
        self.driver.quit() # quits webdriver

# Program starts running
if __name__ == '__main__':
    if len(sys.argv) == 1: # if one argument ie file location parent application
        try: # parent process trys to make duplicate of itself based on how many classes you have and sets them up to run 
            for schoolClass in getClasses():
                os.system("start autoSchool.py %s" % schoolClass)
        except json.decoder.JSONDecodeError:
            print("json file does not have classes")

    elif len(sys.argv) == 2 and ((re.match(valURL, sys.argv[1]) is not None) or (sys.argv[1] in getClasses())): # if two argument ie file location and parameter child application
        print("got right amount of info")
        print(sys.argv[1])
        # sets default assuming it only got url
        schoolClass = None
        timeStart = None
        timeEnd = None
        url = sys.argv[1] 
        if sys.argv[1] in getClasses(): # if it is a class form user.json then sets up appropriately
            with open("user.json", "r") as read_file: 
                data = json.load(read_file)
                schoolClass = sys.argv[1]
                timeStart = data["classes"][sys.argv[1]]["startTime"]
                timeEnd = data["classes"][sys.argv[1]]["endTime"]
                url = data["classes"][sys.argv[1]]["url"]
        print(schoolClass, url)
        if timeEnd == None or datetime.now().time() <= dttime(int(timeEnd.split(":")[0]),int(timeEnd.split(":")[1])): # starts class if it is not passed the end time or if there is no end time
            schoolClass = autoClass(schoolClass = schoolClass, timeStart = timeStart, timeEnd = timeEnd, url = url ,browser = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe" , browserHide = False)
            waitUntilTime(startTime=timeStart)
            schoolClass.run()
            time.sleep(5)
            schoolClass.quit()
    else:
        print("incorrect input")
