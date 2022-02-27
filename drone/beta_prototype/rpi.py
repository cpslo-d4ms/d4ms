import socket as sock
import logging as logger
import threading as thread
import cv2 as opencv
import math
import struct
import signal
import time
#import subprocess
from server import run_server

MAX_DATA_SIZE = 2**16 # maximum payload size for UDP packet is 2^16 = 65536 bytes

# IP address and port number for the Jetson Nano
NANO_ADDR = ("172.16.0.2", 49152)

# IP address and port number for the Raspberry Pi
RPI_ADDR = ("172.16.0.1", 49152)

# Global boolean to tell the code when to stop streaming video and clean up
stop_stream = False


'''
    Signal handler that handles SIGINT being sent by the user to stop the RPI
    application. The handler changes the Boolean value of stop_stream to True
    so that the main loop in stream_video gets broken out of and the program
    can exit.
'''
def signal_handler(signum, frame):
    global stop_stream 

    stop_stream = True # indicate to the program to exit the streaming loop
    print("\nVideo stopped at user request...")


'''
    Given a video frame, partitions the frame into a series of UDP packets
    to be sent over the Ethernet connection. A sequence number is assigned 
    to each packet of a given video frame to indicate to the receiver when
    the last packet of a given video frame has been sent.
'''
def generate_udp_frames(data):
    payloadSize = len(data)
    num_packets = math.ceil(payloadSize / (MAX_DATA_SIZE - 64))
    packets = []
    start = 0

    # Generate packets from the string of video bytes
    while num_packets > 0:
        end = min(payloadSize, start + (MAX_DATA_SIZE-64))
        # Add a sequence number to each packet that indicates to the receiver
        # if more packets are incoming for the same video frame
        packet = struct.pack("B", num_packets) + data[start:end]
        packets.append(packet)
        start = end
        num_packets-=1

    return packets


'''
    Video streaming thread of execution. Takes in video feed from the Raspberry
    Pi's camera, splits it up into UDP frames, and sends those UDP frames over
    Ethernet to the Jetson Nano for further processing.
'''
def stream_video():
    # Set up the socket on which to communicate with the Jetson Nano
    vidSock = sock.socket(family=sock.AF_INET,
                          type=sock.SOCK_DGRAM,
                          proto=0)
    vidSock.bind(RPI_MSG_ADDR)

    # Send an initial handshake packet to the Jetson Nano to establish connection
    hello_msg = bytearray("Hello", encoding="utf-8")
    vidSock.sendto(hello_msg, NANO_VID_ADDR)
    data, addr = vidSock.recvfrom(MAX_DATA_SIZE) # block here until acknowledgment received from Jetson Nano
    
    # Open video file with data to send
    vid = opencv.VideoCapture(0) # capture frames from the Raspberry Pi camera
    while not stop_stream:
       status, frame = vid.read() # read a frame from the video file
       if not status:
           print("Video finished, exiting...")
           break

       # Compress the video to reduce the bandwidth consumed by each transmitted video frame
       compressed = opencv.imencode('.jpg', frame)[1]

       # Split the compressed video frame into a series of UDP packets to be transmitted
       udpFrames = generate_udp_frames(compressed.tostring())
       for i in range(0, len(udpFrames)): # send each frame serially to the Nano
            vidSock.sendto(udpFrames[i], NANO_VID_ADDR)

    # Give receiver time to process its last frame(s) and send an all-done message   
    time.sleep(1)
    vidSock.sendto(struct.pack("!I", 0xdeadbeef), NANO_VID_ADDR) 

    # Release all resources allocated to openCV and the socket
    vid.release()
    opencv.destroyAllWindows()
    vidSock.close()


if __name__ == "__main__":

    # Register the SIGINT handler
    signal.signal(signal.SIGINT, signal_handler)

    # Create separate thread for sending video to the Jetson Nano
    sender = thread.Thread(target=stream_video)
    server = thread.Thread(target=run_server, daemon=True)

    # Start the video streaming thread and wait in this thread until it completes
    sender.start()
    server.start()
    
    sender.join()
