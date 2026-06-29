#水野さんのサイト
ID="CD49226"
PW="kika@8888"
#チノちゃんのサイト
#ID="CB79350"
#PW="garden1!"
#ID="CC02553"
#PW="garden1!"
MICROSOFT_EDGE_ENABLE=False
BROWSER_DISPLAY_ENABLE=True
RANDAM_WAIT_ENABLE=True
TEST_MODE_ENABLE=False
START_TIME=8               # 開始時間(時)
END_TIME=21                # 終了時間(時)
SLEEPTIME=5
SCROLLTIME=3
PAUSETIME=30
TIMEOUT=3*60               # 3分
WAIT_LONG_MINS=20*60       # 20分
WAIT_A_NEW_SECS=0
WAIT_A_NEW_MINS=1

HELP_USAGE="usage:%s\tid=ユーザID pw=パスワード [-nowait] [-test]"
VERSION="ver.1.00"

import pyperclip
import pyautogui as pgui

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from time import sleep
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import urllib.parse
import datetime
import sys
import io
import datetime
import glob
import random
import winsound
import psutil
import subprocess

#タイムスタンプ取得
def timestamp(dt):
    ts = f'{dt.year:04}{dt.month:02}{dt.day:02}{dt.hour:02}{dt.minute:02}{dt.second:02}'
    return ts

#タイムスタンプ付きの拡張ログ
def log_print(text):
    dt_now = datetime.datetime.now()
    log_msg = str(dt_now).split(".")[0]+" "+text
    print(log_msg)

#スクリーンセーバーを解除する
def stop_screen_server():
    try:
        scr_files = glob.glob(r'C:\\Windows\\System32\\*.scr')
        for scr_file in scr_files:
            procnames = scr_file.split("\\")
            procname = procnames[len(procnames)-1]
            for proc in psutil.process_iter(["pid",'cmdline' ]):
                #print("scr:"+procname+" pid:"+str(proc.pid)+" procname:"+proc.name())
                if (procname in proc.name()):
                    print("terminate スクリーンセーバー　{}" .format(proc.pid))
                    psutil.Process(proc.pid).terminate ()
    except:
        pass      
    #マウスを移動させて、スクリーンセーバーを解除する
    pgui.moveTo(x=1, y=1, duration=1)
    print("moveTo マウス (1,1)")

#ランダムに待つ
def randam_wait(type):
    if (type == WAIT_A_NEW_MINS):
        wait = random.randint(31, 39)
    if (type == WAIT_A_NEW_SECS):
        wait = random.randint(5, 9)
    log_print("wait "+str(wait)+" [sec]")
    sleep(wait)
    #スクリーンセーバーを解除する
    try:
        stop_screen_server()
    except:
        pass
    
# 指定文字列を含むポップアップが出ていたら閉じる
def close_popup_by_text(driver, popup_text):
    old_wait = TIMEOUT

    try:
        # 任意ポップアップ確認で長時間止まらないように一時的に implicit wait を切る
        driver.implicitly_wait(0)

        # ブラウザ標準アラートの場合
        try:
            alert = driver.switch_to.alert
            text = alert.text
            if popup_text in text:
                log_print("popup alert 検出: " + text)
                alert.dismiss()
                log_print("popup alert を閉じました")
                return True
        except NoAlertPresentException:
            pass
        except Exception:
            pass

        # HTMLポップアップの場合
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
        except Exception:
            body_text = ""

        if popup_text not in body_text:
            log_print("popup なし: " + popup_text)
            return False

        log_print("popup 検出: " + popup_text)

        # 「はい」などの本文ボタンは押さない。閉じるボタンだけを探す。
        close_candidates = [
            "//button[contains(@class, 'close')]",
            "//a[contains(@class, 'close')]",
            "//button[@aria-label='Close']",
            "//button[@aria-label='閉じる']",
            "//a[@aria-label='Close']",
            "//a[@aria-label='閉じる']",
            "//*[normalize-space()='×']",
            "//*[normalize-space()='✕']",
            "//*[normalize-space()='✖']",
            "//*[normalize-space()='閉じる']",
        ]

        for xpath in close_candidates:
            try:
                elems = driver.find_elements(By.XPATH, xpath)
                for elem in elems:
                    if elem.is_displayed() and elem.is_enabled():
                        elem.click()
                        log_print("popup の閉じるボタンをクリック: " + popup_text)
                        sleep(1)
                        return True
            except Exception:
                pass

        log_print("popup は検出したが、閉じるボタンをクリックできませんでした: " + popup_text)
        return False

    finally:
        driver.implicitly_wait(old_wait)

# 指定URLから別URLへ変わるまで待つ
def wait_url_changed(driver, before_url):
    for i in range(TIMEOUT):
        current_url = driver.current_url
        log_print("url wait current_url=" + current_url)

        if current_url != before_url:
            log_print("url changed: " + before_url + " -> " + current_url)
            return True

        sleep(1)

    log_print("url not changed timeout: " + before_url)
    return False

#メイン
log_print("【BeautyGarden自動アクセスプログラム】"+VERSION)
psw = os.getcwd()
log_print(psw);
today = datetime.datetime.now()
ts = timestamp(today)
random.seed(int(ts))
cdate = int(ts[0:8])
chour = int(ts[8:10])

