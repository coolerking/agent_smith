# -*- coding: utf-8 -*-

import os
import time
import glob
import datetime
import numpy as np
import pandas as pd
from PIL import Image
from donkeycar.parts.datastore import Tub as OldTub

CAMERA_DIR = 'camera'
FWD_CAMERA_KEY = 'fwd/image_array'

class Tub(OldTub):
    def __init__(self, path, inputs=None, types=None, user_meta=[], camera_dir=CAMERA_DIR):
        super().__init__(path, inputs, types, user_meta)
        self.camera_path = os.path.join(self.path, camera_dir)
        if not os.path.exists(self.camera_path):
            print('                    Creating new camera dir...')
            os.makedirs(self.camera_path)

    def put_record(self, data):
        """
        Save values like images that can't be saved in the csv log and
        return a record with references to the saved values that can
        be saved in a csv.
        """
        json_data = {}
        self.current_ix += 1
        
        for key, val in data.items():
            typ = self.get_input_type(key)

            if (val is not None) and (typ == 'float'):
                # in case val is a numpy.float32, which json doesn't like
                json_data[key] = float(val)

            elif typ in ['str', 'float', 'int', 'boolean', 'vector']:
                json_data[key] = val

            elif typ is 'image':
                path = self.make_file_name(key)
                val.save(path)
                json_data[key]=path

            elif typ == 'image_array':
                img = Image.fromarray(np.uint8(val))
                name = self.make_file_name(key, ext='.jpg')
                if key == FWD_CAMERA_KEY:
                    name = name.replace('fwd', 'cam')
                    img.save(os.path.join(self.camera_path, name))
                else:
                    img.save(os.path.join(self.path, name))
                json_data[key]=name

            else:
                msg = 'Tub does not know what to do with this type {}'.format(typ)
                raise TypeError(msg)

        json_data['milliseconds'] = int((time.time() - self.start_time) * 1000)

        self.write_json_record(json_data)
        return self.current_ix

    def erase_record(self, i):
        print('arrived erase_record i={}'.format(str(i)))
        super().erase_record(i)
        img_filename = '%d_cam-image_array_.jpg' % (i)
        camera_img_path = os.path.join(self.camera_path, img_filename)
        print(camera_img_path)
        if os.path.exists(camera_img_path):
            print('erase {}'.format(str(camera_img_path)))
            os.unlink(camera_img_path)
        else:
            print('not exists {}'.format(str(camera_img_path)))

    def get_record(self, ix):

        json_data = self.get_json_record(ix)
        data = self.read_record(json_data)
        return data


class TubWriter(Tub):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, *args):
        '''
        API function needed to use as a Donkey part.

        Accepts values, pairs them with their inputs keys and saves them
        to disk.
        '''
        assert len(self.inputs) == len(args)

        self.record_time = int(time.time() - self.start_time)
        record = dict(zip(self.inputs, args))
        self.put_record(record)
        return self.current_ix


class TubReader(Tub):
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, *args):
        '''
        API function needed to use as a Donkey part.

        Accepts keys to read from the tub and retrieves them sequentially.
        '''

        record = self.get_record(self.current_ix)
        record = [record[key] for key in args ]
        return record


class TubHandler():
    def __init__(self, path):
        self.path = os.path.expanduser(path)

    def get_tub_list(self,path):
        folders = next(os.walk(path))[1]
        return folders

    def next_tub_number(self, path):
        def get_tub_num(tub_name):
            try:
                num = int(tub_name.split('_')[1])
            except:
                num = 0
            return num

        folders = self.get_tub_list(path)
        numbers = [get_tub_num(x) for x in folders]
        #numbers = [i for i in numbers if i is not None]
        next_number = max(numbers+[0]) + 1
        return next_number

    def create_tub_path(self):
        tub_num = self.next_tub_number(self.path)
        date = datetime.datetime.now().strftime('%y-%m-%d')
        name = '_'.join(['tub',str(tub_num),date])
        tub_path = os.path.join(self.path, name)
        return tub_path

    def new_tub_writer(self, inputs, types, user_meta=[]):
        tub_path = self.create_tub_path()
        tw = TubWriter(path=tub_path, inputs=inputs, types=types, user_meta=user_meta)
        return tw



