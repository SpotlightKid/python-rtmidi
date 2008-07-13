# test_threadworker.py

import md5, sha
from threadpool import *

bufsize = 8*1024
rmode = 'rb'

def getmd5(filename, data=None):
    try:
        fp = open(filename, rmode)
    except IOError, exc:
        return (exc, '%s: Can\'t open: %s\n' % (filename, exc))
    m = md5.new()
    try:
        # this will get the disk thrashing very quickly!
        ## while 1:
            ## data = fp.read(bufsize)
            ## if not data:
                ## break
        m.update(fp.read())
    except IOError, exc:
        return (exc, '%s: I/O error: %s\n' % (filename, exc))
    else:
        fp.close()
    return m.hexdigest()

def getmd5_2(dummy, data):
    m = md5.new()
    m.update(data)
    return m.hexdigest()

def getsha(dummy, data):
    m = sha.new()
    m.update(data)
    return m.hexdigest()

def print_result(request, result):
    print '"%s", %s' % (os.path.basename(request.args[0]), result)

if __name__ == '__main__':
    import os, sys

    try:
        topdir = sys.argv[1]
    except IndexError:
        topdir = os.curdir

    files = []
    for dirpath, dirname, filenames in os.walk(topdir):
        for filename in filenames:
            filename = os.path.join(dirpath, filename)
            if os.path.isfile(filename):
                files.append(filename, )
    files.sort()

    main = ThreadPool(10, q_size=50)
    for file in files:
        # bad approach
        ## main.putRequest(WorkRequest(getmd5, args=(file, None),
        ##   callback=print_result))
        # better approach
        main.putRequest(WorkRequest(getsha, args=(file, open(file).read()),
          callback=print_result))
        try:
            main.poll()
        except NoResultsPending:
            pass
    main.wait()
