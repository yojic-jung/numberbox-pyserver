import socket
import os
import customHwp

server_addr = '127.0.0.1', 5555


# Create a socket with port and host bindings
def setupServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(server_addr)
    except socket.error as msg:
        print(msg)
    return s


# Establish connection with a client
def setupConnection(s):
    s.listen(5)  # Allows five connections at a time
    conn, addr = s.accept()
    return conn


# Get input from user
def GET():
    reply = input("Reply: ")
    return reply


def sendFile(filename, conn):
    f = open(filename, 'rb')
    line = f.read(1024)
    while line:
        conn.send(line)
        line = f.read(1024)
    f.close()


# Loop that sends & receives data
def dataTransfer(conn, s, mode):
    while True:
        # Send a File over the network
        if mode == "SEND":
            data = conn.recv(4);
            # 최초 4바이트는 전송할 데이터의 크기이다. 그 크기는 little big 엔디언으로 byte에서 int형식으로 변환한다.
            # C#의 BitConverter는 big엔디언으로 처리된다.
            length = int.from_bytes(data, "little")
            dividend = length//1024
            remainder = length%1024
            if remainder != 0 :
                dividend=dividend+1
            
            #데이터 분할하여 받기
            tmpByteData=bytes()
            for i in range(dividend):
                tmpData = conn.recv(1024)
                tmpByteData=tmpByteData+tmpData
                #tmpData = tmpData.decode('utf-8')
                #tmpData.strip()
            jsonData= tmpByteData.decode('utf-8')
            # 다시 데이터를 수신한다.
            filePath = customHwp.makeHwpController(jsonData)
            sendFile(filePath, conn)
            os.remove(filePath)
            # conn.send(bytes("DONE", 'utf-8'))
            break

        # Chat between client and server
        elif mode == "CHAT":
            # Receive Data
            data = conn.recv(1024)
            data = data.decode(encoding='utf-8')
            data.strip()
            command = str(data)
            if command == "QUIT":
                s.close()
                break
            # Send reply
            reply = GET()
            conn.send(bytes(reply, 'utf-8'))

    conn.close()


sock = setupServer()
while True:
    try:
        connection = setupConnection(sock)
        dataTransfer(connection, sock, "SEND")
    except:
        break