import socket
import shutil
import customHwp
import commonUtil
import threading
import jobScheduler
from datetime import datetime
import random
import os
from apscheduler.schedulers.background import BackgroundScheduler

#server_addr = '127.0.0.1', 5555
server_addr = '172.31.0.169', 5555

th = []

sema = threading.Semaphore(10)

# 스케줄러 등록
sched = BackgroundScheduler(timezone='Asia/Seoul')
sched.start()
sched.add_job(jobScheduler.delete_old_file_folder, 'cron', hour='04', minute='00', id="job_1")


# Create a socket with port and host bindings
def setup_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("start sock server")
    try:
        server_socket.bind(server_addr)
        server_socket.listen(1)  # Allows five connections at a time
    except socket.error as msg:
        print(msg)
    return server_socket


# Establish connection with a client
def setup_connection(server_socket):
    client_socket, addr = server_socket.accept()
    return client_socket


def send_file(filename, conn):
    f = open(filename, 'rb')
    line = f.read(1024)
    while line:
        conn.send(line)
        line = f.read(1024)
    f.close()


# Loop that sends & receives data
def data_transfer(conn, s):
    while True:
        mode = conn.recv(4)
        mode = mode.decode('utf-8')
        # Send a File over the network
        if mode == "json":
            try:
                data = conn.recv(4)
                # 최초 4바이트는 전송할 데이터의 크기이다. 그 크기는 little big 엔디언으로 byte에서 int형식으로 변환한다.
                # C#의 BitConverter는 big엔디언으로 처리된다.
                length = int.from_bytes(data, "little")
                # 데이터 분할하여 받기
                tmpByteData = b''
                while True:
                    tmpData = conn.recv(1024)
                    tmpByteData += tmpData
                    if len(tmpByteData) == length:
                        break
                jsonData = tmpByteData.decode('utf-8')
                # 다시 데이터를 수신한다.
                sema.acquire()
                filePath = customHwp.make_hwp_controller(jsonData)
                sema.release()
                send_file(filePath, conn)
                os.remove(filePath)
                break
            except:
                break
            # conn.send(bytes("DONE", 'utf-8'))
        # Chat between client and server
        elif mode == "hwp":
            data = conn.recv(4)
            # 최초 4바이트는 전송할 데이터의 크기이다. 그 크기는 little big 엔디언으로 byte에서 int형식으로 변환한다.
            # C#의 BitConverter는 big엔디언으로 처리된다.
            length = int.from_bytes(data, "little")

            # 파일 확장자
            extByte = conn.recv(4)
            extension = int.from_bytes(extByte, "little")
            # 1: hwp, 2: hwpx, 3: hwt, 4: hwtx, 5: hml
            if extension == 1:
                extension = "hwp"
            elif extension == 2:
                extension = "hwpx"
            elif extension == 3:
                extension = "hwt"
            elif extension == 4:
                extension = "hwtx"
            elif extension == 5:
                extension = "hml"
            else:
                extension = "hwp"

            # 데이터 분할하여 받기
            tmpByteData = b''
            while True:
                tmpData = conn.recv(1024)
                tmpByteData += tmpData
                if len(tmpByteData) == length:
                    break
            # 파일명 난수로 생성
            nowDate = str(datetime.now()).replace("-", "").replace(" ", "_").replace(":", "").replace(".", "_")
            randNum = str(int(random.random() * 10 ** 9))
            fileName = nowDate + "_" + randNum + "." + extension
            filePath = os.getcwd() + "\\convertHwp\\" + fileName
            f = open(filePath, 'wb')
            f.write(tmpByteData)
            f.close()
            # 데이터 가공
            sema.acquire()
            folderName = customHwp.convert_formular_to_text(fileName)
            sema.release()

            send_file(folderName + ".zip", conn)
            # zip파일 삭제
            os.remove(folderName + ".zip")
            # 폴더 삭제
            shutil.rmtree(folderName, onerror=commonUtil.remove_readonly)
            break

        # Receive Data

    conn.close()


server_sock = setup_server()
while True:
    try:
        client_sock = setup_connection(server_sock)
    except:
        break
    client = threading.Thread(target=data_transfer, args=(client_sock, server_sock))
    client.start()
    th.append(client)
    for t in th[:]:
        if not t.is_alive():
            th.remove(t)
