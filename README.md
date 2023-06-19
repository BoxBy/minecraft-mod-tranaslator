# minecraft-Mod-Translator

[lazylee-l2i/minecraft-Mod-Translator](https://github.com/lazylee-l2i/minecraft-Mod-Translator)를 기반으로 개선하였습니다

# 개선사항

1. translated_mods 폴더는 이제 자동으로 만들어지며, 번역된 모드 파일이 이미 존재할 경우, 다시 번역하지 않습니다.
2. 딥러닝 기반 번역기인 [DeepL](https://www.deepl.com/translator)에 대한 지원을 추가하였습니다.  
현재 DeepL은 한국에 API가 제공되지 않아, 크롤링을 통해 지원합니다.  
3. Google Translate와 Papago Translate 버전을 통합하였습니다.  
4. 이제 어떤 문장이 번역에 실패했는지 알 수 있습니다.  
5. 번역할 모드를 선택할 수 있도록 하였습니다.  
--mode 옵션을 통해 선택할 수 있으며, google, papago, deepl, crawl 4가지 모드가 있습니다.
6. 기존 깃허브와 동일하게, MIT 라이센스를 적용하였습니다.  
배포/수정/상업적 이용 등 모든 용도로 자유롭게 사용하실 수 있습니다.

# Requirements
1. python 3.7 이상  
2. commentjson==0.9.0  
3. googletrans==4.0.0rc1  
4. selenium==3.141.0  
5. tqdm==4.62.3  
6. beautifulsoup4==4.10.0  
~~7. chrome driver가 필요합니다. [다운로드](https://chromedriver.chromium.org/downloads)~~ webdriver-manager 라이브러리 추가하여 요구하지 않습니다

# 사용방법
1. **mod**폴더에 번역하고자 하는 jar 모드 파일을 넣습니다.
2. (**cmd** or **powershell**) python main.py --mode [google, papago, deepl, crawl]
3. 열심히 기다립니다.
4. **translated_mod**에 번역된 jar 모드 파일이 있을겁니다.
5. 이제 그 모드파일을 가져다 적용하고 즐기세요!


# minecraft Mod Translator  
## (부제)영어가 딸려서 만든 모드 번역기  

1. `모드`가 1개면 그냥 하겠는데 **pam's harvest**하다가 능지가 딸려 현타와서 만들었습니다.  
2. 해당 프로그램은 2가지 버전이 존재합니다. `구글 버전`과 `Papago 버전`입니다.  
3. 현재 `구글 버전`의 경우 `무료번역`은 가능하지만 중간 *timeout*뜨면 에러가 나서 그냥 예외처리로 영어가 그대로 들어가게 해놓았습니다.  
4. 대신 `Papago 버전`의 경우 머기업답게 준수한 퀄리티의 번역과 깔끔한 API의 도움으로 번역이 아주 잘되나 아쉽게도 돈이 들어가는 관계로 `N Cloud`에서 직접 API 키를 발급받아 사용해주시기 바랍니다. [Papago N Cloud 링크](https://www.ncloud.com/product/aiService/papagoTranslation)
5. 버전은 **branch**로 나눠놓았습니다.
  
# Requirements
1. commentjson==0.9.0  
pip install commentjson
2. googletrans==4.0.0rc1  
pip install googletrans==4.0.0rc1
# 사용방법
1. **mod**폴더에 번역하고자 하는 jar 모드 파일을 넣습니다.
2. (**cmd** or **powershell**) python main.py
3. 열심히 기다립니다.
4. **translated_mod**에 번역된 jar 모드 파일이 있을겁니다.
5. 이제 그 모드파일을 가져다 적용하고 즐기세요!  
![0](./mdimg/01.png)
# 잡담
제가 생각해도 기능구현만 우선시해서 가독성이 겁나 구린데 죄송합니다.  
아직 parameter도 설정파일로 안만들었고 UI도 없는데 직장인이라 업데이트가 많이 늦어요.  
혹시라도 이 프로그램을 사용하시고 수정이나 이슈를 알려주시면 최대한 빨리 반영하도록 하겠습니다.  
영알못들아... 나에게 힘을 줘..!!