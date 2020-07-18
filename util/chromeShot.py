from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def printR(msg,val): print("\033[91m" +'{0:35}: {1}'.format("[!] " + msg, val + '\033[00m')) 
def printG(msg,val): print("\033[92m" +'{0:35}: {1}'.format("[*] " + msg, val + '\033[00m')) 

def chromeShot (url,f):
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	chrome_options.add_argument("--window-size=1920x1080")
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("--user-data-dir /tmp")
	chrome_options.add_argument('--ignore-certificate-errors')

	chrome_driver = "/usr/bin/chromedriver"

	try:
		driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
		driver.set_page_load_timeout(3)
		driver.get(url)
		driver.get_screenshot_as_file(f)
		driver.quit()
		printG("Screenshot Done!", url) 
	except Exception as e:
		printR("Screenshot Error ...", url) 

		
