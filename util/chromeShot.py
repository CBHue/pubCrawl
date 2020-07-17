from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
		print("Screenshot Done! : " + url)
	except Exception as e:
		print("\033[91m" + "[!] Screenshot Error  : " + url + "\033[00m")
		
