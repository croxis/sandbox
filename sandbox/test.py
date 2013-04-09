import urwid
from direct.showbase.ShowBase import ShowBase
import select

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        # Load the environment model.
        self.environ = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.environ.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.environ.setScale(0.25, 0.25, 0.25)
        self.environ.setPos(-8, 42, 0)


class PandaMainLoop(urwid.MainLoop):
    pass

class PandaEventLoop(object):
    """
    Event loop based on Panda3d
    """
    _idle_emulation_delay = 1.0/256 # a short time (in seconds)

    def __init__(self, showBase=None, manage_base=True):
        """
        :param showBase: ShowBase to use
        :type shorBase: :class:`direct.showbase.ShowBase.ShowBase`.
        :param: manage_base: `True` if you want this event loop to run
                                and stop the reactor.
        :type manage_base: boolean

        .. WARNING::
           Panda3d doesn't like to be stopped and run again.  If you
           need to stop and run your :class:`MainLoop`, consider setting
           ``manage_base=False`` and take care of running/stopping the reactor
           at the beginning/ending of your program yourself.

        .. _Panda3D: http://www.panda3d.org/
        """
        if showBase is None:
            from direct.showbase.ShowBase import ShowBase
            showBase = ShowBase()
        self.showBase = showBase
        self._alarms = []
        self._watch_files = {}
        self._idle_handle = 0
        self._panda_idle_enabled = False
        self._idle_callbacks = {}
        self._exc_info = None
        self.manage_base = manage_base
        self._enable_panda_idle()

    def alarm(self, seconds, callback):
        """
        Call callback() given time from from now.  No parameters are
        passed to callback.

        Returns a handle that may be passed to remove_alarm()

        seconds -- floating point time to wait before calling callback
        callback -- function to call from event loop
        """
        handle = self.reactor.callLater(seconds, self.handle_exit(callback))
        return handle

    def remove_alarm(self, handle):
        """
        Remove an alarm.

        Returns True if the alarm exists, False otherwise
        """
        from twisted.internet.error import AlreadyCancelled, AlreadyCalled
        try:
            handle.cancel()
            return True
        except AlreadyCancelled:
            return False
        except AlreadyCalled:
            return False

    def _test_remove_alarm(self):
        """
        >>> evl = TwistedEventLoop()
        >>> handle = evl.alarm(50, lambda: None)
        >>> evl.remove_alarm(handle)
        True
        >>> evl.remove_alarm(handle)
        False
        """

    def watch_file(self, fd, callback):
        """
        Call callback() when fd has some data to read.  No parameters
        are passed to callback.

        Returns a handle that may be passed to remove_watch_file()

        fd -- file descriptor to watch for input
        callback -- function to call when input is available
        """
        ind = TwistedInputDescriptor(self.reactor, fd,
            self.handle_exit(callback))
        self._watch_files[fd] = ind
        self.reactor.addReader(ind)
        return fd

    def remove_watch_file(self, handle):
        """
        Remove an input file.

        Returns True if the input file exists, False otherwise
        """
        if handle in self._watch_files:
            self.reactor.removeReader(self._watch_files[handle])
            del self._watch_files[handle]
            return True
        return False

    def _test_remove_watch_file(self):
        """
        >>> evl = TwistedEventLoop()
        >>> handle = evl.watch_file(1, lambda: None)
        >>> evl.remove_watch_file(handle)
        True
        >>> evl.remove_watch_file(handle)
        False
        """

    def enter_idle(self, callback):
        """
        Add a callback for entering idle.

        Returns a handle that may be passed to remove_enter_idle()
        """
        self._idle_handle += 1
        self._idle_callbacks[self._idle_handle] = callback
        return self._idle_handle

    def _enable_panda_idle(self):
        """
        Panda3D's reactors don't have an idle or enter-idle callback
        so the best we can do for now is to set a timer event in a very
        short time to approximate an enter-idle callback.

        .. WARNING::
           This will perform worse than the other event loops until we can find a
           fix or workaround
        """
        if self._panda_idle_enabled:
            return
        self.showBase.doMethodLater(self._idle_emulation_delay,
            self.handle_exit_task, 'urwid', extraArgs=[self._panda_idle_callback, False])
        #self.reactor.callLater(self._idle_emulation_delay,
        #    self.handle_exit(self._twisted_idle_callback, enable_idle=False))
        self._panda_idle_enabled = True

    def _panda_idle_callback(self):
        for callback in self._idle_callbacks.values():
            callback()
        self._panda_idle_enabled = False

    def remove_enter_idle(self, handle):
        """
        Remove an idle callback.

        Returns True if the handle was removed.
        """
        try:
            del self._idle_callbacks[handle]
        except KeyError:
            return False
        return True

    def run(self):
        """
        Start the event loop.  Exit the loop when any callback raises
        an exception.  If ExitMainLoop is raised, exit cleanly.
        """
        if not self.manage_base:
            return
        self.showBase.run()
        if self._exc_info:
            # An exception caused us to exit, raise it now
            exc_info = self._exc_info
            self._exc_info = None
            raise exc_info[0], exc_info[1], exc_info[2]

    def _test_run(self):
        """
        >>> import os
        >>> rd, wr = os.pipe()
        >>> os.write(wr, "data") # something to read from rd
        4
        >>> evl = TwistedEventLoop()
        >>> def say_hello_data():
        ...     print "hello data"
        ...     os.read(rd, 4)
        >>> def say_waiting():
        ...     print "waiting"
        >>> def say_hello():
        ...     print "hello"
        >>> handle = evl.watch_file(rd, say_hello_data)
        >>> def say_being_twisted():
        ...     print "oh I'm messed up"
        ...     raise ExitMainLoop
        >>> handle = evl.alarm(0.0625, say_being_twisted)
        >>> handle = evl.alarm(0.03125, say_hello)
        >>> evl.enter_idle(say_waiting)
        1
        >>> evl.run()
        hello data
        waiting
        hello
        waiting
        oh I'm messed up
        """

    def handle_exit(self, f, enable_idle=True):
        """
        Decorator that cleanly exits the :class:`TwistedEventLoop` if
        :class:`ExitMainLoop` is thrown inside of the wrapped function. Store the
        exception info if some other exception occurs, it will be reraised after
        the loop quits.

        *f* -- function to be wrapped
        """
        def wrapper(*args, **kargs):
            rval = None
            try:
                rval = f(*args, **kargs)
            except urwid.ExitMainLoop:
                if self.manage_reactor:
                    self.reactor.stop()
            except:
                import sys
                print sys.exc_info()
                self._exc_info = sys.exc_info()
                if self.manage_reactor:
                    self.reactor.crash()
            if enable_idle:
                self._enable_panda_idle()
            return rval
        return wrapper

    def handle_exit_task(self, task, f, enable_idle=True):
        """
        Decorator that cleanly exits the :class:`TwistedEventLoop` if
        :class:`ExitMainLoop` is thrown inside of the wrapped function. Store the
        exception info if some other exception occurs, it will be reraised after
        the loop quits.

        *f* -- function to be wrapped

        This is the same as above, but for panda3d task system
        """
        def wrapper(*args, **kargs):
            rval = None
            try:
                rval = f(*args, **kargs)
            except urwid.ExitMainLoop:
                if self.manage_reactor:
                    self.showBase.stop()
            except:
                import sys
                print sys.exc_info()
                self._exc_info = sys.exc_info()
                if self.manage_showBase:
                    self.showBase.crash()
            if enable_idle:
                self._enable_panda_idle()
            return rval
        return task.done




def show_or_exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()
    txt.set_text(repr(key))
app = MyApp()

txt = urwid.Text(u"Hello World")
fill = urwid.Filler(txt, 'top')
loop = urwid.MainLoop(fill, unhandled_input=show_or_exit,
    event_loop=PandaEventLoop(app))
#loop.event_loop = PEventLoop()
#loop.run()
#app.run()
loop.run()