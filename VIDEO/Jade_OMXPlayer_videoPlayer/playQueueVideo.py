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

# video player class
class VideoPlayer :
    # init
    def __init__(self, _window) :
        # window
        self.window = _window
        self.window.title("Jade-playVideo")
        self.window.overrideredirect(True)
        self.appW = 100
        self.appH = 100
        self.offX = 10
        self.offY = 10
        self.window.geometry("{}x{}+{}+{}".format(self.appW, self.appH, self.offX, self.offY))
        
        # canvas
        self.canvas = Canvas(self.window, width=self.appW, height=self.appH, bd=0, highlightthickness=0, relief='ridge', bg='black')
        self.canvas.pack(side = LEFT)
        
        # init folders name for data
        self.config_folder = "../../DATA/config/"

        # load calibration
        with open(self.config_folder + 'calib.json', 'r') as f_calib:
            self.calib = json.load(f_calib)
        
        # set up object list
        self.objects_on_scale = []
        self.n_objects_prev = 0

        # setup osc dispatcher
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/add", self.add_object)
        self.dispatcher.map("/remove", self.remove_object)

        # launch osc server
        self.server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 8000), self.dispatcher)
        self.server_thread = threading.Thread(target = self.server.serve_forever)
        self.server_thread.start()
        
        # video variables
        self.curr_video = None
        self.next_video = None
        
        # launch app
        self.delay = 5
        self.update()
        self.window.mainloop()
        
    # loop function
    def update(self) :        
        # a video ended
        if self.next_video != None :
            # play video
            self.curr_video = self.next_video
            #self.next_video = self.get_next_video()
            
            self.delay = int(self.curr_video["video_duration"] * 1000)
            
            # debug
            print("{}Launch video [{}]\twait {} sec".format(base_debug, self.curr_video["video_name"], self.curr_video["video_duration"]))

        # this means there's no objects on the board
        else :
            self.delay = 5
            
            self.curr_video = None
            
            # debug
            objects_on_scale_names = [el["name"] for el in self.objects_on_scale]
            print(objects_on_scale_names)

            
        # update loop
        self.n_objects_prev = len(self.objects_on_scale) 
        self.window.after(self.delay, self.update)

    # called when an obbject is added on scale
    def add_object(self, unused_addr, args):
        # get object we added
        added_object = next(item for item in self.calib["objects"] if item["name"] == args)
        
        # add it to list and get next video
        self.objects_on_scale.append(added_object)
        self.next_video = self.get_next_video()

       
        # debug
        #print("{}Adding [{}]".format(base_debug, added_object["name"]))
        
    # called when an object is removed from scale
    def remove_object(self, unused_addr, args):
        # get object we removed
        removed_object = next(item for item in self.calib["objects"] if item["name"] == args)
        
        # remove it from list if present
        # this is a sanity check because it should be present
        if removed_object in self.objects_on_scale :            
            # get next video and remove it from list
            self.next_video = self.get_next_video()
            self.objects_on_scale.remove(removed_object)

            
            # debug            
            #print("{}Removing [{}]".format(base_debug, removed_object["name"]))
    
    # function that decides which video is next
    # knows where we're at
    # knows current state of scale
    def get_next_video(self) :
        # no video currently playing
        if self.curr_video == None :
            return self.objects_on_scale[0]
        
        # a video is currently playing
        else:
            #
            if len(self.objects_on_scale) == 0 :
                return None
            
            else :
                print(self.objects_on_scale)
                c = """
                # find curr_video in list
                curr_video_index = self.objects_on_scale.index(self.curr_video)
                
                # get index of next video
                next_video_index = curr_video_index + 1
                if next_video_index >= len(self.objects_on_scale) :
                    next_video_index = 0
                return self.objects_on_scale[next_video_index]
                """
            
            
# main function
if __name__ == "__main__" :
    # get script name
    program_name = os.path.basename(__file__)

    # debug
    base_debug = "[{}]\t".format(program_name)
    print("{}start.".format(base_debug))
    
    #
    vP = VideoPlayer(Tk())
    
    
    
    
    
