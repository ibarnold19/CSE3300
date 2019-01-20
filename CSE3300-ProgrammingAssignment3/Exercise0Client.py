# Imports
import urllib.request, socket, random, re

############################
# Bryan Arnold             #
# 11/15/18                 #
# CSE 3300                 #
# Programming Assignment 3 #
############################

# Used this as a resource in order to find the local ip address of the machine
# https://stackoverflow.com/questions/2311510/getting-a-machines-external-ip-address-with-python
# Generate random integer for usernum and initialize ip
ipAddress = urllib.request.urlopen('https://ident.me').read().decode('utf8')
port = random.randint(0, 9000)

# Get the server ip as well as the port
hostIP = socket.gethostbyname('tao.ite.uconn.edu')
hostPort = 3300

# Create new socket and initialize it
# Generate random usernum and create student name
newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
usernum = random.randint(1000, 8000)
studentName = 'B.Arnold'

# Establish connection to the server with socket
newSocket.connect((hostIP, hostPort))

# Create string to send to the server and send it
stringToSend = ('ex0' + ' ' + str(hostIP) + '-' + str(hostPort) + ' ' + ipAddress + '-' + str(port) + ' ' + str(usernum) + ' ' + studentName + '\n').encode()
newSocket.send(stringToSend)
print('First message to the server: ' + stringToSend.decode())

# Get the data in the response back from the server
recvBuf = 1500
data = newSocket.recv(recvBuf).decode()

# If the data contained 'OK' within it, the message sent was good, so read the contents
# of the server response
if data.find("OK") != -1:

    # Print the contents of the server response and prepare the ACK message to send back
    # to the server by parsing the servernum from the response data
    print('Server response to first message: ' + data)
    recvBuff = 1500
    servernum = int(data[data.rindex(' ') + 1:])
    newStringToSend = ('ex0' + ' ' + str(usernum + 2) + ' ' + str(servernum + 1) + '\n').encode()
    print('Second message to server: ' + newStringToSend.decode())

    # Send the ack response back to the server
    # and await another server response
    newSocket.send(newStringToSend)
    newData = newSocket.recv(recvBuff).decode()

    # If the response of the ack message to the server contains
    # 'OK', the request was good so print the data
    if newData.find("OK") != -1:

        print('Second server response: ' + newData)

    # Bad request, print an error
    else:

        print('An error has occurred with sending the second message to the server: ' + newData)

# Bad request, print an error
else:

    print('An error has occurred with sending the first message to the server: ' + data)

# Close connection of the socket to the server
newSocket.close()