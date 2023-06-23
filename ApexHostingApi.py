import asyncio
import os
import random
import time
import re
import logging

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()


class ApexHostingApi:
    APH_USERNAME = os.getenv("APH_USERNAME")
    APH_PASSWORD = os.getenv("APH_PASSWORD")
    ApexHostingPanelLoginURL = "https://panel.apexminecrafthosting.com/"
    ApexHostingPanelServerDashboardURL = "https://panel.apexminecrafthosting.com/server/"
    ServerID = None

    def __init__(self, headless=True, min_timeout=5, max_timeout=10):
        options = uc.ChromeOptions()
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/80.0.3987.163 Safari/537.36")
        options.add_argument('--disable-dev-shm-usage')
        if headless:
            options.add_argument('--headless')
        self.driver = uc.Chrome(options=options)
        self.min_timeout = min_timeout
        self.max_timeout = max_timeout

    async def get_server_status(self):
        try:
            logging.debug("Getting Server Status")
            soup = await self.go_to_console()
            status_icon_div = soup.find('div', id='statusicon-ajax')
            img_source = status_icon_div.img.attrs['src']
            status = img_source.split("/")[-1].split(".png")[0]
            logging.debug(f"Server Status: {status}")
            return status
        except Exception as err:
            logging.error(err)
            raise

    async def stop_server(self):
        try:
            logging.debug("Stopping Server")
            await self.go_to_console()
            button = self.driver.find_element("name", "yt1")
            if button.get_attribute('disabled') is not None:
                raise Exception("Failed to stop server.")
            button.click()
            logging.debug("Command sent!")
        except Exception as err:
            logging.error(err)
            raise

    async def force_stop_server(self):
        try:
            logging.debug("Force stopping Server")
            await self.go_to_console()
            button = self.driver.find_element("name", "yt3")
            if button.get_attribute('disabled') is not None:
                raise Exception("Failed to force stop server.")
            button.click()
            logging.debug("Command sent!")
        except Exception as err:
            logging.error(err)
            raise

    async def start_server(self):
        try:
            logging.debug("Starting Server")
            await self.go_to_console()
            button = self.driver.find_element("name", "yt0")
            if button.get_attribute('disabled') is not None:
                raise Exception("Failed to start server.")
            button.click()
            logging.debug("Command sent!")
        except Exception as err:
            logging.error(err)
            raise

    async def restart_server(self):
        try:
            logging.debug("Restarting Server")
            await self.go_to_console()
            button = self.driver.find_element("name", "yt2")
            if button.get_attribute('disabled') is not None:
                raise Exception("Failed to restart server.")
            button.click()
            logging.debug("Command sent!")
        except Exception as err:
            logging.error(err)
            raise

    async def go_to_dashboard(self):
        self.driver.get(self.get_server_dashboard_url())
        await asyncio.sleep(self.get_timeout())
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, features="html.parser")
        if soup.find('div', id='statusicon-ajax') is None:
            raise Exception("Server dashboard failed to load.")
        return soup

    async def go_to_console(self):
        self.driver.get(self.get_server_console_url())
        await asyncio.sleep(self.get_timeout())
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, features="html.parser")
        if soup.find('div', id='statusicon-ajax') is None:
            raise Exception("Server dashboard failed to load.")
        return soup

    async def run_console_command(self, command):
        try:
            logging.debug("Running console command: ", command)
            await self.go_to_console()
            self.driver.find_element("id", "command").send_keys(command)
            button = self.driver.find_element("name", "yt4")
            if button.get_attribute('disabled') is not None:
                raise Exception("Failed to send command to server.")
            button.click()
            logging.debug("Command sent!")
        except Exception as err:
            logging.error(err)
            raise

    async def get_console_log(self, lines=10):
        try:
            logging.debug("Getting console logs")
            soup = await self.go_to_console()
            console_log = soup.find('div', id='log-ajax')
            log_entry_regex = "\d{2}.\d{2} \d{2}:\d{2}:\d{2}"
            entries = re.sub(log_entry_regex, lambda x: '\n' + x.group(0), console_log.text)
            entries = entries.split('\n')
            return '\n'.join(list(filter(None, entries))[-lines:])
        except Exception as err:
            logging.error(err)
            raise

    def get_server_dashboard_url(self):
        return self.ApexHostingPanelServerDashboardURL + self.ServerID

    def get_server_console_url(self):
        return self.ApexHostingPanelServerDashboardURL + "log/" + self.ServerID

    async def login(self):
        try:
            logging.debug("Loading Login Page")
            self.driver.get(self.ApexHostingPanelLoginURL)
            element = None
            try:
                element = WebDriverWait(self.driver, self.get_timeout()).until(
                    EC.presence_of_element_located((By.ID, 'LoginForm_name')))
            except:
                pass
            if element is None:
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, features="html.parser")
                if soup.find('li', id='logout_link') is not None:
                    # We are already logged in
                    logging.debug("Already Logged In! Skipping...")
                    await self.get_server_id()
                    return
                else:
                    raise Exception("Login Page Unable to load")
            logging.debug("Login Page Loaded")
            self.driver.find_element("id", "LoginForm_name").send_keys(self.APH_USERNAME)
            self.driver.find_element("id", "LoginForm_password").send_keys(self.APH_PASSWORD)
            self.driver.find_element("name", "yt0").click()
            logging.debug("Trying login...")
            await asyncio.sleep(self.get_timeout())
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, features="html.parser")
            soup.find('div', id='LoginForm_name')
            if soup.find('div', class_='errorMessage') is not None:
                raise Exception("Login Failed. Either Username/Password is incorrect")
            if soup.find('li', id='logout_link') is None:
                raise Exception("Login Failed. Api blocked by Url.")
            logging.debug("Login Succeeded")
            await self.get_server_id()
        except Exception as err:
            logging.error(err)
            raise

    async def get_server_id(self):
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, features="html.parser")
        server_index = soup.find('a', class_='btn btn-primary btn-block').attrs['href']
        server_index_url = self.ApexHostingPanelLoginURL + server_index[1:]
        self.driver.get(server_index_url)
        element = None
        try:
            element = WebDriverWait(self.driver, self.get_timeout()).until(
                EC.presence_of_element_located((By.ID, 'statusicon-ajax')))
        except Exception:
            pass
        if element is None:
            raise Exception("Server dashboard failed to load.")
        url = self.driver.current_url
        self.ServerID = url.split('/')[-1]
        logging.debug("Server Id: ", self.ServerID)
        return self.ServerID

    def get_timeout(self):
        return random.randint(self.min_timeout, self.max_timeout)
