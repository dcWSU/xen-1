import sys
import struct
import types

from xen.lowlevel import xu

DEBUG = 0

""" All message formats.
Added to incrementally for the various message types.
See below.
"""
msg_formats = {}

#============================================================================
# Console message types.
#============================================================================

CMSG_CONSOLE  = 0

console_formats = { 'console_data': (CMSG_CONSOLE, 0) }

msg_formats.update(console_formats)

#============================================================================
# Block interface message types.
#============================================================================

CMSG_BLKIF_BE = 1
CMSG_BLKIF_FE = 2

CMSG_BLKIF_FE_INTERFACE_STATUS_CHANGED =  0
CMSG_BLKIF_FE_DRIVER_STATUS_CHANGED    = 32
CMSG_BLKIF_FE_INTERFACE_CONNECT        = 33
CMSG_BLKIF_FE_INTERFACE_DISCONNECT     = 34

CMSG_BLKIF_BE_CREATE      = 0
CMSG_BLKIF_BE_DESTROY     = 1
CMSG_BLKIF_BE_CONNECT     = 2
CMSG_BLKIF_BE_DISCONNECT  = 3
CMSG_BLKIF_BE_VBD_CREATE  = 4
CMSG_BLKIF_BE_VBD_DESTROY = 5
CMSG_BLKIF_BE_VBD_GROW    = 6
CMSG_BLKIF_BE_VBD_SHRINK  = 7
CMSG_BLKIF_BE_DRIVER_STATUS_CHANGED    = 32

BLKIF_DRIVER_STATUS_DOWN  = 0
BLKIF_DRIVER_STATUS_UP    = 1

BLKIF_INTERFACE_STATUS_DESTROYED    = 0 #/* Interface doesn't exist.    */
BLKIF_INTERFACE_STATUS_DISCONNECTED = 1 #/* Exists but is disconnected. */
BLKIF_INTERFACE_STATUS_CONNECTED    = 2 #/* Exists and is connected.    */
BLKIF_INTERFACE_STATUS_CHANGED      = 3 #/* A device has been added or removed. */

BLKIF_BE_STATUS_OKAY                = 0
BLKIF_BE_STATUS_ERROR               = 1
BLKIF_BE_STATUS_INTERFACE_EXISTS    = 2
BLKIF_BE_STATUS_INTERFACE_NOT_FOUND = 3
BLKIF_BE_STATUS_INTERFACE_CONNECTED = 4
BLKIF_BE_STATUS_VBD_EXISTS          = 5
BLKIF_BE_STATUS_VBD_NOT_FOUND       = 6
BLKIF_BE_STATUS_OUT_OF_MEMORY       = 7
BLKIF_BE_STATUS_EXTENT_NOT_FOUND    = 8
BLKIF_BE_STATUS_MAPPING_ERROR       = 9

blkif_formats = {
    'blkif_be_connect_t':
    (CMSG_BLKIF_BE, CMSG_BLKIF_BE_CONNECT),

    'blkif_be_create_t':
    (CMSG_BLKIF_BE, CMSG_BLKIF_BE_CREATE),

    'blkif_be_disconnect_t':
    (CMSG_BLKIF_BE, CMSG_BLKIF_BE_DISCONNECT),

    'blkif_be_destroy_t':
    (CMSG_BLKIF_BE, CMSG_BLKIF_BE_DESTROY),

    'blkif_be_vbd_create_t':
    (CMSG_BLKIF_BE, CMSG_BLKIF_BE_VBD_CREATE),

    'blkif_be_vbd_grow_t':
    (CMSG_BLKIF_BE, CMSG_BLKIF_BE_VBD_GROW),

    'blkif_be_vbd_destroy_t':
    (CMSG_BLKIF_BE, CMSG_BLKIF_BE_VBD_DESTROY),

    'blkif_fe_interface_status_changed_t':
    (CMSG_BLKIF_FE, CMSG_BLKIF_FE_INTERFACE_STATUS_CHANGED),

    'blkif_fe_driver_status_changed_t':
    (CMSG_BLKIF_FE, CMSG_BLKIF_FE_DRIVER_STATUS_CHANGED),

    'blkif_fe_interface_connect_t':
    (CMSG_BLKIF_FE, CMSG_BLKIF_FE_INTERFACE_CONNECT),
}

msg_formats.update(blkif_formats)

#============================================================================
# Network interface message types.
#============================================================================

CMSG_NETIF_BE = 3
CMSG_NETIF_FE = 4

CMSG_NETIF_FE_INTERFACE_STATUS_CHANGED =  0
CMSG_NETIF_FE_DRIVER_STATUS_CHANGED    = 32
CMSG_NETIF_FE_INTERFACE_CONNECT        = 33
CMSG_NETIF_FE_INTERFACE_DISCONNECT     = 34

CMSG_NETIF_BE_CREATE      = 0
CMSG_NETIF_BE_DESTROY     = 1
CMSG_NETIF_BE_CONNECT     = 2
CMSG_NETIF_BE_DISCONNECT  = 3
CMSG_NETIF_BE_DRIVER_STATUS_CHANGED    = 32

