import argparse

import itertools
import logging
import os
from random import choice
from re import findall
from time import sleep

import pandas as pd
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from onesec_api import Mailbox

DB_URL = ('https://docs.google.com/spreadsheets/u/0/d/1zaxjdu9ESYy2MCNuDow0_5PnZpwEsyrdTQ_kk0PMZbw/export?'
          'format=csv&id=1zaxjdu9ESYy2MCNuDow0_5PnZpwEsyrdTQ_kk0PMZbw&gid=807277577')


class Sexmsk:
    def __init__(self, contacts, logins, passwords, titles, descriptions, proxys, headless=False):
        # self.driver.maximize_window()
        self.proxy = next(proxys)
        try:
            self.login = next(logins)
            self.password = next(passwords)
            print('{} {}'.format(self.login, self.password))
        except StopIteration:
            pass
        self.contact = next(contacts)
        options = webdriver.ChromeOptions()
        options.add_argument(f'--proxy-server={self.proxy}')
        if headless:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def photo_upload(self, input_path):
        images_folder = f'/home/danil/images'
        random_image = choice([
            file for file in os.listdir(images_folder) if findall(r'\w+$', file)[0] == 'jpg'
        ])
        jpg = images_folder + f"/{random_image}"  # image.jpg
        self.driver.find_element_by_xpath(input_path).send_keys(jpg)

    def captcha_solver(self, captcha_xpath, url):
        print('solving captcha')
        captcha_key = self.driver.find_element_by_xpath(captcha_xpath).get_attribute('data-sitekey')
        payload = dict(key='42a3a6c8322f1bec4b5ba84b85fdbe2f',
                       method='userrecaptcha',
                       googlekey=captcha_key,
                       pageurl=url,
                       json=1)
        req = requests.get('http://rucaptcha.com/in.php', params=payload)

        payload = dict(key='42a3a6c8322f1bec4b5ba84b85fdbe2f',
                       action='get',
                       id=req.json()['request'],
                       json=1)
        for _ in range(120):
            req = requests.get('http://rucaptcha.com/res.php', params=payload)
            if req.json()['status']:
                print('captcha solved')
                return req.json()['request']
            sleep(1)
        return False

    def auth(self):
        try:
            auth = 'https://sex24msk.com/index.php/sex24msk'
            self.driver.get(auth)
            WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.execute_script('return document.readyState;') == 'complete'
            )
            accept_button = '//div[2]/button[1]'
            self.driver.find_element_by_xpath(accept_button).click()
            username_field = '//*[@id="username"]'
            self.driver.find_element_by_xpath(username_field).send_keys(self.login)
            password_field = '//*[@id="password"]'
            self.driver.find_element_by_xpath(password_field).send_keys(self.password)
            entry_button = '//button[@type="submit"]'
            self.driver.find_element_by_xpath(entry_button).click()
            assert 'Предупреждение' not in self.driver.page_source
            return True
        except Exception as error:
            logging.exception(error)
            return False

    def spamming(self):
        title = choice(titles)
        description = choice(descriptions)
        try:
            url = 'https://sex24msk.com/index.php/dobavit-ob-yavlenie'
            self.driver.get(url)
            try:
                captcha_xpath = '//*[@class="g-recaptcha"]'
                captcha_answer = self.captcha_solver(captcha_xpath, url)
                if not captcha_answer:
                    print('captcha not solvable')
                    return False
                captcha_answer_input_xpath = '//*[@id="g-recaptcha-response"]'
                self.driver.execute_script(
                    'document.querySelector("#g-recaptcha-response").style="width: 250px;'
                    ' height: 40px; border: 1px solid rgb(193, 193, 193); margin: 10px 25px; padding: 0px; resize: none;"')
                self.driver.find_element_by_xpath(captcha_answer_input_xpath).send_keys(captcha_answer)
                self.driver.execute_script(
                    'document.querySelector("#g-recaptcha-response").style="width: 250px;'
                    ' height: 40px; border: 1px solid rgb(193, 193, 193); margin: 10px 25px; padding: 0px; resize: none; display: none"')
                submit_btn = '//*[@id="submit_b"]'
                self.driver.find_element_by_xpath(submit_btn).click()
            except NoSuchElementException:
                print('Капча не найдена')
            titile_field = '//input[@class="inputbox required"]'
            self.driver.find_element_by_xpath(titile_field).send_keys(title)
            woman_xpath = '//*[@id="cat_0"]/option[2]'
            self.driver.find_element_by_xpath(woman_xpath).click()
            country = '//*[@id="reg_0"]/option[2]'
            self.driver.find_element_by_xpath(country).click()
            city = '//*[@id="reg_83"]/option[8]'
            WebDriverWait(self.driver, 2).until(lambda d: self.driver.find_element_by_xpath(city)).click()
            sleep(1)
            editor_btn = '//a[@class="btn"]'
            self.driver.find_element_by_xpath(editor_btn).click()
            description_field = '//*[@id="description"]'

            WebDriverWait(self.driver, 2).until(
                ec.visibility_of_element_located((By.XPATH, description_field))).send_keys(
                f'{description}\n{self.contact}')
            contact_field = '//*[@id="contact"]'
            self.driver.find_element_by_xpath(contact_field).send_keys(self.contact)
            photo_xpath = '//input[@type="file"]'
            self.photo_upload(photo_xpath)
            submit_button = '//*[@id="submit_button"]'
            sleep(2)
            self.driver.find_element_by_xpath(submit_button).click()
            return True
        except (NoSuchElementException, TimeoutException):
            logging.exception('NoSuchElementException, TimeoutException')
            return False

    def registration(self, email):
        # email = Mailbox(domain='1secmail.com')
        print(str(email))
        try:
            reg_url = 'https://sex24msk.com/index.php/registratsiya'
            self.driver.get(reg_url)
            WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.execute_script('return document.readyState;') == 'complete'
            )
            element_xpath = '//*[@id="jform_name"]'
            self.driver.find_element_by_xpath(element_xpath).send_keys(str(email))
            element_xpath = '//*[@id="jform_username"]'
            self.driver.find_element_by_xpath(element_xpath).send_keys(str(email))
            element_xpath = '//*[@id="jform_password1"]'
            self.driver.find_element_by_xpath(element_xpath).send_keys(str(email))
            element_xpath = '//*[@id="jform_password2"]'
            self.driver.find_element_by_xpath(element_xpath).send_keys(str(email))
            element_xpath = '//*[@id="jform_email1"]'
            self.driver.find_element_by_xpath(element_xpath).send_keys(str(email))
            element_xpath = '//*[@id="jform_email2"]'
            self.driver.find_element_by_xpath(element_xpath).send_keys(str(email))
            element_xpath = '//*[@id="jform_profile_dob"]'
            self.driver.find_element_by_xpath(element_xpath).send_keys('12344123')
            element_xpath = '//*[@id="jform_profile_tos0"]'
            self.driver.find_element_by_xpath(element_xpath).click()
            captcha_xpath = '//*[@id="jform_captcha"]'
            captcha_answer = self.captcha_solver(captcha_xpath, reg_url)
            captcha_answer_input_xpath = '//*[@id="g-recaptcha-response"]'
            self.driver.execute_script(
                'document.querySelector("#g-recaptcha-response").style="width: 250px;'
                ' height: 40px; border: 1px solid rgb(193, 193, 193); margin: 10px 25px; padding: 0px; resize: none;"')
            self.driver.find_element_by_xpath(captcha_answer_input_xpath).send_keys(captcha_answer)
            element_xpath = '//*[@id="member-registration"]/div/div/button'
            self.driver.find_element_by_xpath(element_xpath).click()
            # email.mailjobs('read', email.filtred_mail())
            # mb = email.filtred_mail()
            # mf = email.mailjobs('read', mb[0])
            # js = mf.json()
            # self.driver.execute_script("window.open('');")
            # self.driver.switch_to.window(self.driver.window_handles[-1])
            # text_body = js['textBody']
            # print(text_body.splitlines()[6])
            # self.driver.get(text_body.splitlines()[6])
            sleep(2)
        except Exception as error:
            logging.exception(error)

    def main(self):
        self.auth()
        for _ in range(2):
            if not self.spamming():
                break
        self.driver.quit()


if __name__ == '__main__':
    df = pd.read_csv(DB_URL)
    titles = df['title'].dropna().tolist()
    descriptions = df['description'].dropna().tolist()
    contacts = itertools.cycle(df['contact'].dropna().tolist())
    logins = itertools.cycle(df['login'].dropna().tolist())
    passwords = itertools.cycle(df['password'].dropna().tolist())
    proxys = itertools.cycle(df['proxy'].dropna().tolist())
    while True:
        headless = False
        parser = argparse.ArgumentParser()
        parser.add_argument("--headless", dest="headless", default=headless, help='Используй для режима без браузера',
                            type=bool)
        args = parser.parse_args()
        sexmsk = Sexmsk(contacts, logins, passwords, titles, descriptions, proxys, args.headless)
        sexmsk.main()
        # mail = 'alianterent673@gmail.com'
        # sexmsk.registration(mail)