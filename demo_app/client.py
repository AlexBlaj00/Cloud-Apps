#!/usr/bin/env python3

import socket
import sys
import getpass

#==============================================================================#
###
# Predefined variables used in various places
###
HOST = '127.0.0.1' # address of the server
PORT = 1337 # port of the server

#==============================================================================#
###
# Receive and decode a message from the client
###
def recv_msg(sock):
    data = bytearray()
    msg = ''
    # while there is no message we do a receive
    while not msg:
        recvd = sock.recv(300)
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
    msg = msg.encode('utf-8')
    # send the message
    sock.send(msg)

#==============================================================================#

if __name__ == '__main__':
    try:
        # create the socket for the client
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect to the servers' address
        sock.connect((HOST, PORT))
    except ConnectionError:
        print('Socket error on connection')
        sys.exit(1)
    print('Connected to {}:{}'.format(HOST, PORT))

    try:
        # receive the request for username/email
        msg = recv_msg(sock)
        # let the user input it
        user_login = input(msg)
        # send it to the server
        send_msg(sock, user_login)

        # receive the request for the password
        msg = recv_msg(sock)
        # let the user input it in a way that is not visible
        password = getpass.getpass(msg)
        # send the password
        send_msg(sock, password)

        # receive a response from the server
        response = recv_msg(sock)
        if response == "ERROR":
            # if the first message is an error, then do another receive to get the 
            # error message and print it 
            err_msg = recv_msg(sock)
            print(err_msg)
        elif response == 'OK':
            # it means that everything went good and we should receive
            # the number of permissions for the user
            limit = recv_msg(sock)
            # do a receive for all the permissions and print them            
            for i in range(0, int(limit)):
                perm = recv_msg(sock)
                print(perm)
        else:
            # something unexpected happened
            print("There was an unknown error! Please try again later.")

    except ConnectionError:
        print('Socket error during communication')
        print('Closed connection to server\n')
        sys.exit(1)

    # close the connection to the server
    print("Closing connection")
    sock.close()

#==============================================================================#