import os
class Config(object):
    req_rep_port = 5556
    pub_sub_port = 5557
    library_path = os.path.join(os.getcwd(),'library')
    show_pic_time = 10 #seconds for how log the taken pic will be shown before live stream starts again
    count_down_time = 5 #seconds till pic gest taken