NETIF_INTERFACE_STATUS_DESTROYED    = 0 #/* Interface doesn't exist.    */
NETIF_INTERFACE_STATUS_DISCONNECTED = 1 #/* Exists but is disconnected. */
NETIF_INTERFACE_STATUS_CONNECTED    = 2 #/* Exists and is connected.    */
NETIF_INTERFACE_STATUS_CHANGED      = 3 #/* A device has been added or removed. */

NETIF_DRIVER_STATUS_DOWN   = 0
NETIF_DRIVER_STATUS_UP     = 1

netif_formats = {
    'netif_be_connect_t':
    (CMSG_NETIF_BE, CMSG_NETIF_BE_CONNECT),

    'netif_be_create_t':
    (CMSG_NETIF_BE, CMSG_NETIF_BE_CREATE),

    'netif_be_disconnect_t':
    (CMSG_NETIF_BE, CMSG_NETIF_BE_DISCONNECT),

    'netif_be_destroy_t':
    (CMSG_NETIF_BE, CMSG_NETIF_BE_DESTROY),

    'netif_be_driver_status_changed_t':
    (CMSG_NETIF_BE, CMSG_NETIF_BE_DRIVER_STATUS_CHANGED),

    'netif_fe_driver_status_changed_t':
    (CMSG_NETIF_FE, CMSG_NETIF_FE_DRIVER_STATUS_CHANGED),

    'netif_fe_interface_connect_t':
    (CMSG_NETIF_FE, CMSG_NETIF_FE_INTERFACE_CONNECT),

    'netif_fe_interface_status_changed_t':
    (CMSG_NETIF_FE, CMSG_NETIF_FE_INTERFACE_STATUS_CHANGED),
    }

msg_formats.update(netif_formats)

#============================================================================
# Domain shutdown message types.
#============================================================================

CMSG_SHUTDOWN = 6

CMSG_SHUTDOWN_POWEROFF  = 0
CMSG_SHUTDOWN_REBOOT    = 1
CMSG_SHUTDOWN_SUSPEND   = 2

STOPCODE_shutdown       = 0
STOPCODE_reboot         = 1
STOPCODE_suspend        = 2

shutdown_formats = {
    'shutdown_poweroff_t':
    (CMSG_SHUTDOWN, CMSG_SHUTDOWN_POWEROFF),
    
    'shutdown_reboot_t':
    (CMSG_SHUTDOWN, CMSG_SHUTDOWN_REBOOT),

    'shutdown_suspend_t':
    (CMSG_SHUTDOWN, CMSG_SHUTDOWN_SUSPEND),
    }

msg_formats.update(shutdown_formats)

#============================================================================

class Msg:
    pass

_next_msgid = 0

def nextid():
    """Generate the next message id.

    @return: message id
    @rtype: int
    """
    global _next_msgid
    _next_msgid += 1
    return _next_msgid

def packMsg(ty, params):
    """Pack a message.
    Any I{mac} parameter is passed in as an int[6] array and converted.

    @param ty: message type name
    @type ty: string
    @param params: message parameters
    @type params: dicy
    @return: message
    @rtype: xu message
    """
    msgid = nextid()
    if DEBUG: print '>packMsg', msgid, ty, params
    (major, minor) = msg_formats[ty]
    args = {}
    for (k, v) in params.items():
        if k == 'mac':
            for i in range(0, 6):
                args['mac[%d]' % i] = v[i]
        else:
            args[k] = v
    msg = xu.message(major, minor, msgid, args)
    if DEBUG: print '<packMsg', msg.get_header()['id'], ty, args
    return msg

def unpackMsg(ty, msg):
    """Unpack a message.
    Any mac addresses in the message are converted to int[6] array
    in the return dict.

    @param ty:  message type
    @type ty: string
    @param msg: message
    @type msg: xu message
    @return: parameters
    @rtype: dict
    """
    args = msg.get_payload()
    if DEBUG: print '>unpackMsg', args
    if isinstance(args, types.StringType):
        args = {'value': args}
    else:
        mac = [0, 0, 0, 0, 0, 0]
        macs = []
        for (k, v) in args.items():
            if k.startswith('mac['):
                macs += k
                i = int(k[4:5])
                mac[i] = v
            else:
                pass
        if macs:
            args['mac'] = mac
            for k in macs:
                del args[k]
    if DEBUG:
        msgid = msg.get_header()['id']
        print '<unpackMsg', msgid, ty, args
    return args

def msgTypeName(ty, subty):
    """Convert a message type, subtype pair to a message type name.

    @param ty: message type
    @type ty: int
    @param subty: message subtype
    @type ty: int
    @return: message type name (or None)
    @rtype: string or None
    """
    for (name, info) in msg_formats.items():
        if info[0] == ty and info[1] == subty:
            return name
    return None

def printMsg(msg, out=sys.stdout, all=0):
    """Print a message.

    @param msg: message
    @type msg: xu message
    @param out: where to print to
    @type out: stream
    @param all: print payload if true
    @type all: bool
    """
    hdr = msg.get_header()
    major = hdr['type']
    minor = hdr['subtype']
    msgid = hdr['id']
    ty = msgTypeName(major, minor)
    print >>out, 'message:', 'type=', ty, '%d:%d' % (major, minor), 'id=%d' % msgid
    if all:
        print >>out, 'payload=', msg.get_payload()

