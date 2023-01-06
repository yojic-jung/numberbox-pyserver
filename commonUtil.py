import os, stat
from datetime import datetime
import shutil
import commonUtil
#import numpy as np
#import cv2

def delete_old_files(path_target, timeUnit, time_elapsed, ext):
    """path_target:삭제할 파일이 있는 디렉토리, days_elapsed:경과일수"""
    if timeUnit == "minute":
        time_elapsed = time_elapsed * 60
    elif timeUnit == "hour":
        time_elapsed = time_elapsed * 60 * 60
    elif timeUnit == "day":
        time_elapsed = time_elapsed * 60 * 60 * 24
    else:
        time_elapsed = time_elapsed

    for f in os.listdir(path_target): # 디렉토리를 조회한다
        f = os.path.join(path_target, f)
        if os.path.isfile(f): # 파일이면
            timestamp_now = datetime.now().timestamp() # 타임스탬프
            # st_mtime(마지막으로 수정된 시간)기준 X 기준시간 경과 여부
            is_old = os.stat(f).st_mtime < timestamp_now - (time_elapsed)
            if (is_old and (f.endswith(ext.upper()) or f.endswith(ext.lower()))): # X분 경과했다면
                try:
                    os.remove(f)  # 파일을 지운다
                    print(f, 'is deleted') # 삭제완료 로깅
                except OSError: # Device or resource busy (다른 프로세스가 사용 중)등의 이유
                    print(f, 'can not delete') # 삭제불가 로깅
            else:
                print("none-exist old-file")

def delete_old_folders(path_target, timeUnit, time_elapsed):
    if timeUnit == "minute":
        time_elapsed = time_elapsed * 60
    elif timeUnit == "hour":
        time_elapsed = time_elapsed * 60 * 60
    elif timeUnit == "day":
        time_elapsed = time_elapsed * 60 * 60 * 24
    else:
        time_elapsed = time_elapsed

    for f in os.listdir(path_target):
        timestamp_now = datetime.now().timestamp()  # 타임스탬프
        #파일이 아닌 폴더인 경우
        if not os.path.isfile(path_target+"/"+f):
            is_old = os.stat(path_target+"/" + f).st_mtime < timestamp_now - (time_elapsed)
            print(is_old)
            if is_old :
                shutil.rmtree(path_target+"/"+f, onerror=commonUtil.remove_readonly)



def remove_readonly(fn, path, excinfo):
    try:
        os.chmod(path, stat.S_IWRITE)
        fn(path)
    except Exception as exc:
        print("Skipped:", path, "because:\n", exc)

"""
def pixelDiff(img1, img2):
    oneImg = cv2.imread(img1)
    one = cv2.resize(oneImg, (512, 512))
    twoImg = cv2.imread(img2)
    two = cv2.resize(twoImg, (512, 512))

    pix = np.array(one)
    pix2 = np.array(two)
    a = []
    b = []
    try:
        for y in range(0, 512):
            for x in range(0, 512):
                a.append(int((abs(int(pix[x][y][0])-int(pix2[x][y][0]))+abs(int(pix[x][y][1])-int(pix2[x][y][1]))
                              +abs(int(pix[x][y][2])-int(pix2[x][y][2])))/3))
            b.append(sum(a, 0.0)/len(a))
            a = []
    except:
        b=[100, 100, 100]
    return (sum(b, 0.0)/len(b))
"""