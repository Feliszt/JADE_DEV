#
#   installation_play_video_queue.py
#
#   This script listens to the OSC adress on which the objects put on and
#   removed from the scale are written.
#   It then plays a dynamic playlist of videos that depends on those objects,
#   the link between each video and the video to play is written in "calib.json".
#   This file is created by running calibration.py
#

# GUI
from tkinter import *
# OSC server
from pythonosc import dispatcher
from pythonosc import osc_server
import threading
# misc
import os
import json
import time
import subprocess

# video player class
class VideoPlayer :
    # init
    def __init__(self, _window) :
        # window
        self.window = _window
        self.window.title("Jade-playVideo")
        self.window.overrideredirect(True)
        self.appW = 10
        self.appH = 10
        self.offX = 0
        self.offY = 0
        self.window.geometry("{}x{}+{}+{}".format(self.appW, self.appH, self.offX, self.offY))

        # canvas
        self.canvas = Canvas(self.window, width=self.appW, height=self.appH, bd=0, highlightthickness=0, relief='ridge', bg='black')
        self.canvas.pack(side = LEFT)

        # init folders name for data
        self.config_folder = "../DATA/config/"

        # load calibration
        with open(self.config_folder + 'calib.json', 'r') as f_calib:
            self.calib = json.load(f_calib)
            
        # load config
        with open(self.config_folder + 'config.json', 'r') as f_config:
            self.config = json.load(f_config)

        # set up object list
        self.objects_on_scale = []
        self.n_objects_prev = 0

        # get base video object
        self.base_video = self.calib["base_video"]

        # setup osc dispatcher
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/add", self.add_object)
        self.dispatcher.map("/remove", self.remove_object)

        # launch osc server
        self.server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 8000), self.dispatcher)
        self.server_thread = threading.Thread(target = self.server.serve_forever)
        self.server_thread.daemon=True
        self.server_thread.start()

        # video variables
        self.curr_video = self.base_video
        self.next_video = self.base_video
        self.video_proc = []

        # launch app
        self.n_iter = 0
        self.delay = 0
        self.update()
        self.window.mainloop()

    # loop function
    def update(self) :
        # update current video
        self.curr_video = self.next_video
        #self.delay = int(self.curr_video["video_duration"] * 1000)
        
        # get next video
        # at this point multiple things are possible
        # 1) we are playing base video, in that case curr_video will not be in the list of
        # objects on the scale
        # 1-a) there are no objects on the scale : next_video is base_video
        # 1-b) there are objects on the scale : next_video is first object on objects list
        # 2) we are playing a video from the list
        # 2-a) we are playing the last video of the list : next_video is base_video
        # 2-b) we are not playing the last video of the list : next_video is the one that arrives after
        if self.curr_video == self.base_video :
            if len(self.objects_on_scale) == 0 :
                self.next_video = self.base_video
            else :
                self.next_video = self.objects_on_scale[0]
        else :
            if self.curr_video == self.objects_on_scale[-1] :
                self.next_video = self.base_video
            else :
                curr_video_index = self.objects_on_scale.index(self.curr_video)
                next_video_index = curr_video_index + 1
                self.next_video = self.objects_on_scale[next_video_index]

        # actually plays the video
        video_folder = "../DATA/videos/" + self.config["video_folder"] + "/"
        video_file = video_folder + self.curr_video["video_name"] + ".mp4"
        #print("{}video_file = [{}]".format(base_debug, video_file))
        subprocess.call(["omxplayer", video_file])

        # debug
        print("{}(update)\t[{}]\t=>\t[{}]".format(base_debug, self.curr_video["video_name"], self.next_video["video_name"]))

        # update loop
        self.n_iter += 1
        self.n_objects_prev = len(self.objects_on_scale)
        self.window.after(self.delay, self.update)

    # called when an obbject is added on scale
    def add_object(self, unused_addr, args):
        # get object we added
        added_object = next(item for item in self.calib["objects"] if item["name"] == args)

        # when an object is added
        # 1) there are no objects on the scale : next_video is added_object
        # 2) there are objects on the scale
        # 2-a) if we are playing the last video of the list then next_video is add_dobject
        if len(self.objects_on_scale) == 0 :
            self.next_video = added_object
        else :
            if self.curr_video == self.objects_on_scale[-1] :
                self.next_video = added_object

        # add it to list and get next video
        self.objects_on_scale.append(added_object)

        # debug
        #print("{}Adding [{}]".format(base_debug, added_object["name"]))
        #print("{}{}".format(base_debug, [item["name"] for item in self.objects_on_scale]))

        # debug
        objects_on_board_names = [el["name"] for el in self.objects_on_scale]
        #print("{}(add_object)\t[{}]\t=>\t[{}]\t{}".format(base_debug, self.curr_video["video_name"], self.next_video["video_name"], objects_on_board_names))
        #print("{}(add_object)\t{}".format(base_debug, objects_on_board_names))

    # called when an object is removed from scale
    def remove_object(self, unused_addr, args):
        # get object we removed
        removed_object = next(item for item in self.calib["objects"] if item["name"] == args)

        # remove it from list if present
        # this is a sanity check because it should be present
        if removed_object in self.objects_on_scale :
            # when an object is removed there is one case in which it changes the next video
            # 1) if we just removed the object which video was supposed to be played next
            # in that case we get the video that comes after
            if self.next_video == removed_object :
                # get index of remove_object and set next video
                # if the removed object is the last object in the list,
                # next video will be base_video
                removed_object_index = self.objects_on_scale.index(removed_object)
                next_video_index = removed_object_index + 1
                if next_video_index == len(self.objects_on_scale) :
                    self.next_video = self.base_video
                else :
                    self.next_video = self.objects_on_scale[next_video_index]

            # get index of object and remove it
            self.objects_on_scale.remove(removed_object)

            # debug
            #print("{}Removing [{}]".format(base_debug, removed_object["name"]))
            #print("{}{}".format(base_debug, [item["name"] for item in self.objects_on_scale]))

            # debug
            objects_on_board_names = [el["name"] for el in self.objects_on_scale]
            #print("{}(remove_object)\t[{}]\t=>\t[{}]\t{}".format(base_debug, self.curr_video["video_name"], self.next_video["video_name"], objects_on_board_names))
            #print("{}(remove_object)\t{}".format(base_debug, objects_on_board_names))


# main function
if __name__ == "__main__" :
    # get script name
    program_name = os.path.basename(__file__)

    # debug
    base_debug = "[{}]\t".format(program_name)
    print("{}start.".format(base_debug))

    #
    vP = VideoPlayer(Tk())
