# import pyczmq


from zyre.Zyre import Zyre
from zyre.ZyreEvent import ZyreEvent





# from cffi import FFI

# def zmq_version_info():
#     ffi = FFI()
#     ffi.cdef('void zmq_version(int *major, int *minor, int *patch);')
#     libzmq = ffi.verify('#include <zmq.h>',
#                                             libraries=['c', 'zmq'])
#     major = ffi.new('int*')
#     minor = ffi.new('int*')
#     patch = ffi.new('int*')

#     libzmq.zmq_version(major, minor, patch)

#     return (int(major[0]), int(minor[0]), int(patch[0]))

# zmq_version_info()
print('everything is ok')