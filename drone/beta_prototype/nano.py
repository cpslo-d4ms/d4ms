import socket as sock
import logging as logger
import threading as thread
import cv2 as opencv
import numpy as np
import struct

MAX_DATA_SIZE = 2**16

# addresses of the Jetson Nano and Raspberry Pi
# in the form of (IP address, port number) pairs
NANO_MSG_ADDR = ("172.16.0.2", 49152)
NANO_VID_ADDR = ("172.16.0.2", 49153)
RPI_MSG_ADDR = ("172.16.0.1", 49152)

def dump_buffer(frame):
    while True:
        seg, addr = frame.recvfrom(MAX_DATA_SIZE)
        if struct.unpack("B", seg[0:1])[0] == 1:
            print("finished emptying buffer")
            break

def receive_video():
    vidSock = sock.socket(family=sock.AF_INET, type=sock.SOCK_DGRAM, proto=0)

    # Bind the UDP video socket to the desired port and IP address
    try:
        vidSock.bind(NANO_VID_ADDR)
        logger.info("Bound receiver to video addr (IP: %s, Port: %d)\n", NANO_VID_ADDR[0], NANO_VID_ADDR[1])
        data, addr = vidSock.recvfrom(MAX_DATA_SIZE)
        vidSock.sendto(b'Hello Nano', RPI_MSG_ADDR)
        data = b'' # data buffer to read into
        #dump_buffer(vidSock)

        # Define the video codec for MP4 files (codec = encoder and decoder for video compression)
        codec = opencv.VideoWriter_fourcc(*'mp4v')

        # Define handler for saving video to an output file
        #                           File name         codec   fps  frame size
        out = opencv.VideoWriter("camera_output.mp4", codec, 20.0, (640, 480))

        while True:
            packet, addr = vidSock.recvfrom(MAX_DATA_SIZE)
            if struct.unpack("!I", packet[0:4])[0] == 0xdeadbeef:
                print("Received all done from sender...")
                break
            if struct.unpack("B", packet[0:1])[0] > 1:
                data += packet[1:]
            else:
                data += packet[1:]
                frame = opencv.imdecode(np.fromstring(data, dtype=np.uint8), 1)

                # Write current frame to the output file
                out.write(frame)

                # Display the current frame to the screen
                opencv.imshow("Raspberry Pi Camera", frame)
                
                if opencv.waitKey(1) & 0XFF == ord('q'):
                    break
                data = b'' # empty data buffer for next image frame
        
        # Release all resources allocated by openCV
        out.release()
        opencv.destroyAllWindows()
        vidSock.close()

    except sock.error as msg:
        logger.error("bind() call raised exception: %s\n", msg.strerror)


        
if __name__ == "__main__":

    receive_video()
'''
    receiver = thread.Thread(target=receive_video)
    receiver.start()

    # Create a UDP socket object to handle the communication
    udpSocket = sock.socket(family=sock.AF_INET, # using IP address family
                            type=sock.SOCK_DGRAM, # using UDP protocol
                            proto=0 # unused parameter for UDP
                           )

    # Bind the UDP socket to the desired port and IP address
    try:
        # Bind the socket to the Pi's IP address and port number
        # Allows the Raspberry Pi's socket to receive data from the Jetson Nano
        udpSocket.bind(NANO_MSG_ADDR)
        logger.info("Bound to (IP: %s, Port: %d)\n", NANO_MSG_ADDR[0], NANO_MSG_ADDR[1])

        data, addr = udpSocket.recvfrom(MAX_DATA_SIZE)
        print("Received message from {}: {}\n".format(addr, data))
        
        # Message Loop
        while True:
            msg = input("> ")

            udpSocket.sendto(msg, RPI_MSG_ADDR)

            data, addr = udpSocket.recvfrom(MAX_DATA_SIZE)
            print("Raspberry PI: {}".format(data))

    except sock.error as msg:
        logger.error("bind() call raised exception: %s\n", msg.strerror)
'''
