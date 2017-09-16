#!/usr/bin/env python3

"""
Useful for synchronously debugging queue operations.
"""

from numpy import array

import sys
sys.path.insert(0, "..")

from lib.queue_operations import QueueOperations
from lib.logger import setup_logger

# def run_segmentation_test():
#     """Run segmentation test on pre-existing local file"""
#     subject_id = '5823822'
#     subject_image_path = '/tmp/5823822.png'
#     vertex_centroids = array(
#         [579.69410197, 1121.70011393, 1637.67895508, 2169.64591471, 2706.0571696]
#     )
#     logger = setup_logger('TestLogger', 'log/test_segmentation.log')
#     queue_ops = QueueOperations(logger)
#     column_image_paths = queue_ops.perform_column_segmentation(
#         subject_id,
#         subject_image_path,
#         vertex_centroids
#     )
#     for column_image_path in column_image_paths:
#         queue_ops.upscale_small_images(column_image_path)
#     queue_ops.perform_row_segmentation(column_image_paths)

def run_full_image_slicing_test():
    """Run image slicing test"""
    mock_centroids_by_subject = {
        # '5823821': array([1668.72990723]),
        '5823822': array([579.69410197, 1121.70011393, 1637.67895508, 2169.64591471, 2706.0571696])
    }
    for subject_id, vertex_centroids in mock_centroids_by_subject.items():
        QueueOperations.queue_new_subject_creation(subject_id, vertex_centroids)

