import numpy as np

class Square():
    def convert_pos_to_int(self,row,column):
        return np.uint64(row*8 + column)

    def convert_int_to_pos(self, bb):
        """
        :param bb:
        :return:
        """
        pass