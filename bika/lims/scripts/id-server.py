import os, sys, getopt, cgi
import BaseHTTPServer
from cPickle import Pickler, Unpickler

class IDRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def run(self):
        try:
            self.counter_file = os.environ.get('counter')
            self.get_id()
        except:
            self.send_response(400)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            raise
    do_GET = run
    # do_POST = run

    def getCounter(self, key):
        # initialise counter
        try:
            f = open(self.counter_file, 'r+')
            self._counters = Unpickler(f).load()
        except:
            f = open(self.counter_file, 'w+')
            self._counters = {}
        f.close()
        if not self._counters.has_key(key):
            self._counters[key] = 0
        return self._counters[key]

    def setCounter(self, key, count):
        self._counters[key] = count
        f = open(self.counter_file, 'r+')
        p = Pickler(f)
        p.dump(self._counters)
        f.close()

    def get_id(self):
        batch_size = None
        command = self.command.lower() 
        if command == 'get' and self.path.find('?') != -1:
            key, qs = self.path.split('?', 1)
            data = cgi.parse_qs(qs)
            try:
                batch_size = int(data['batch_size'][0])
            except:
                batch_size = None
        else:
            key = self.path

        # POST (also works .. let's GET for now .. )
        # elif command == 'post':
        #     key = self.path
        #     length = self.headers.getheader('content-length')
        #     if length:
        #         length = int(length)
        #         qs = self.rfile.read(length)
        #         data = cgi.parse_qs(qs)

        prev_count = self.getCounter(key)
        next_count = prev_count + 1
        if batch_size:
            last_count = prev_count + batch_size
        else:
            last_count = next_count 
        self.setCounter(key, last_count)
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(str(next_count))

# Copied and modified roundup-server code - thanks Richard Jones

def usage(message=''):
    if message:
        message = 'Error: %(error)s\n\n'%{'error': message}
    print '''%(message)sUsage:
id-server [-f counter] [-n hostname] [-p port] [-l file] [-d file]

  -f: counter file
  -n: sets the host name
  -p: sets the port to listen on
  -l: sets a filename to log to (instead of stdout)
  -d: run the server in the background and on UN*X write the server's PID
      to the nominated file. Note: on Windows the PID argument is needed,
      but ignored.

  Call the ID server with the key for which you want a count as path.
  E.g. calling
    http://<hostname>:<port>/Key
  repeatedly will return 1, 2, 3, etc. To start counting at a particular
  number (e.g. to skip a range of numbers), pass 'count_from' as a
  parameter:
    http://<hostname>:<port>/Key?count_from=104
  This will return 104, or (if 104 has already been issued) the next
  available number.

'''%locals()
    sys.exit(0)

def abspath(path):
    ''' Make the given path an absolute path.

        Code from Zope-Coders posting of 2002-10-06 by GvR.
    '''
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    return os.path.normpath(path)

def daemonize(pidfile):
    ''' Turn this process into a daemon.
        - make sure the sys.std(in|out|err) are completely cut off
        - make our parent PID 1

        Write our new PID to the pidfile.

        From A.M. Kuuchling (possibly originally Greg Ward) with
        modification from Oren Tirosh, and finally a small mod from me.
    '''
    # Fork once
    if os.fork() != 0:
        os._exit(0)

    # Create new session
    os.setsid()

    # Second fork to force PPID=1
    pid = os.fork()
    if pid:
        pidfile = open(pidfile, 'w')
        pidfile.write(str(pid))
        pidfile.close()
        os._exit(0)         

    os.chdir("/")         
    os.umask(0)

    # close off sys.std(in|out|err), redirect to devnull so the file
    # descriptors can't be used again
    devnull = os.open('/dev/null', 0)
    os.dup2(devnull, 0)
    os.dup2(devnull, 1)
    os.dup2(devnull, 2)

def run():
    ''' Script entry point - handle args and figure out what to to.
    '''
    # time out after a minute if we can
    import socket
    if hasattr(socket, 'setdefaulttimeout'):
        socket.setdefaulttimeout(120)

    hostname = ''
    port = 8081
    pidfile = None
    logfile = None
    user = None
    counter = None
    try:
        # handle the command-line args
        try:
            optlist, args = getopt.getopt(sys.argv[1:], 'f:n:p:u:d:l:h')
        except getopt.GetoptError, e:
            usage(str(e))

        for (opt, arg) in optlist:
            if opt == '-f': counter = arg
            elif opt == '-n': hostname = arg
            elif opt == '-p': port = int(arg)
            elif opt == '-u': user = arg
            elif opt == '-d': pidfile = abspath(arg)
            elif opt == '-l': logfile = abspath(arg)
            elif opt == '-h': usage()

        if hasattr(os, 'getuid'):
            # if root, setuid to the running user
            if not os.getuid() and user is not None:
                try:
                    import pwd
                except ImportError:
                    raise ValueError, "Can't change users - no pwd module"
                try:
                    uid = pwd.getpwnam(user)[2]
                except KeyError:
                    raise ValueError, "User %(user)s doesn't exist"%locals()
                os.setuid(uid)
            elif os.getuid() and user is not None:
                print 'WARNING: ignoring "-u" argument, not root'

            # People can remove this check if they're really determined
            if not os.getuid() and user is None:
                raise ValueError, "Can't run as root!"

        if counter is None:
            raise ValueError, "You have to specify the location of the counter file."
        else:
            os.environ['counter'] = counter

    except SystemExit:
        raise
    except:
        exc_type, exc_value = sys.exc_info()[:2]
        usage('%s: %s'%(exc_type, exc_value))

    # we don't want the cgi module interpreting the command-line args ;)
    sys.argv = sys.argv[:1]
    address = (hostname, port)

    # fork?
    if pidfile:
        if not hasattr(os, 'fork'):
            print "Sorry, you can't run the server as a daemon on this" \
                'Operating System'
            sys.exit(0)
        else:
            daemonize(pidfile)

    # redirect stdout/stderr to our logfile
    if logfile:
        # appending, unbuffered
        sys.stdout = sys.stderr = open(logfile, 'a', 0)

    httpd = BaseHTTPServer.HTTPServer(address, IDRequestHandler)
    print 'ID server started on %(address)s'%locals()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print 'Keyboard Interrupt: exiting'

if __name__ == '__main__':
    run()
