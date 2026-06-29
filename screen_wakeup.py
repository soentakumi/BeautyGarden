from time import sleep
import os
import datetime
import sys
import io
import glob
import random
import psutil
import pyautogui as pgui

#スクリーンセーバーを解除する
def stop_screen_server():
    scr_files = glob.glob(r'C:\Windows\System32\*.scr')
    for scr_file in scr_files:
        procnames = scr_file.split("\\")
        procname = procnames[len(procnames)-1]
        for proc in psutil.process_iter(["pid",'cmdline' ]):
            #print("scr:"+procname+" pid:"+str(proc.pid)+" procname:"+proc.name())
            if (procname in proc.name()):
                print("terminate スクリーンセーバー　{}" .format(proc.pid))
                psutil.Process(proc.pid).terminate ()
    #マウスを移動させて、スクリーンセーバーを解除する
    pgui.moveTo(x=1, y=1, duration=1)
    print("moveTo マウス (1,1)")

#メイン
stop_screen_server()    #スクリーンセーバーを解除する
