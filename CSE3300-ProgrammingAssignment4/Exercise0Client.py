import socket
import random
import struct
import urllib.request  # the lib that handles the url stuff

#############################
# Bryan Arnold              #
# CSE 3300                  #
# 12/9/18                   #
# Programming Assignment 4  #
#############################

# Get the IP address of the machine making
# the client request to the server.
host_ip_address = urllib.request.urlopen('https://ident.me').read().decode('utf8')

# Default IP address and port of the server
# to make requests to. Also initialize UDP socket.
host_IP = socket.gethostbyname("tao.ite.uconn.edu")
host_port = 3300
UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
timeout = 5.0

# Create the initial states for the packages to be
# sent over the socket to the server
head = 3300
lab_and_version_number = 1031
client_cookie = random.randint(5000, pow(2, 32))
ssn_request = 111111111
other = 0

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

# Ask for user input on which type of request they want to make.
# 0 = client to tao.ite.uconn.edu, 1 = server set up by me
while 1:

    request_type = input('Please choose a request type. 0 or 1: ')

    if request_type == '' or request_type == '0':
        break
    elif request_type == '1':
        head = 36068
        break

    # If the user wants to do type 0 request, ask for Social
    # Security number
if head != 36068:

    ssn = -1

    while 1:

        try:

            ssn = int(input('Please enter the Social Security Number you wish to find the PO Box for: '))

            if ssn == '':
                break
            elif 0 < int(ssn) < 1000000000:
                ssn_request = int(ssn)
                break

        except ValueError:
            pass

# If the user wishes to make a request to the server created
host_address = 0
if head == 36068:

    # Default initializers. Includes server port, address generation, and
    # ip of sender.
    other = 3200
    server_ip = host_ip_address
    server_ip = server_ip.split('.')
    part_a, part_b, part_c, part_d = server_ip

    # Try to set up server address to send to
    try:
        part_a = int(part_a) << 24
        part_b = int(part_b) << 16
        part_c = int(part_c) << 8
        part_d = int(part_d)
        host_address = part_a | part_b | part_c | part_d
    except ValueError:
        pass

if head == 36068:

    ssn_request = host_address

# Get checksum for checking
checksum = get_checksum(head, lab_and_version_number, client_cookie, ssn_request, other)

# Variables set up to display and read incoming and outgoing
# messages.
data = None
unpacked_msg = None
packed_msg = struct.pack('!2H2I2H', head, lab_and_version_number, client_cookie, ssn_request, checksum, other)

print("Attempting to send message to server", struct.unpack('!2H2I2H', packed_msg))

# A lot cap for retransmitting if timeout occurs
max_transmission = 5
retransmission_counter = 1
while max_transmission > 0:

    UDPSock.sendto(packed_msg, (host_IP, host_port))

    # Timeout checker
    try:
        UDPSock.settimeout(timeout)

        data, client_address = UDPSock.recvfrom(20)
        if data:
            print("Successfully received message from server:", struct.unpack('!2H2I2H', data))
            unpacked_msg = struct.unpack('!2H2I2H', data)
            if unpacked_msg[4] == get_checksum(unpacked_msg[0], unpacked_msg[1], unpacked_msg[2], unpacked_msg[3],
                                               unpacked_msg[5]):
                break
            else:
                continue

    # Attempt retransmit
    except socket.timeout:

        print('The request to the server timed out, attempting to retransmit') + str(retransmission_counter)
        retransmission_counter += 1
        pass

    max_transmission -= 1

# Error checking. If no errors are found, print out the PO box
# corresponding to the requested SSN
if unpacked_msg is not None:

    if unpacked_msg[5] & 0x8000 != 0:

        if unpacked_msg[5] == 32769:
            print('An error occurred while checking the checksum. Please try again.')

        elif unpacked_msg[5] == 32770:
            print('A syntax error occurred.')

        elif unpacked_msg[5] == 32776:
            print('An error occurred in the server. Please wait and try again.')

        else:
            print('Successfully got message from server.')

    elif unpacked_msg[0] == 19684:
        print('PO Box number: ' + str(unpacked_msg[5]))

else:
    print('No response from Server. Please wait and try again.')