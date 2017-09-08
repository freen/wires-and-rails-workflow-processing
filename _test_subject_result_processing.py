#!/usr/bin/env python3

"""
Useful for synchronously debugging queue operations.
"""

from numpy import array
from lib.image_operations import ImageOperations

def run():
    """Run test"""
    mock_centroids_by_subject = {
        '5823821': array([1668.72990723]),
        '5823822': array([579.69410197, 1121.70011393, 1637.67895508, 2169.64591471, 2706.0571696])
    }
    for subject_id, vertex_centroids in mock_centroids_by_subject.items():
        ImageOperations.queue_new_subject_creation(subject_id, vertex_centroids)

if __name__ == '__main__':
    run()
