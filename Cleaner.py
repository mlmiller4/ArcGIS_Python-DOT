#-------------------------------------------------------------------------------
# Name:        Cleaning Directory
# Purpose:     Walks Directory and clears any files extending past 30 day period. Recursively
#              checks any subdirectories also. Any files that are not writeable are passed.
#
# Author:      Todd Ulery
#
# Created:     05/12/2013
# Copyright:   HDR Inc.

#-------------------------------------------------------------------------------

import os, time, shutil

from os import sys

# One day = 86400 seconds x 30 days

##base = os.curdir
base = r"E:\gis\projects\IL\Chicago\CDOT_Menu_Pro\Spatial\gdb\working\scratch"

#Check if Dir
valid = False
if os.path.isdir(base):
    valid = True

    print valid
else:
    print "...NOT VALID."
    exit


def clean(dir):
    if valid:
        if not os.access(dir, os.R_OK|os.X_OK): return
        now = time.time()

        for f in os.listdir(dir):
            curpath = os.path.join(dir, f)
            if os.path.isfile(curpath):
                locking(curpath)

            if os.path.isdir(curpath):
                locking(curpath)

            if locking.lock is True:
                pass
            if locking.lock is False:
                if os.path.isfile(curpath) and os.stat(curpath).st_mtime < (now - (30 * 86400)):
                    os.remove(curpath)
                if os.path.isdir(curpath) and locking.ext == 'gdb':
                    if os.stat(curpath).st_mtime < (now - (30 * 86400)):
                        shutil.rmtree(curpath, True, None)
            else:
                if os.path.isfile(curpath):
                    pass
                elif os.path.isdir(curpath):
                        clean(curpath)
    else:
        pass
    print"...Finished."

def locking(curpath):
    setattr(locking, "Lock", None)
    setattr(locking, "ext", None)
    obj = None
    try:
        buffer_size = 8
        obj = open(curpath, 'a', buffer_size)
        if obj:
            locking.lock = False
    except IOError, message:
        print message
        ext = os.path.splitext(curpath)
        print ext[1]
        if ext[1] == '.gdb':
            locking.lock = False
            locking.ext ="gdb"
        else:
            locking.lock = True
    finally:
        if obj:
            obj.close()
        return

clean(base)