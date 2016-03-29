import os
class Config(object):
    req_rep_port = 5556
    pub_sub_port = 5557
    library_path = os.path.join(os.getcwd(),'library')
    show_pic_time = 10 #seconds for how log the taken pic will be shown before live stream starts again
    count_down_time = 5 #seconds till pic gest taken
    camera_cfg = 'camera.cfg'
    preview_ui_pos_size = (.05,.1,.9,.8) #percent of with and height
    button_hide_time = 30#seconds
    slide_show_time = 2
