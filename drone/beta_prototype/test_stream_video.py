import socket as sock
import logging
import threading as thread
import cv2 as opencv
import numpy as np
import struct
import math

# IP address and port number for the Jetson Nano
NANO_ADDR = ("172.16.0.2", 49152)

# IP address and port number for the Raspberry Pi
RPI_ADDR = ("172.16.0.1", 49152)

# Maximum allowed data tranfser size over Ethernet
MAX_DATA_SIZE = 2**16

FPS_PROP = 5
FRAME_COUNT_PROP = 7
POS_FRAMES_PROP = 1

def dump_buffer(frame):
    while True:
        seg, addr = frame.recvfrom(MAX_DATA_SIZE)
        if struct.unpack("B", seg[0:1])[0] == 1:
            print("finished emptying buffer")
            break

def compareVideos():

    original = opencv.VideoCapture("./test/test.mp4")
    fps = original.get(FPS_PROP)
    adjusted_fps = fps * 0.1
    numOriginalFrames = original.get(FRAME_COUNT_PROP)

    incoming = opencv.VideoCapture("./test/incoming.mp4")
    numIncomingFrames = incoming.get(FRAME_COUNT_PROP) # get total # of frames in incoming stream
    
    ratio = math.ceil(numOriginalFrames / numIncomingFrames)

    for i in range(int(numIncomingFrames)):
        original.set(POS_FRAMES_PROP, ratio*i)
        _, orig_frame = original.read()
        compressed = opencv.imencode(".jpg", orig_frame)[1]
        orig_frame = opencv.imdecode(np.fromstring(compressed, dtype=np.uint8), 1)

        _, incoming_frame = incoming.read()
        color_diff = opencv.subtract(orig_frame, incoming_frame)

        imageHeight = incoming_frame.shape[0]
        imageWidth = incoming_frame.shape[1]
        totalPixels = imageHeight * imageWidth

        # Split the color difference result into its different channels
        b, g, r = opencv.split(color_diff)

        if opencv.countNonZero(b) == 0 and opencv.countNonZero(g) == 0 and opencv.countNonZero(r) == 0:
            print("Identical images")
        else:
            print("!!!!!!!!!!! Diff images !!!!!!!!!!!!!")
            print("Diff b: {0}, Diff g: {1}, Diff r: {2}".format(opencv.countNonZero(b), opencv.countNonZero(g), opencv.countNonZero(r)))
            print("Same b: {0}, Same g: {1}, Same r: {2}".format(totalPixels-opencv.countNonZero(b), totalPixels-opencv.countNonZero(g), totalPixels-opencv.countNonZero(r)))
        
#    while True:
#        _, orig_frame = original.read()
#        compressed = opencv.imencode('.jpg', orig_frame)[1]
#        orig_frame = opencv.imdecode(np.fromstring(compressed, dtype=np.uint8), 1)
#        
#        status, incoming_frame = incoming.read()
#        
#        if not status: # video done being processed
#            print("Status return false")
#            break
#
#        opencv.imshow("Original", orig_frame)
#        opencv.imshow("Incoming", incoming_frame)
#
#        # Extract the color difference between the two images
#        color_diff = opencv.subtract(orig_frame, incoming_frame)
#        imageHeight = incoming_frame.shape[0]
#        imageWidth = incoming_frame.shape[1]
#        totalPixels = imageHeight * imageWidth
#        # Split the color difference result into its different channels
#        b, g, r = opencv.split(color_diff)
#
#        if opencv.countNonZero(b) == 0 and opencv.countNonZero(g) == 0 and opencv.countNonZero(r) == 0:
#            print("Identical images")
#        else:
#            print("!!!!!!!!!!! Diff images !!!!!!!!!!!!!")
#            print("Diff b: {0}, Diff g: {1}, Diff r: {2}".format(opencv.countNonZero(b), opencv.countNonZero(g), opencv.countNonZero(r)))
#            print("Same b: {0}, Same g: {1}, Same r: {2}".format(totalPixels-opencv.countNonZero(b), totalPixels-opencv.countNonZero(g), totalPixels-opencv.countNonZero(r)))

def receive_video():
    vidSock = sock.socket(family=sock.AF_INET, type=sock.SOCK_DGRAM, proto=0)

    # Bind the UDP video socket to the desired port and IP address
    try:
        vidSock.bind(NANO_ADDR)
#        logger.info("Bound receiver to video addr (IP: %s, Port: %d)\n", NANO_ADDR[0], NANO_ADDR[1])
        data, addr = vidSock.recvfrom(MAX_DATA_SIZE)
        vidSock.sendto(b'Hello Nano', RPI_ADDR)
        data = b'' # data buffer to read into
        dump_buffer(vidSock)

        codec = opencv.VideoWriter_fourcc(*'mp4v')

        out = opencv.VideoWriter("./test/incoming.mp4", codec, 20.0, (1280, 720))

        while True:
            packet, addr = vidSock.recvfrom(MAX_DATA_SIZE)

            # Check if the incoming packet is a signal from the RPi to stop listening for video feed
            if struct.unpack("!I", packet[0:4])[0] == 0xdeadbeef:
                print("Received all done from sender...")
                break

            # Check if we've reached the last sequence number for the packets making up the current frame
            if struct.unpack("B", packet[0:1])[0] > 1:
                data += packet[1:]
            else:
                data += packet[1:]
                frame = opencv.imdecode(np.fromstring(data, dtype=np.uint8), 1)
                # write the frame to the output file
                out.write(frame) 
                #opencv.imshow("Incoming", frame)
                if opencv.waitKey(1) & 0XFF == ord('q'):
                    break
                data = b'' # empty data buffer for next image frame
        
        # Release all resources allocated by openCV
        out.release()
        opencv.destroyAllWindows()
        vidSock.close()

    except sock.error as msg:
        print("bind() call raised exception: %s\n", msg.strerror)
        #logger.error("bind() call raised exception: %s\n", msg.strerror)


        
if __name__ == "__main__":

    # Configure logging info for this application (show all debug info by default)
    logging.basicConfig(format='%(asctime)s | %(levelname)s: %(message)s', level=logging.NOTSET)
    nano_logger = logging.getLogger("nano")

    # Begin running the application
    receive_video()
    print("Done receiving video")
    # Run comparison of the retrieved video to a known sample
    compareVideos()