#コマンドの引数解析
args = sys.argv
if (len(args) > 1):
    for arg in args:
        if (arg.startswith('-id=')):
            ID = arg.split('=')[1]
        if (arg.startswith('-pw=')):
            PW = arg.split('=')[1]
        if (arg.startswith('-nowait')):
            RANDAM_WAIT_ENABLE = False
        if (arg.startswith('-test')):
            TEST_MODE_ENABLE=True
            RANDAM_WAIT_ENABLE = False
        if (arg.startswith('--help')):
            log_print(HELP_USAGE.replace('%s',args[0]))
            sys.exit()
            
if (len(ID) == 0) or (len(PW) == 0):
    log_print(HELP_USAGE.replace('%s', args[0]))
    sys.exit()

# 環境変数USERNAMEによる依存フォルダの設定
username = os.environ['USERNAME']

while 1:
    
    if MICROSOFT_EDGE_ENABLE:
        # Edge ドライバの組み込み
        web_driver_path = ".\\msedgedriver.exe"
        edge_service = EdgeService(web_driver_path)
        driver = webdriver.Edge(service=edge_service)
    else:
        # Chrome ドライバの組み込み
        web_driver_path = ".\\chromedriver.exe"
        chrome_service = ChromeService(web_driver_path)
        if BROWSER_DISPLAY_ENABLE:
            driver = webdriver.Chrome(service=chrome_service)
        else:
            options = Options()
            options.add_argument('--headless')
            driver = webdriver.Chrome(service=chrome_service, options=options)
        
    nowts = timestamp(today)
    nowchour = int(ts[8:10])
    if (nowchour >= END_TIME):
        break
    if (nowchour < START_TIME):
        sleep(PAUSETIME) 
        continue
    
    #ランダムに数分待つ 
    if (RANDAM_WAIT_ENABLE):
        randam_wait(WAIT_A_NEW_MINS)
        
    driver.set_page_load_timeout(TIMEOUT)     #タイムアウト
    driver.implicitly_wait(TIMEOUT)           #タイムアウト
    
    #ログイン
    URL="https://salonboard.com/login/"
    driver.get(URL)                #対象のサイトを開く
    sleep(SLEEPTIME)

    # ログイン前のヘルプポップアップを閉じる
    close_popup_by_text(driver, "ログインでお困り")
    sleep(SLEEPTIME)
    
    #ログインのIDとPWの設定
    elem_user_id = driver.find_element(By.NAME, "userId")
    elem_user_id.send_keys(ID)
    elem_user_pw = driver.find_element(By.NAME, "password")
    elem_user_pw.send_keys(PW)
    elem_login = driver.find_element(By.CSS_SELECTOR, "a.loginBtnSize")
    sleep(SLEEPTIME)
    
    #ログインの実行
    #elem_user_id.send_keys(Keys.ENTER)
    elem_login.click()

    if not wait_url_changed(driver, URL):
        log_print("login要求後にURLが変わりませんでした")
        driver.quit()
        sys.exit(1)
    
    #画像ログイン対応
    try:
        elem_login_btn = driver.find_element(By.NAME, "captchaLogin")
        log_print("loginのための画像認証が必要です")
        log_print("画像を30秒以内に合わせて下さい")
        log_print(f"login ID={ID} request")
        for i in range(5):
            winsound.MessageBeep()
            sleep(1)  # 1秒間隔
        sleep(30)
        elem_login_btn.click()
        try:
            #トップ画面 or 画像認証エラー画面
            sleep(SLEEPTIME)
            ret_btn = driver.find_element(By.XPATH, "//input[@type='button' and @value='戻る']")
            #画像認証エラー
            log_print("login error")
            log_print(f"login ID={ID} request") #再度、手動で起動する
            # ===== ここから再実行スケジュール =====
            log_print(f"1時間後に ID={ID} 再実行をスケジュールします...")
            command = f"python auto.py -id={ID} -pw={PW}"
            current_dir = os.getcwd()  # 現在の作業ディレクトリ
            # 15分（900秒）後に実行
            subprocess.Popen(
                ["cmd", "/c", f"timeout /t 900 /nobreak && {command}"],
                cwd=current_dir,  # 親と同じディレクトリを指定
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            log_print(f"ID={ID} スケジュール完了。終了します。")
            sys.exit(1)
        except Exception as e:
            #トップ画面
            log_print("login")  #画像確認あり(人手による対応)でlogin成功
    except Exception as e:
        #トップ画面
        log_print("login")  #画像確認なしでlogin成功

    #掲載管理
    url = "https://salonboard.com/CNK/reflect/reflectTop/" 
    log_print(url)
    driver.get(url)                #対象のサイトを開く
    sleep(SLEEPTIME)

    #メニュー
    url = "https://salonboard.com/CNK/draft/menuEdit/" 
    log_print(url)
    driver.get(url)                #対象のサイトを開く
    sleep(SLEEPTIME)
    
    elem = driver.find_element(By.ID, "moveBtn chk btn_reg")
    log_print(url)
    elem.click()
    log_print('click')
    sleep(SLEEPTIME)
    
    #放置する
    sleep(PAUSETIME)
    
    elem_form = driver.find_element(By.ID, "formReflectedButton")
    elem = elem_form.find_element(By.TAG_NAME, "img")
    elem.click()
    log_print('click')
    sleep(SLEEPTIME)
    
    #放置する
    sleep(PAUSETIME)
    
    #掲載管理
    url = "https://salonboard.com/CNK/reflect/reflectTop/" 
    log_print(url)
    driver.get(url)                #対象のサイトを開く
    sleep(SLEEPTIME)
    
    #放置する
    sleep(PAUSETIME)
        
    #Webドライバを終了する
    driver.quit()
    
    sleep(WAIT_LONG_MINS) 
exit(0)