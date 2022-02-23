#!/usr/bin/env python3

import socket
import threading
import time
import sys
sys.path.insert(0, '/home/danton/data/proiect_colectiv/proiect/src') # used for importing the module
from export_module_functions import *

#==============================================================================#
###
# Predefined variables used in various places
###
HOST = '127.0.0.1' # listening address
PORT = 1337 # listening port
MAX_CONN = 15 # maximum simultaneous accepted connections 
CONN_NO = 0 
APP_ID = 3 # application id, as defined in the database
# result of the permissions defined in the database
CREATE = "You can create new data!"
READ = "You can read the data!"
UPDATE = "You can update data!"
DELETE = "You can delete data!"
# the data that is managed by the server
DATA = (" /^ ^\\ \n"
        "/ 0 0 \\ \n"
        "V\ Y /V \n"
        " / - \\ \n"
        " |    \\ \n"
        " || (__V\n")

#==============================================================================#
###
# Handle the interaction with the client
###
def handle_client(client_sock, addr):
    global CONN_NO

    try:
        # request the username/email from the user
        send_msg(client_sock, "Enter username/email:\n")
        print("Sent request for username/email.")
        user_login = recv_msg(client_sock)
        print('Received the username/email: {}'.format(user_login))

        # request the password from the user
        send_msg(client_sock, "Enter password:\n")
        print("Sent request for password.")
        pass_hash = recv_msg(client_sock)
        print('Received the password from the user. ')

        # check if the details are ok
        response = login_user(APP_ID, user_login, pass_hash)

        # if there was an error on the verify part, return the error message
        # to the client
        if response[0] == "ERROR":
            # send the ERROR string
            send_msg(client_sock, response[0])
            time.sleep(1)
            # and the error message
            send_msg(client_sock, response[1])
        elif response[0] == "OK":
            # send the OK string that lets the client know that everything is ok
            send_msg(client_sock, response[0])
            # count how many permission does the user have and create the list 
            # that contains all of them
            no_of_perms = 0
            client_response = []
            for i in range(1, len(response)):
                if response[i].startswith("CREATE"):
                    client_response.append(str(CREATE))
                    no_of_perms += 1
                if response[i].startswith("READ"):
                    client_response.append(str(READ))
                    client_response.append(str(DATA))
                    no_of_perms += 2
                if response[i].startswith("UPDATE"):
                    client_response.append(str(UPDATE))
                    no_of_perms += 1
                if response[i].startswith("DELETE"):
                    client_response.append(str(DELETE))
                    no_of_perms += 1
            # do a sleep to avoid sending multime messages at the same time
            time.sleep(1)
            # send the number of permissions that the client should expect
            send_msg(client_sock, str(no_of_perms))
            # do a sleep to avoid sending multime messages at the same time
            time.sleep(1)
            # send the list of permissions one by one 
            for i in range(0, no_of_perms):
                send_msg(client_sock, client_response[i])
                # do a sleep to avoid sending multime messages at the same time
                time.sleep(1)
        else:
            # something unexpected happened
            send_msg(client_sock, "ERROR")
            # do a sleep to avoid sending multime messages at the same time
            time.sleep(1)
            send_msg(client_sock, ("There was an unknown error! Please try"
                                   " again later.\n"))
        
        CONN_NO = CONN_NO - 1
    except (ConnectionError, BrokenPipeError):
        print('Closed connection to {}'.format(addr))

    # close the connection to the client
    print('Closing connection...')
    client_sock.close()

#==============================================================================#
###
# Receive and decode a message from the client
###
def recv_msg(sock):
    data = bytearray()
    msg = ''
    # while there is no message we do a receive
    while not msg:
        recvd = sock.recv(2000)
        if not recvd:
            # if there is no data then there might be a connection error
            raise ConnectionError()
        # store the message
        data = data + recvd
        # decode the message
        msg = data.decode('utf-8')
    return msg

#==============================================================================#
###
# Encode and send the message to the client
###
def send_msg(sock, msg):
    # encode the message
    tmp = msg.encode('utf-8')
    # send the message
    sock.sendall(tmp)

#==============================================================================#

if __name__ == '__main__':
    # create a listening TCP socket
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # set the options for the socket
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the socket to the chosen host and port 
    listener.bind((HOST, PORT))
    # start listening on the socket for connections with a limit of 15 simultaneous
    # clients
    listener.listen(15)
    # get the addres of the listening socket
    addr = listener.getsockname()
    print('Listening on {}'.format(addr))

    while True:
        # get the client socket object and its address
        client_sock, addr = listener.accept()
        # increment the number of connections open
        CONN_NO = CONN_NO + 1
        # if the number of connections has reached the maximum one, make the client wait
        while CONN_NO > MAX_CONN:
            print('Please wait')
            time.sleep(1)
        # if the number of connections hasn't reached the maximum one, start
        # the thread that deals with the client
        if CONN_NO <= MAX_CONN:
            print('Accept client {}'.format(addr))
            thread = threading.Thread(target = handle_client, args = [client_sock, addr], daemon = True)
            thread.start()

    listener.close()

#==============================================================================#