def run_subject_push_test():
    """Run subject push test"""
    logger = setup_logger('TestLogger', 'log/test_queue_operations.log')
    row_paths_by_column = {
        0: [
            '/tmp/5823821_0/010001.bin.png',
            '/tmp/5823821_0/01000b.bin.png',
            '/tmp/5823821_0/010015.bin.png',
            '/tmp/5823821_0/01001f.bin.png',
            '/tmp/5823821_0/010029.bin.png',
            '/tmp/5823821_0/010033.bin.png',
            '/tmp/5823821_0/01003d.bin.png',
            '/tmp/5823821_0/010047.bin.png',
            '/tmp/5823821_0/010051.bin.png',
            '/tmp/5823821_0/01005b.bin.png',
            '/tmp/5823821_0/010065.bin.png',
            '/tmp/5823821_0/010002.bin.png',
            '/tmp/5823821_0/01000c.bin.png',
            '/tmp/5823821_0/010016.bin.png',
            '/tmp/5823821_0/010020.bin.png',
            '/tmp/5823821_0/01002a.bin.png',
            '/tmp/5823821_0/010034.bin.png',
            '/tmp/5823821_0/01003e.bin.png',
            '/tmp/5823821_0/010048.bin.png',
            '/tmp/5823821_0/010052.bin.png',
            '/tmp/5823821_0/01005c.bin.png',
            '/tmp/5823821_0/010066.bin.png',
            '/tmp/5823821_0/010003.bin.png',
            '/tmp/5823821_0/01000d.bin.png',
            '/tmp/5823821_0/010017.bin.png',
            '/tmp/5823821_0/010021.bin.png',
            '/tmp/5823821_0/01002b.bin.png',
            '/tmp/5823821_0/010035.bin.png',
            '/tmp/5823821_0/01003f.bin.png',
            '/tmp/5823821_0/010049.bin.png',
            '/tmp/5823821_0/010053.bin.png',
            '/tmp/5823821_0/01005d.bin.png',
            '/tmp/5823821_0/010067.bin.png',
            '/tmp/5823821_0/010004.bin.png',
            '/tmp/5823821_0/01000e.bin.png',
            '/tmp/5823821_0/010018.bin.png',
            '/tmp/5823821_0/010022.bin.png',
            '/tmp/5823821_0/01002c.bin.png',
            '/tmp/5823821_0/010036.bin.png',
            '/tmp/5823821_0/010040.bin.png',
            '/tmp/5823821_0/01004a.bin.png',
            '/tmp/5823821_0/010054.bin.png',
            '/tmp/5823821_0/01005e.bin.png',
            '/tmp/5823821_0/010068.bin.png',
            '/tmp/5823821_0/010005.bin.png',
            '/tmp/5823821_0/01000f.bin.png',
            '/tmp/5823821_0/010019.bin.png',
            '/tmp/5823821_0/010023.bin.png',
            '/tmp/5823821_0/01002d.bin.png',
            '/tmp/5823821_0/010037.bin.png',
            '/tmp/5823821_0/010041.bin.png',
            '/tmp/5823821_0/01004b.bin.png',
            '/tmp/5823821_0/010055.bin.png',
            '/tmp/5823821_0/01005f.bin.png',
            '/tmp/5823821_0/010069.bin.png',
            '/tmp/5823821_0/010006.bin.png',
            '/tmp/5823821_0/010010.bin.png',
            '/tmp/5823821_0/01001a.bin.png',
            '/tmp/5823821_0/010024.bin.png',
            '/tmp/5823821_0/01002e.bin.png',
            '/tmp/5823821_0/010038.bin.png',
            '/tmp/5823821_0/010042.bin.png',
            '/tmp/5823821_0/01004c.bin.png',
            '/tmp/5823821_0/010056.bin.png',
            '/tmp/5823821_0/010060.bin.png',
            '/tmp/5823821_0/010007.bin.png',
            '/tmp/5823821_0/010011.bin.png',
            '/tmp/5823821_0/01001b.bin.png',
            '/tmp/5823821_0/010025.bin.png',
            '/tmp/5823821_0/01002f.bin.png',
            '/tmp/5823821_0/010039.bin.png',
            '/tmp/5823821_0/010043.bin.png',
            '/tmp/5823821_0/01004d.bin.png',
            '/tmp/5823821_0/010057.bin.png',
            '/tmp/5823821_0/010061.bin.png',
            '/tmp/5823821_0/010008.bin.png',
            '/tmp/5823821_0/010012.bin.png',
            '/tmp/5823821_0/01001c.bin.png',
            '/tmp/5823821_0/010026.bin.png',
            '/tmp/5823821_0/010030.bin.png',
            '/tmp/5823821_0/01003a.bin.png',
            '/tmp/5823821_0/010044.bin.png',
            '/tmp/5823821_0/01004e.bin.png',
            '/tmp/5823821_0/010058.bin.png',
            '/tmp/5823821_0/010062.bin.png',
            '/tmp/5823821_0/010009.bin.png',
            '/tmp/5823821_0/010013.bin.png',
            '/tmp/5823821_0/01001d.bin.png',
            '/tmp/5823821_0/010027.bin.png',
            '/tmp/5823821_0/010031.bin.png',
            '/tmp/5823821_0/01003b.bin.png',
            '/tmp/5823821_0/010045.bin.png',
            '/tmp/5823821_0/01004f.bin.png',
            '/tmp/5823821_0/010059.bin.png',
            '/tmp/5823821_0/010063.bin.png',
            '/tmp/5823821_0/01000a.bin.png',
            '/tmp/5823821_0/010014.bin.png',
            '/tmp/5823821_0/01001e.bin.png',
            '/tmp/5823821_0/010028.bin.png',
            '/tmp/5823821_0/010032.bin.png',
            '/tmp/5823821_0/01003c.bin.png',
            '/tmp/5823821_0/010046.bin.png',
            '/tmp/5823821_0/010050.bin.png',
            '/tmp/5823821_0/01005a.bin.png',
            '/tmp/5823821_0/010064.bin.png'
        ],
        1: [
            '/tmp/5823821_1/010001.bin.png',
            '/tmp/5823821_1/01000b.bin.png',
            '/tmp/5823821_1/010015.bin.png',
            '/tmp/5823821_1/01001f.bin.png',
            '/tmp/5823821_1/010029.bin.png',
            '/tmp/5823821_1/010033.bin.png',
            '/tmp/5823821_1/01003d.bin.png',
            '/tmp/5823821_1/010047.bin.png',
            '/tmp/5823821_1/010051.bin.png',
            '/tmp/5823821_1/01005b.bin.png',
            '/tmp/5823821_1/010065.bin.png',
            '/tmp/5823821_1/010002.bin.png',
            '/tmp/5823821_1/01000c.bin.png',
            '/tmp/5823821_1/010016.bin.png',
            '/tmp/5823821_1/010020.bin.png',
            '/tmp/5823821_1/01002a.bin.png',
            '/tmp/5823821_1/010034.bin.png',
            '/tmp/5823821_1/01003e.bin.png',
            '/tmp/5823821_1/010048.bin.png',
            '/tmp/5823821_1/010052.bin.png',
            '/tmp/5823821_1/01005c.bin.png',
            '/tmp/5823821_1/010066.bin.png',
            '/tmp/5823821_1/010003.bin.png',
            '/tmp/5823821_1/01000d.bin.png',
            '/tmp/5823821_1/010017.bin.png',
            '/tmp/5823821_1/010021.bin.png',
            '/tmp/5823821_1/01002b.bin.png',
            '/tmp/5823821_1/010035.bin.png',
            '/tmp/5823821_1/01003f.bin.png',
            '/tmp/5823821_1/010049.bin.png',
            '/tmp/5823821_1/010053.bin.png',
            '/tmp/5823821_1/01005d.bin.png',
            '/tmp/5823821_1/010067.bin.png',
            '/tmp/5823821_1/010004.bin.png',
            '/tmp/5823821_1/01000e.bin.png',
            '/tmp/5823821_1/010018.bin.png',
            '/tmp/5823821_1/010022.bin.png',
            '/tmp/5823821_1/01002c.bin.png',
            '/tmp/5823821_1/010036.bin.png',
            '/tmp/5823821_1/010040.bin.png',
            '/tmp/5823821_1/01004a.bin.png',
            '/tmp/5823821_1/010054.bin.png',
            '/tmp/5823821_1/01005e.bin.png',
            '/tmp/5823821_1/010068.bin.png',
            '/tmp/5823821_1/010005.bin.png',
            '/tmp/5823821_1/01000f.bin.png',
            '/tmp/5823821_1/010019.bin.png',
            '/tmp/5823821_1/010023.bin.png',
            '/tmp/5823821_1/01002d.bin.png',
            '/tmp/5823821_1/010037.bin.png',
            '/tmp/5823821_1/010041.bin.png',
            '/tmp/5823821_1/01004b.bin.png',
            '/tmp/5823821_1/010055.bin.png',
            '/tmp/5823821_1/01005f.bin.png',
            '/tmp/5823821_1/010069.bin.png',
            '/tmp/5823821_1/010006.bin.png',
            '/tmp/5823821_1/010010.bin.png',
            '/tmp/5823821_1/01001a.bin.png',
            '/tmp/5823821_1/010024.bin.png',
            '/tmp/5823821_1/01002e.bin.png',
            '/tmp/5823821_1/010038.bin.png',
            '/tmp/5823821_1/010042.bin.png',
            '/tmp/5823821_1/01004c.bin.png',
            '/tmp/5823821_1/010056.bin.png',
            '/tmp/5823821_1/010060.bin.png',
            '/tmp/5823821_1/010007.bin.png',
            '/tmp/5823821_1/010011.bin.png',
            '/tmp/5823821_1/01001b.bin.png',
            '/tmp/5823821_1/010025.bin.png',
            '/tmp/5823821_1/01002f.bin.png',
            '/tmp/5823821_1/010039.bin.png',
            '/tmp/5823821_1/010043.bin.png',
            '/tmp/5823821_1/01004d.bin.png',
            '/tmp/5823821_1/010057.bin.png',
            '/tmp/5823821_1/010061.bin.png',
            '/tmp/5823821_1/010008.bin.png',
            '/tmp/5823821_1/010012.bin.png',
            '/tmp/5823821_1/01001c.bin.png',
            '/tmp/5823821_1/010026.bin.png',
            '/tmp/5823821_1/010030.bin.png',
            '/tmp/5823821_1/01003a.bin.png',
            '/tmp/5823821_1/010044.bin.png',
            '/tmp/5823821_1/01004e.bin.png',
            '/tmp/5823821_1/010058.bin.png',
            '/tmp/5823821_1/010062.bin.png',
            '/tmp/5823821_1/010009.bin.png',
            '/tmp/5823821_1/010013.bin.png',
            '/tmp/5823821_1/01001d.bin.png',
            '/tmp/5823821_1/010027.bin.png',
            '/tmp/5823821_1/010031.bin.png',
            '/tmp/5823821_1/01003b.bin.png',
            '/tmp/5823821_1/010045.bin.png',
            '/tmp/5823821_1/01004f.bin.png',
            '/tmp/5823821_1/010059.bin.png',
            '/tmp/5823821_1/010063.bin.png',
            '/tmp/5823821_1/01000a.bin.png',
            '/tmp/5823821_1/010014.bin.png',
            '/tmp/5823821_1/01001e.bin.png',
            '/tmp/5823821_1/010028.bin.png',
            '/tmp/5823821_1/010032.bin.png',
            '/tmp/5823821_1/01003c.bin.png',
            '/tmp/5823821_1/010046.bin.png',
            '/tmp/5823821_1/010050.bin.png',
            '/tmp/5823821_1/01005a.bin.png',
            '/tmp/5823821_1/010064.bin.png'
        ]
    }
    subject_id = 5823821
    queue_ops = QueueOperations(logger)
    queue_ops.push_new_row_subjects(subject_id, row_paths_by_column)

if __name__ == '__main__':
    pass
    # run_segmentation_test()
    # run_full_image_slicing_test()
    # run_subject_push_test()
