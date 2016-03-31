#!/usr/bin/python
import os
import time
import zmq
import argparse

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-port', type=int, default=5556)
    parser.add_argument('-ip', type=str, default='127.0.0.1')
    parser.add_argument('-cmd', type=str, default='take_pic',choices=['take_pic', 'print_pic', 'load_preview_pic'])
    parser.add_argument('-args', type=str, nargs='*')
    args = parser.parse_args()
    context = zmq.Context()
    print "Connecting to server..."
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://%s:%i" % (args.ip,args.port))
    socket.send_json({'cmd':args.cmd,'args':args.args})
    print socket.recv()

if __name__ == '__main__':
    main()