class TubImageStacker(Tub):
    '''
    A Tub for training a NN with images that are the last three records stacked 
    togther as 3 channels of a single image. The idea is to give a simple feedforward
    NN some chance of building a model based on motion.
    If you drive with the ImageFIFO part, then you don't need this.
    Just make sure your inference pass uses the ImageFIFO that the NN will now expect.
    '''
    
    def rgb2gray(self, rgb):
        '''
        take a numpy rgb image return a new single channel image converted to greyscale
        '''
        return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

    def stack3Images(self, img_a, img_b, img_c):
        '''
        convert 3 rgb images into grayscale and put them into the 3 channels of
        a single output image
        '''
        width, height, _ = img_a.shape

        gray_a = self.rgb2gray(img_a)
        gray_b = self.rgb2gray(img_b)
        gray_c = self.rgb2gray(img_c)
        
        img_arr = np.zeros([width, height, 3], dtype=np.dtype('B'))

        img_arr[...,0] = np.reshape(gray_a, (width, height))
        img_arr[...,1] = np.reshape(gray_b, (width, height))
        img_arr[...,2] = np.reshape(gray_c, (width, height))

        return img_arr

    def get_record(self, ix):
        '''
        get the current record and two previous.
        stack the 3 images into a single image.
        '''
        data = super(TubImageStacker, self).get_record(ix)

        if ix > 1:
            data_ch1 = super(TubImageStacker, self).get_record(ix - 1)
            data_ch0 = super(TubImageStacker, self).get_record(ix - 2)

            json_data = self.get_json_record(ix)
            for key, val in json_data.items():
                typ = self.get_input_type(key)

                #load objects that were saved as separate files
                if typ == 'image':
                    val = self.stack3Images(data_ch0[key], data_ch1[key], data[key])
                    data[key] = val
                elif typ == 'image_array':
                    img = self.stack3Images(data_ch0[key], data_ch1[key], data[key])
                    val = np.array(img)

        return data



class TubTimeStacker(TubImageStacker):
    '''
    A Tub for training N with records stacked through time. 
    The idea here is to force the network to learn to look ahead in time.
    Init with an array of time offsets from the current time.
    '''

    def __init__(self, frame_list, *args, **kwargs):
        '''
        frame_list of [0, 10] would stack the current and 10 frames from now records togther in a single record
        with just the current image returned.
        [5, 90, 200] would return 3 frames of records, ofset 5, 90, and 200 frames in the future.

        '''
        super(TubTimeStacker, self).__init__(*args, **kwargs)
        self.frame_list = frame_list
  
    def get_record(self, ix):
        '''
        stack the N records into a single record.
        Each key value has the record index with a suffix of _N where N is
        the frame offset into the data.
        '''
        data = {}
        for i, iOffset in enumerate(self.frame_list):
            iRec = ix + iOffset
            
            try:
                json_data = self.get_json_record(iRec)
            except FileNotFoundError:
                pass
            except:
                pass

            for key, val in json_data.items():
                typ = self.get_input_type(key)

                #load only the first image saved as separate files
                if typ == 'image' and i == 0:
                    val = Image.open(os.path.join(self.path, val))
                    data[key] = val                    
                elif typ == 'image_array' and i == 0 and key != FWD_CAMERA_KEY:
                    d = super(TubTimeStacker, self).get_record(ix)
                    data[key] = d[key]
                else:
                    '''
                    we append a _offset to the key
                    so user/angle out now be user/angle_0
                    '''
                    new_key = key + "_" + str(iOffset)
                    data[new_key] = val
        return data


class TubGroup(Tub):
    def __init__(self, tub_paths):
        tub_paths = self.resolve_tub_paths(tub_paths)
        print('TubGroup:tubpaths:', tub_paths)
        tubs = [Tub(path) for path in tub_paths]
        self.input_types = {}

        record_count = 0
        for t in tubs:
            t.update_df()
            record_count += len(t.df)
            self.input_types.update(dict(zip(t.inputs, t.types)))

        print('joining the tubs {} records together. This could take {} minutes.'.format(record_count,
                                                                                         int(record_count / 300000)))

        self.meta = {'inputs': list(self.input_types.keys()),
                     'types': list(self.input_types.values())}


        self.df = pd.concat([t.df for t in tubs], axis=0, join='inner')



    def find_tub_paths(self, path):
        matches = []
        path = os.path.expanduser(path)
        for file in glob.glob(path):
            if os.path.isdir(file):
                matches.append(os.path.join(os.path.abspath(file)))
        return matches


    def resolve_tub_paths(self, path_list):
        path_list = path_list.split(",")
        resolved_paths = []
        for path in path_list:
            paths = self.find_tub_paths(path)
            resolved_paths += paths
        return resolved_paths
