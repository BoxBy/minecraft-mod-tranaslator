import zipfile
import glob
import json
import shutil
import commentjson
import googletrans
import requests
from tqdm import tqdm
import os
import argparse
from translator import init_api, translate_papago
import time

import deepl

from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

auth_key = "" # Your DeepL API Key

headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "Your API Key",
	"X-RapidAPI-Host": "Custom Host"
}

parser = argparse.ArgumentParser(description='Minecraft Mod Translator')
parser.add_argument('-m', '--mode', type=str, default='cli', choices=['google', 'papago', 'deepl', 'crawl'], help='one of google, papago, deepl, crawl')
parser.add_argument('api_key', type=str, default=None, help='API Key for DeepL')

if parser.api_key is not None:
    auth_key = parser.api_key

translated = './translated_mods'

class JsonExporter:
    def __init__(self, mode='google') -> None:
        self.mod_list = glob.glob("./mods/*.jar")
        if os.path.isdir(translated) is False:
            os.mkdir(translated)
        if os.path.isdir('./temp') is False:
            os.mkdir('./temp')

        self.mode = mode
        self.translated_list = glob.glob(translated + "/*.jar")
        if self.translated_list != []:
            print(f'Find Already Translated {len(self.translated_list)} files')
        if self.mode == 'google':
            self.translator = googletrans.Translator()
        elif self.mode == 'papago':
            self.request = init_api()
        elif self.mode == 'crawl':
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
            self.url = 'https://www.deepl.com/ko/translator#en/ko/'
            self.wait = WebDriverWait(self.driver, 4)
            self.source = '#panelTranslateText > div.lmt__sides_container > div.lmt__sides_wrapper > section.lmt__side_container.lmt__side_container--target > div.lmt__textarea_container.lmt__raise_alternatives_placement > div.lmt__inner_textarea_container > d-textarea > div > p > span'
            self.source_alter = '#panelTranslateText > div.lmt__sides_container > div.lmt__sides_wrapper > section.lmt__side_container.lmt__side_container--target > div.lmt__textarea_container > div.lmt__inner_textarea_container > d-textarea > div > p > span'
        elif self.mode =='deepl':
            self.translator = deepl.Translator(auth_key)

        self.translate = {
            'google': self.translate_google,
            'deepl': self.translate_deepl,
            'papago': self.translate_papago,
            'crawl': self.translate_crawl,
        }

    def oneFile(self, _file):
        json_file, lang_path = self.postProcessing(jar_file=_file)
        if json_file is None:
            print(lang_path)
            return None
        pbar = tqdm(json_file.keys(),
                    desc=f'Translate {_file}',
                    position=1,
                    leave=False
                    )
        result_json = self.translate[self.mode](pbar, _json_data=json_file)
        self.saveJar(result_json, _file, lang_path)
        print(f"Translated {_file}")

    def allFile(self):
        pbar = tqdm(self.mod_list,
                    desc="desc",
                    position=0)
        for file in pbar:
            pbar.set_description(f'Current File: {file}')

            zip_path = file.replace("mods", "translated_mods")
            copy_path = file.replace("mods", "temp")
            zip_path = zip_path.replace(".jar", "_korean.jar")
            if zip_path in self.translated_list:
                print(f'{zip_path} is already translated')
                continue
            else :
                shutil.copy(file, copy_path)
            translate = self.oneFile(copy_path)
            shutil.copy(copy_path, zip_path)
            os.remove(copy_path)
            if translate is None:
                continue

    def postProcessing(self, jar_file :str="jar_file"):
        json_file = "json_file"
        file_list = zipfile.ZipFile(jar_file, 'r')
        for _file in file_list.namelist():
            if "ko_kr.json" in _file:
                return None, f'Korean Language file is already exist at {jar_file}'
        for _file in file_list.namelist():
            if "en_us.json" in _file:
                try:
                    json_file = json.loads(file_list.read(_file))
                except:
                    try:
                        json_file = commentjson.loads(file_list.read(_file))
                    except:
                        print(f"Error occured at {jar_file}")
                        return None, None
                    
                file_list.close()
                return json_file ,_file
        print(f"Here is no Language file at {jar_file}")
        return None, None
    
    def translate_cli(self, pbar, _json_data : dict="Json File"):
        result = _json_data.copy()
        error_count=0
        for _key in pbar:
            try:
                result[_key] = self.translator.translate(_json_data[_key])
                error_count=0
                print(f' translate {_json_data[_key]} to {result[_key]}')
            except Exception as e:
                print(f'{result[_key]} 를 번역하는 도중 문제가 생겼습니다.')
                print(e)
                result[_key] = _json_data[_key]
                error_count+=1
                if error_count > 10:
                    print("10번 이상 에러가 발생하여 번역을 종료합니다.")
                    quit()

        return result

    def translate_google(self, pbar, _json_data :dict="Json File"):
        result = _json_data.copy()
        for _key in pbar:
            try:
                result[_key] = self.translator.translate(_json_data[_key], src="en", dest="ko").text
            except Exception as e:
                print(f"{result[_key]} 를 번역하는 도중 문제가 생겼습니다.")
                print(e)
                print("아 걱정마세요. 평범한 에러메세지입니다. 무료버전의 한계니 그냥 넘어가도록하죠.")
                result[_key] = _json_data[_key]
        return result
    
    def translate_deepl(self, pbar, _json_data :dict="Json File"):
        result = _json_data.copy()
        for _key in pbar:
            try:
                result[_key] = self.translator.translate(_json_data[_key], target_lang="KR").text
            except Exception as e:
                print(f"{result[_key]} 를 번역하는 도중 문제가 생겼습니다.")
                print(e)
                print("아 걱정마세요. 평범한 에러메세지입니다. 무료버전의 한계니 그냥 넘어가도록하죠.")
                result[_key] = _json_data[_key]
        return result
    
    def translate_crawl(self, pbar, _json_data :dict="Json File"):
        result = _json_data.copy()
        for _key in pbar:
            url = self.url + result[_key]

            self.driver.get(url)
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.source)))
                time.sleep(0.2)
            except:
                pass

            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            try:
                result[_key] = soup.select_one(self.source).get_text()
            except:
                try:
                    result[_key] = soup.select_one(self.source_alter).get_text()
                except:
                    print(f"{result[_key]} 를 번역하는 도중 문제가 생겼습니다.")
                    result[_key] = _json_data[_key]
        return result

    def translate_papago(self, pbar, _json_data :dict="Json File"):
        result = _json_data.copy()
        for _key in pbar:
            result[_key] = translate_papago(self.request, _json_data[_key])
            if result[_key] == -1:
                print("Something wrong... so.. just pass..")
                result[_key] = _json_data[_key]
        return result

    def saveJar(self, _result_json :dict, _zip_path :str, _lang_path :str):
        t_jar = zipfile.ZipFile(_zip_path, 'a')
        t_jar.writestr(_lang_path.replace("en_us", "ko_kr"), json.dumps(_result_json, indent=4, ensure_ascii=False))
        t_jar.close()


def run(args):
    je = JsonExporter(args.mode)
    je.allFile()


if __name__ == "__main__":
    args = parser.parse_args()
    run(args)
