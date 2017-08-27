# -*- coding: utf-8 -*-

"""
This module is concerned with the analysis of each variable found by the
debugger, as well as identifying and describing the buffers that should be
plotted in the ImageWatch window.
"""

import re

from giwscripts import symbols


# OpenCV constants
CV_CN_MAX = 512
CV_CN_SHIFT = 3
CV_MAT_CN_MASK = ((CV_CN_MAX - 1) << CV_CN_SHIFT)
CV_DEPTH_MAX = (1 << CV_CN_SHIFT)
CV_MAT_TYPE_MASK = (CV_DEPTH_MAX * CV_CN_MAX - 1)

def get_buffer_info(picked_obj, debugger_bridge):
    """
    Default values created for OpenCV Mat structures. Change it according to
    your needs.
    """
    buffer = debugger_bridge.get_casted_pointer('char', picked_obj['data'])
    if buffer == 0x0:
        raise Exception('Received null buffer!')

    width = int(picked_obj['cols'])
    height = int(picked_obj['rows'])
    flags = int(picked_obj['flags'])

    channels = ((((flags) & CV_MAT_CN_MASK) >> CV_CN_SHIFT) + 1)
    step = int(int(picked_obj['step']['buf'][0])/channels)

    if channels >= 3:
        pixel_layout = 'bgra'
    else:
        pixel_layout = 'rgba'

    cvtype = ((flags) & CV_MAT_TYPE_MASK)

    typevalue = (cvtype & 7)

    if (typevalue == symbols.GIW_TYPES_UINT16 or
        typevalue == symbols.GIW_TYPES_INT16):
        step = int(step / 2)
    elif (typevalue == symbols.GIW_TYPES_INT32 or
          typevalue == symbols.GIW_TYPES_FLOAT32):
        step = int(step / 4)
    elif typevalue == symbols.GIW_TYPES_FLOAT64:
        step = int(step / 8)

    return (buffer, width, height, channels, typevalue, step, pixel_layout)


def is_symbol_observable(symbol):
    """
    Returns true if the given symbol is of observable type (the type of the
    buffer you are working with). Make sure to check for pointers of your type
    as well
    """
    # Check if symbol type is the expected buffer
    symbol_type = str(symbol.type)
    type_regex = r'(const\s+)?cv::Mat(\s+?[*&])?'
    return re.match(type_regex, symbol_type) is not None