import os
import sys
import shutil
import stat
from datetime import datetime
import json
import src.util.common_util as common_util


def delete_old_files(path_target, time_unit, time_elapsed, ext):
    """path_target:삭제할 파일이 있는 디렉토리, days_elapsed:경과일수"""
    if time_unit == "minute":
        time_elapsed = time_elapsed * 60
    elif time_unit == "hour":
        time_elapsed = time_elapsed * 60 * 60
    elif time_unit == "day":
        time_elapsed = time_elapsed * 60 * 60 * 24
    else:
        time_elapsed = time_elapsed

    for f in os.listdir(path_target):  # 디렉토리를 조회한다
        f = os.path.join(path_target, f)
        if os.path.isfile(f):  # 파일이면
            timestamp_now = datetime.now().timestamp()  # 타임스탬프
            # st_mtime(마지막으로 수정된 시간)기준 X 기준시간 경과 여부
            is_old = os.stat(f).st_mtime < timestamp_now - (time_elapsed)
            if is_old and (f.endswith(ext.upper()) or f.endswith(ext.lower())):  # X분 경과했다면
                try:
                    os.remove(f)  # 파일을 지운다
                    print(f, 'is deleted')  # 삭제완료 로깅
                except OSError:  # Device or resource busy (다른 프로세스가 사용 중)등의 이유
                    print(f, 'can not delete')  # 삭제불가 로깅
            else:
                print("none-exist old-file")


def delete_old_folders(path_target, time_unit, time_elapsed):
    if time_unit == "minute":
        time_elapsed = time_elapsed * 60
    elif time_unit == "hour":
        time_elapsed = time_elapsed * 60 * 60
    elif time_unit == "day":
        time_elapsed = time_elapsed * 60 * 60 * 24
    else:
        time_elapsed = time_elapsed

    for f in os.listdir(path_target):
        timestamp_now = datetime.now().timestamp()  # 타임스탬프
        # 파일이 아닌 폴더인 경우
        if not os.path.isfile(path_target + "/" + f):
            is_old = os.stat(path_target + "/" + f).st_mtime < timestamp_now - time_elapsed
            print(is_old)
            if is_old:
                shutil.rmtree(path_target + "/" + f, onerror=common_util.remove_readonly)


def remove_readonly(fn, path, excinfo):
    try:
        os.chmod(path, stat.S_IWRITE)
        fn(path)
    except Exception as exc:
        print("Skipped:", path, "because:\n", exc)


def safe_json_deserializer(m):
    try:
        return json.loads(m.decode('utf-8'))
    except Exception as e:
        print(f"⚠️ JSON 디코딩 실패 - 무시됨: {m} | 에러: {e}")
        return None


def get_resource_path() -> str:
    root = os.environ.get("PROJECT_ROOT", os.getcwd())  # 없으면 현재 경로
    return os.path.join(root, "resources")