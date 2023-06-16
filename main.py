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

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "Your API Key",
	"X-RapidAPI-Host": "Custom Host"
}

parser = argparse.ArgumentParser(description='Minecraft Mod Translator')
parser.add_argument('-m', '--mode', type=str, default='google', choices=['google', 'papago', 'deepl', 'crawl'], help='one of google, papago, deepl, crawl')

translated = './translated_mods'

class JsonExporter:
    def __init__(self, mode='google') -> None:
        self.mod_list = glob.glob("./mods/*.jar")
        if os.path.isdir(translated) is False:
            os.mkdir(translated)

        self.mode = mode
        self.translated_list = glob.glob(translated + "/*.jar")
        if self.translated_list != []:
            print(f'Find Already Translated {len(self.translated_list)} files')
        if self.mode == 'google':
            self.translator = googletrans.Translator()
        elif self.mode == 'papago':
            self.request = init_api()
        elif self.mode == 'deepl':
            self.url = 'one of deepl url(DeepL or rapidapi)'
        elif self.mode == 'crawl':
            self.driver = webdriver.Chrome('./chromedriver.exe')
            self.url = 'https://www.deepl.com/ko/translator#en/ko/'
            self.wait = WebDriverWait(self.driver, 4)
            self.source = '#panelTranslateText > div.lmt__sides_container > div.lmt__sides_wrapper > section.lmt__side_container.lmt__side_container--target > div.lmt__textarea_container.lmt__raise_alternatives_placement > div.lmt__inner_textarea_container > d-textarea > div > p > span'
            self.source_alter = '#panelTranslateText > div.lmt__sides_container > div.lmt__sides_wrapper > section.lmt__side_container.lmt__side_container--target > div.lmt__textarea_container > div.lmt__inner_textarea_container > d-textarea > div > p > span'

        self.translate = {
            'google': self.translate_google,
            'deepl': self.translate_deepl,
            'papago': self.translate_papago,
            'crawl': self.translate_crawl
        }

    def oneFile(self, _file):
        json_file, lang_path = self.postProcessing(jar_file=_file)
        if json_file is None:
            print(lang_path)
            return None
        result_json = self.translate[self.mode](_json_data=json_file)
        self.saveJar(result_json, _file, lang_path)
        print(f"Translated {_file}")
        quit()

    def allFile(self):
        for count, file in enumerate(self.mod_list):
            print(f"{count+1}/{len(self.mod_list)} {file}")

            zip_path = file.replace("mods", "translated_mods")
            zip_path = zip_path.replace(".jar", "_korean.jar")
            if zip_path in self.translated_list:
                print(f'{zip_path} is already translated')
                continue
            shutil.copy(file, zip_path)
            translate = self.oneFile(zip_path)
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

    def translate_google(self, _json_data :dict="Json File"):
        result = _json_data.copy()
        for _key in _json_data.keys():
            try:
                if self.mode == 'google':
                    result[_key] = self.translator.translate(_json_data[_key], src="en", dest="ko").text
            except Exception as e:
                print(f"{result[_key]} 를 번역하는 도중 문제가 생겼습니다.")
                print(e)
                print("아 걱정마세요. 평범한 에러메세지입니다. 무료버전의 한계니 그냥 넘어가도록하죠.")
                result[_key] = _json_data[_key]
            print(result[_key])
        return result
    
    def translate_deepl(self, _json_data :dict="Json File"):
        payload = {
            "text": "This is a example text for translation.",
            "source": "EN",
            "target": "KO"
        }
        result = _json_data.copy()
        for _key in _json_data.keys():
            try:
                result[_key] = requests.post(self.url, data=payload, headers=headers).text
            except:
                print(f"{result[_key]} 를 번역하는 도중 문제가 생겼습니다.")
                print("아 걱정마세요. 평범한 에러메세지입니다. 무료버전의 한계니 그냥 넘어가도록하죠.")
                result[_key] = _json_data[_key]
        return result
    
    def translate_crawl(self, _json_data :dict="Json File"):
        result = _json_data.copy()
        for _key in _json_data.keys():
            url = self.url + result[_key]

            self.driver.get(url)
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.source)))
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

    def translate_papago(self, _json_data :dict="Json File"):
        result = _json_data.copy()
        for _key in _json_data.keys():
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
