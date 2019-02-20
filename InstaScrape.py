# InstaScrape.py

# With Notepad++, use F5 then copy this into box
# C:\Python27\python.exe -i "$(FULL_CURRENT_PATH)"
# C:\Users\Casivio\Anaconda3\python.exe -i "$(FULL_CURRENT_PATH)"
# C:\Users\Casey\Anaconda3\python.exe -i "$(FULL_CURRENT_PATH)"

import os
from selenium import webdriver
from time import sleep
from xlsxwriter import Workbook
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import shutil
import requests

# ------------------------------------------------------
# DEFINE FUNCTIONS
# ------------------------------------------------------

# Define last position finder
def find_last(s,t):
	last_pos = -1
	while True:
		pos = s.find(os.sep, last_pos +1)
		if pos == -1:
			return last_pos
		last_pos = pos

# ------------------------------------------------------
# INPUTS
# ------------------------------------------------------

# Define path
filePath = os.path.abspath(os.path.dirname(__file__))
# Shorten path to one folder up
filePath = filePath[:find_last(filePath,os.sep)]

# ------------------------------------------------------
# Copy ends here
# ------------------------------------------------------

class App:
	def __init__(self, username='CasivioGierkao', password='1italy', target_username='dataminer2060', path=filePath+os.sep+'Instagram Scrape'+os.sep+'InstaPhotos'):
		
		self.username = username
		self.password = password
		self.target_username = target_username
		self.path = path
		self.driver = webdriver.Chrome(filePath+os.sep+'chromedriver_win32'+os.sep+'chromedriver.exe')
		self.error = False
		self.main_url = 'https://www.instagram.com'
		self.driver.get(self.main_url)
		sleep(3)
		
		# Call log_in function
		self.log_in()
		if self.error is False:
			print('Got logged in')
			sleep(1)
			self.close_dialog_box()
			print('Got the dialog box closed')
			
			sleep(1)
			self.close_dialog_box()
			print('Got the other dialog box closed')
			
			self.open_target_profile()
			
			# Scroll down target profile to open all the images
			sleep(3)
		if self.error is False:
			self.scroll_down()
		if self.error is False:
			if not os.path.exists(path):
				os.mkdir(path)
		self.downloading_images()	
		# self.download_caption()
		
		input('Stop for now')
		
		sleep(3)
		self.driver.close()
	
	def write_captions_to_excel_file(self, images, caption_path):
		print('Writing to excel')
		# workbook = Workbook(caption_path + os.sep+'captions.xlsx')
		workbook = Workbook(os.path.join(caption_path, 'Captions.xlsx'))
		worksheet = workbook.add_worksheet()
		row = 0
		worksheet.write(row, 0, 'Image name')
		worksheet.write(row, 1, 'Caption')
		row = row + 1
		for index, image in enumerate(images):
			filename = 'image_'+str(index)+'.jpg'
			try:
				caption = image['alt']
			except KeyError:
				caption = 'No caption exists'
			worksheet.write(row,0, filename)
			worksheet.write(row,1, caption)
			print(row)
			row = row + 1
		workbook.close()
	
	def download_captions(self, images):
		captions_folder_path = os.path.join(self.path, 'captions')
		if not os.path.exists(captions_folder_path):
			os.mkdir(captions_folder_path)
		self.write_captions_to_excel_file(images, captions_folder_path)
					
	def downloading_images(self):
		soup = BeautifulSoup(self.driver.page_source, 'html.parser')
		all_images = soup.find_all('img')
		self.download_captions(all_images)
		print('Length of all images', len(all_images))
		for index, image in enumerate(all_images):
			filename = 'image_'+str(index)+'.jpg'
			image_path = os.path.join(self.path, filename)
			link = image['src']
			print('Downloading image ', index)
			response = requests.get(link, stream=True)
			try:
				with open(image_path, 'wb') as file:
					shutil.copyfileobj(response.raw, file)   # source location, destination
			except Exception as e:
				print(e)
				print('Could not download image number ', index)
				print('Image link -->', link)
		
	def scroll_down(self):
		try:
			no_of_posts = self.driver.find_element_by_xpath('//span[text()=" posts"]').text
			print(no_of_posts)
			no_of_posts = no_of_posts.replace(' posts','')
			no_of_posts = no_of_posts.replace(',','')
			self.no_of_posts = int(no_of_posts)
			if self.no_of_posts > 12:
				no_of_posts = int(self.no_of_posts/12) + 3
				
				try:
					for value in range(no_of_posts):
						self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
						sleep(3)
				except Exception as e:
					self.error = True
					print(e)
					print('Some error occured while trying to scroll down')
					
		except Exception:
			print('Could not find number of posts while trying to scroll down')
			self.error = True
			
	def open_target_profile(self):
		try:
			search_bar = self.driver.find_element_by_xpath('//input[@class="XTCLo x3qfX "]')
			search_bar.send_keys(self.target_username)
			target_profile_url = self.main_url+'/'+self.target_username+'/'
			self.driver.get(target_profile_url)
			sleep(3)
		except Exception:
			self.error = True
			print('Could not find search bar')
			
	def close_dialog_box(self):
		# reload page
		sleep(1)
		self.driver.get(self.driver.current_url)
		sleep(2)
		try:
			sleep(1)
			not_now_btn = self.driver.find_element_by_xpath('//*[text()="Not Now"]')
			not_now_btn.click()
			sleep(1)
		except Exception:
			pass
			
	def close_settings_tab(self):
		try:
			self.driver.switch_to_window(self.driver.window_handles[1])
			self.driver.close()
			self.driver.switch_to_window(self.driver.window_handles[0])
		except Exception:
			pass
	
	def log_in(self,):
		try:
			log_in_button = self.driver.find_element_by_xpath('//p[@class="izU2O"]/a[@href="/accounts/login/?source=auth_switcher"]')
			log_in_button.click()
			sleep(3)
			try:
				user_name_input = self.driver.find_element_by_xpath('//input[@class="_2hvTZ pexuQ zyHYP"]')
				user_name_input.send_keys(self.username)
				password_input = self.driver.find_element_by_xpath('//input[@aria-label="Password"]')
				password_input.send_keys(self.password)
				password_input.submit()
				self.close_settings_tab()
			except Exception:
				print('Some exception occurred while trying to find username or password field')
				self.error = True
				
		except Exception:
			self.error = True
			print('Unable to find login button')
		
if __name__ == '__main__':
	app = App()