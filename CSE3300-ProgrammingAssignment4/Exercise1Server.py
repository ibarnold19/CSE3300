import socket
import struct
import urllib.request

#############################
# Bryan Arnold              #
# CSE 3300                  #
# 12/9/18                   #
# Programming Assignment 4  #
#############################

# Get local IP address as well as the information within the database of Social
# Security Numbers to PO Boxes
host_ip_address = urllib.request.urlopen('https://ident.me').read().decode('utf8')
dataBase = urllib.request.urlopen('http://engr.uconn.edu/~song/classes/cn/db').read().decode('utf8')
dataBase = dataBase.split('\n')
ssn_dataBase = dataBase

# Initialize socket, head, local server port number, etc.
UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
head = 19684
lab_and_version_number = 1031
info_field = 0
host_port = 3200
UDPSock.bind(('', host_port))

# Check to see if the social security number is in fact
# within the database.
def get_ssn(value):

    result = 32772

    if value > 99999999:

        for line in ssn_dataBase:

            if line.find(str(value)) != -1:  # Find Post Office Box number

                result = int(line[len(line) - 4:])
                print('Requested Social Security Number was found in the database: %s' % result)
                break

    if result == 32772:

        print('Requested Social Security was not found in the database.')

    return result


# Compute the sum of two 16 bit integers
# that are received/sent to the server
def get_sum(unsigned16_1, unsigned16_2):

    result = unsigned16_1 + unsigned16_2

    if result > 0x0000ffff:

        result = (result & 0x0000ffff) + 1

    return result

# Calculate the checksum for the message being sent
# by looking at each line 1-4 each. Add each line up together,
# then add all up together to generate a checksum.
def get_checksum(unsigned16_1, unsigned16_2, unsigned32_1, unsigned32_2, unsigned16_3):

    temp_sum = get_sum(unsigned16_1, unsigned16_2)

    temp = unsigned32_1 >> 16
    temp_sum = get_sum(temp_sum, temp)
    temp = unsigned32_1 & 0x0000ffff
    temp_sum = get_sum(temp_sum, temp)

    temp = unsigned32_2 >> 16
    temp_sum = get_sum(temp_sum, temp)
    temp = unsigned32_2 & 0x0000ffff
    temp_sum = get_sum(temp_sum, temp)

    temp_sum = get_sum(temp_sum, unsigned16_3)

    result = ~temp_sum & 0x0000ffff
    return result


# Get the information received in the request message from the client,
# unpack and sort it, then craft another message that will be passed onto
# the server as a new message.
def generate_msg(unsigned16_1, unsigned16_2, unsigned32_1, unsigned32_2, unsigned16_3):

    temp = get_checksum(unsigned16_1, unsigned16_2, unsigned32_1, unsigned32_2, unsigned16_3)
    result = struct.pack('!2H2I2H', unsigned16_1, unsigned16_2, unsigned32_1, unsigned32_2, temp, unsigned16_3)

    return result

# Checksum > Syntax Error > Unknown SSN > Server Error
print('Server is now listening on port %s...' % host_port)

while 1:

    # Wait for incoming messages, and receive if one comes in
    data, client_address = UDPSock.recvfrom(20)
    unpacked_msg = struct.unpack('!2H2I2H', data)
    msg_type = 1

    #If the messages coming in was of type 0, this is S
    if unpacked_msg[0] == 3300:
        msg_type = 0

    print('Type[%s] messages received from %s\nContent: %s' % (msg_type, client_address, unpacked_msg))

    # Check checksum of message and make sure it matches
    checksum = get_checksum(unpacked_msg[0], unpacked_msg[1], unpacked_msg[2], unpacked_msg[3], unpacked_msg[5])
    if checksum != unpacked_msg[4]:
        print('Error, the checksum does not match. An error occurred.')
        data = generate_msg(head, lab_and_version_number, unpacked_msg[2], unpacked_msg[3], 32769)

    #Checksum is good
    else:

        print('Checksum match.')

        #Unpack the message contents and send off a message to the server regarding the message recevied
        request_ssn = get_ssn(unpacked_msg[3])
        if unpacked_msg[0] != 3300 or unpacked_msg[1] != 1031:
            data = generate_msg(head, lab_and_version_number, unpacked_msg[2], unpacked_msg[3], 32770)
        elif request_ssn > 0:
            data = generate_msg(head, lab_and_version_number, unpacked_msg[2], unpacked_msg[3], request_ssn)
        else:
            data = generate_msg(head, lab_and_version_number, unpacked_msg[2], unpacked_msg[3], 32776)

    #Send off message
    print('The following message will now be sent: ', struct.unpack('!2H2I2H', data))
    UDPSock.sendto(data, client_address)