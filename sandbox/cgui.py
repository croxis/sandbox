'''This is an example of a command line curses style gui for Panda3D.
It uses urwid for graphical widgets and bpython for the python console.

This sample creates 3 windows. The first is for controlling the application
though text commands (ie, like a minecraft server). In this example text
is just reposted to the output.

The second window is a read only log viewer.

The last window is an interactive python interpreter allowing for direct
manipulation of your application and Panda3D. This is not intended to
be an full fledged IDE, but just another debugging and prototyping
tool.

Additional windows can be added or removed as seen fit.

I have tried to be extra verbose with the comments for the sake of learning.

This snippet of code is under the MIT license.
'''

import os

import urwid
from urwid.display_common import INPUT_DESCRIPTORS_CHANGED

## Setup basic urwid windows ##


def onScreenChange(button, newState, userData=None):
    if newState and button.get_label() == 'Python Console':
        #fill = urwid.Frame(myrepl.frame, menu)
        fill.body = myrepl.frame
        fill.footer = None
        fill.set_focus('body')
    elif newState and button.get_label() == 'Logs':
        fill.footer = None
        fill.set_focus('body')
    elif newState and button.get_label() == 'Server Console':
        fill.body = outputWindow
        fill.footer = edit
        fill.set_focus('footer')
        #fill = urwid.Frame(outputWindow, menu, edit, 'footer')


class CommandEdit(urwid.Edit):
    def keypress(self, size, key):
        if key != 'enter':
            super(CommandEdit, self).keypress(size, key)
        else:
            '''Here you would add a command processor where the game
            would respond with a message that is placed in output, or
            a message is sent with a callback that places the message in
            output'''
            text = edit.edit_text
            output.contents.append(urwid.Text(text))
            edit.edit_text = ''
            output.set_focus(len(output) - 1)
            if text in ('quit', 'Quit'):
                output.contents.append(urwid.Text("Attempting to quit"))
                output.set_focus(len(output) - 1)
                raise urwid.ExitMainLoop()
#Input
edit = CommandEdit('> ')


#Menu
menuList = []
#rb = urwid.RadioButton(mode_radio_buttons, text, state)
rb = urwid.RadioButton(menuList, 'Python Console', True)
urwid.connect_signal(rb, 'change', onScreenChange)
rb = urwid.RadioButton(menuList, 'Logs', False)
urwid.connect_signal(rb, 'change', onScreenChange)
rb = urwid.RadioButton(menuList, 'Server Console', False)
urwid.connect_signal(rb, 'change', onScreenChange)
menu = urwid.Columns(menuList, 2)

#Output
output = urwid.SimpleListWalker([])
outputWindow = urwid.ListBox(output)


## Panda overrides for urwid loops ##


class PandaEventLoop(urwid.SelectEventLoop):
    '''urwid defaults classes expect to be managing the master loop.
    This does otherwise'''
    def run(self):
        '''This version of run is called manually each tick'''
        try:
            self._did_something = True
            self._loop()
        except urwid.ExitMainLoop:
            pass
        '''try:
            self._did_something = True
            try:
                self._loop()
            except select.error, e:
                if e.args[0] != 4:
                    raise
        except urwid.ExitMainLoop:
            pass'''


class PandaMainLoop(urwid.MainLoop):
    '''urwid.MainLoop run function is designed to run forever. This does
    otherwise and splits cleanup into a different function.'''
    pandaSetup = False

    def run(self, task=None):
        try:
            if self.screen.started:
                self._run()
            else:
                self.screen.run_wrapper(self._run)
            if task:
                return task.cont
        except urwid.ExitMainLoop:
            return task.done

    def _run(self, task=None):
        '''This must be called each tick from Panda3D main thread.'''
        if not self.pandaSetup:
            if self.handle_mouse:
                self.screen.set_mouse_tracking()

            if not hasattr(self.screen, 'get_input_descriptors'):
                return self._run_screen_event_loop()

            self.draw_screen()

            fd_handles = []

            def reset_input_descriptors(only_remove=False):
                for handle in fd_handles:
                    self.event_loop.remove_watch_file(handle)
                if only_remove:
                    del fd_handles[:]
                else:
                    fd_handles[:] = [
                        self.event_loop.watch_file(fd, self._update)
                        for fd in self.screen.get_input_descriptors()]
                if not fd_handles and self._input_timeout is not None:
                    self.event_loop.remove_alarm(self._input_timeout)
            try:
                urwid.signals.connect_signal(
                    self.screen, INPUT_DESCRIPTORS_CHANGED,
                    reset_input_descriptors
                )
            except NameError:
                pass
            # watch our input descriptors
            reset_input_descriptors()
            idle_handle = self.event_loop.enter_idle(self.entering_idle)
            self.pandaSetup = True

        # Go..
        self.event_loop.run()
        if task:
            return task.cont

    def pandaCleanup(self):
        # tidy up
        self.event_loop.remove_enter_idle(idle_handle)
        reset_input_descriptors(True)
        signals.disconnect_signal(self.screen, INPUT_DESCRIPTORS_CHANGED,
            reset_input_descriptors)



## Overrides for bpython to work under panda's loop and modified urwid ##


import bpython
import locale
from bpython import args as bpargs, repl
from bpython.importcompletion import find_coroutine
import bpython.urwid as bp
import sys

COLORMAP = {
    'k': 'black',
    'r': 'dark red',  # or light red?
    'g': 'dark green',  # or light green?
    'y': 'yellow',
    'b': 'dark blue',  # or light blue?
    'm': 'dark magenta',  # or light magenta?
    'c': 'dark cyan',  # or light cyan?
    'w': 'white',
    'd': 'default',
}

bp.translations.init()
config, options, exec_args = bpargs.parse(None, ('Urwid options', None, []))

palette = [(name, COLORMAP[color.lower()], 'default', 'bold' if color.isupper() else 'default') for name, color in config.color_scheme.iteritems()]
palette.extend([('bold ' + name, color + ',bold', background, monochrome) for name, color, background, monochrome in palette])
interpreter = bpython.repl.Interpreter(globals(), locale.getpreferredencoding())
myrepl = bp.URWIDRepl(None, palette, interpreter, config)
orig_stdin = sys.stdin
orig_stdout = sys.stdout
orig_stderr = sys.stderr

if config.flush_output and not options.quiet:
    sys.stdout.write(myrepl.getstdout())
if hasattr(sys.stdout, "flush"):
    sys.stdout.flush()

#Input
edit = CommandEdit('> ')

#Master container
fill = urwid.Frame(myrepl.frame, menu)
myrepl.main_loop = PandaMainLoop(
    fill, palette, unhandled_input=myrepl.handle_input,
    event_loop=PandaEventLoop()
)

if config.flush_output and not options.quiet:
    sys.stdout.write(myrepl.getstdout())
if hasattr(sys.stdout, "flush"):
    sys.stdout.flush()
repl.extract_exit_value(myrepl.exit_value)


def run_with_screen_before_mainloop():
    sys.stdin = None  # FakeStdin(myrepl)
    sys.stdout = myrepl
    sys.stderr = myrepl

    myrepl.main_loop.set_alarm_in(0, start)
    '''try:
        # Currently we just set this to None because I do not
        # expect code hitting stdin to work. For example: exit()
        # (not sys.exit, site.py's exit) tries to close sys.stdin,
        # which breaks urwid's shutdown. bpython.cli sets this to
        # a fake object that reads input through curses and
        # returns it. When using twisted I do not think we can do
        # that because sys.stdin.read and friends block, and we
        # cannot re-enter the reactor. If using urwid's own
        # mainloop we *might* be able to do something similar and
        # re-enter its mainloop.
        sys.stdin = None  # FakeStdin(myrepl)
        sys.stdout = myrepl
        sys.stderr = myrepl

        myrepl.main_loop.set_alarm_in(0, start)

        while True:
            try:
                myrepl.main_loop.run()
            except KeyboardInterrupt:
                # HACK: if we run under a twisted mainloop this should
                # never happen: we have a SIGINT handler set.
                # If we use the urwid select-based loop we just restart
                # that loop if interrupted, instead of trying to cook
                # up an equivalent to reactor.callFromThread (which
                # is what our Twisted sigint handler does)
                myrepl.main_loop.set_alarm_in(
                    0, lambda *args: myrepl.keyboard_interrupt())
                continue
            break

    finally:
        sys.stdin = orig_stdin
        sys.stderr = orig_stderr
        sys.stdout = orig_stdout'''


# This needs more thought. What needs to happen inside the mainloop?
def start(main_loop, user_data):
    if exec_args:
        bpargs.exec_code(interpreter, exec_args)
        if not options.interactive:
            raise urwid.ExitMainLoop()
    if not exec_args:
        sys.path.insert(0, '')
        # this is CLIRepl.startup inlined.
        filename = os.environ.get('PYTHONSTARTUP')
        if filename and os.path.isfile(filename):
            with open(filename, 'r') as f:
                interpreter.runsource(f.read(), filename, 'exec', encode=False)
    myrepl.start()
    #myrepl.main_loop.screen.start()

    # This bypasses main_loop.set_alarm_in because we must *not*
    # hit the draw_screen call (it's unnecessary and slow).
    def run_find_coroutine():
        if find_coroutine():
            main_loop.event_loop.alarm(0, run_find_coroutine)

    run_find_coroutine()


if __name__ == '__main__':
    from direct.showbase.ShowBase import ShowBase
    from math import pi, sin, cos
    from direct.task import Task

    def spinCameraTask(task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (pi / 180.0)
        app.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        app.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont

    class MyApp(ShowBase):
        def __init__(self):
            ShowBase.__init__(self)
            self.environ = self.loader.loadModel("models/environment")
            self.environ.reparentTo(self.render)
            self.environ.setScale(0.25, 0.25, 0.25)
            self.environ.setPos(-8, 42, 0)

    app = MyApp()

    #This results in a working urwid screen, but not bpython
    #myrepl.main_loop.screen.start()

    #This results in a non working screen
    #myrepl.main_loop.screen.run_wrapper(run_with_screen_before_mainloop)
    run_with_screen_before_mainloop()

    app.taskMgr.add(spinCameraTask, "SpinCameraTask")
    app.taskMgr.add(myrepl.main_loop.run, 'cgui')
    app.run()

    myrepl.main_loop.pandaCleanup()

    sys.stdin = orig_stdin
    sys.stderr = orig_stderr
    sys.stdout = orig_stdout

    if config.flush_output and not options.quiet:
        sys.stdout.write(myrepl.getstdout())
    if hasattr(sys.stdout, "flush"):
        sys.stdout.flush()
    repl.extract_exit_value(myrepl.exit_value)
