'''Panda3D urwid interface
Version 1
Authors: croxis

This is an example of a command line curses style gui for Panda3D.
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

Known bugs: Text typed in bash is invisible after exiting
Non panda logs don't get pipped into log window
Todo: Replace python eval with bpython
'''

import urwid
from urwid.display_common import INPUT_DESCRIPTORS_CHANGED

from panda3d.core import Notify, LineStream
from direct.directnotify.DirectNotify import DirectNotify


### Urwid overrides ###
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


class PandaMainLoop(urwid.MainLoop):
    '''urwid.MainLoop run function is designed to run forever. This does
    otherwise and splits cleanup into a different function.'''
    pandaSetup = False

    def run(self, task=None):
        try:
            self._run()
            #if self.screen.started:
            #    self._run()
            #else:
            #    self.screen.run_wrapper(self._run)
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

            self.rid = reset_input_descriptors

            try:
                urwid.signals.connect_signal(
                    self.screen, INPUT_DESCRIPTORS_CHANGED,
                    #reset_input_descriptors
                    self.rid
                )
            except NameError:
                pass
            # watch our input descriptors
            reset_input_descriptors()
            self.idle_handle = self.event_loop.enter_idle(self.entering_idle)
            self.pandaSetup = True

        # Go..
        self.event_loop.run()
        if task:
            return task.cont

    def panda_quit(self):
        '''Forces raising exception to try and quit. I think'''
        raise urwid.ExitMainLoop()

    def pandaCleanup(self):
        raise urwid.ExitMainLoop()
        # tidy up
        self.event_loop.remove_enter_idle(self.idle_handle)
        #reset_input_descriptors(True)
        self.rid(True)
        urwid.signals.disconnect_signal(
            self.screen, INPUT_DESCRIPTORS_CHANGED,
            #reset_input_descriptors)
            self.rid
        )


### Console UI ###

# Enums for state
PYTHON = 0
LOGS = 1
COMMANDWIN = 2

state = 0

# Command mapper. Command string will be stripped
# {'command string': function}
commands = {}


def add_command(command_string, function):
    '''Adds command to command database. All commands are handled in lower
    case internally.'''
    commands[command_string] = function


def print_to_command(output_string):
    '''Prints text to the command console.'''
    commandOutput.contents.append(urwid.Text(output_string))
    commandOutput.set_focus(len(commandOutput) - 1)


def onScreenChange(button, newState, userData=None):
    global state
    if newState and button.get_label() == 'Python Console':
        fill.body = pythonOutputWindow
        fill.footer = edit
        fill.set_focus('footer')
        state = PYTHON
    elif newState and button.get_label() == 'Logs':
        fill.body = logOutputWindow
        fill.footer = None
        fill.set_focus('body')
        state = LOGS
    elif newState and button.get_label() == 'Server Console':
        fill.body = commandOutputWindow
        fill.footer = edit
        fill.set_focus('footer')
        state = COMMANDWIN


class CommandEdit(urwid.Edit):
    def keypress(self, size, key):
        if key != 'enter':
            super(CommandEdit, self).keypress(size, key)
        else:
            '''Here you would add a command processor where the game
            would respond with a message that is placed in output, or
            a message is sent with a callback that places the message in
            output.

            The editor functions in on of two ways. If the python window
            is active then the thread will be validated. If the command
            window is active the command will be checked against a database,
            the appropriate function called and parameters passed.

            All text is lower case internally.

            Any additional text is passed as one argument'''
            text = edit.edit_text.lower()
            edit.edit_text = ''

            if state == COMMANDWIN:
                commandOutput.contents.append(urwid.Text(text))
                commandOutput.set_focus(len(commandOutput) - 1)

                # I am sure there is a better way to do this
                for command, function in commands.items():
                    if text.startswith(command):
                        remaining_text = text.lstrip(command + ' ')
                        if remaining_text:
                            commands[command](remaining_text)
                        else:
                            commands[command]()
            elif state == PYTHON:
                pythonOutput.contents.append(urwid.Text('>>> ' + text))
                try:
                    pythonOutput.contents.append(urwid.Text(str(eval(text))))
                    #pythonOutput.contents.append(urwid.Text(str(eval(compile(text, '<string>', 'single')))))
                except SyntaxError:
                    pythonOutput.contents.append(
                        urwid.Text("Exception: " + str(SyntaxError))
                    )
                pythonOutput.set_focus(len(pythonOutput) - 1)


#Menu
menuList = []
#rb = urwid.RadioButton(mode_radio_buttons, text, state)
rb = urwid.RadioButton(menuList, 'Python Console', False)
urwid.connect_signal(rb, 'change', onScreenChange)
rb = urwid.RadioButton(menuList, 'Logs', True)
urwid.connect_signal(rb, 'change', onScreenChange)
rb = urwid.RadioButton(menuList, 'Server Console', False)
urwid.connect_signal(rb, 'change', onScreenChange)
menu = urwid.Columns(menuList, 2)

#Input
edit = CommandEdit('> ')

#Output
logOutput = urwid.SimpleListWalker([])
logOutputWindow = urwid.ListBox(logOutput)

pythonOutput = urwid.SimpleListWalker([])
pythonOutputWindow = urwid.ListBox(pythonOutput)

commandOutput = urwid.SimpleListWalker([])
commandOutputWindow = urwid.ListBox(commandOutput)

fill = urwid.Frame(logOutputWindow, header=menu, footer=None, focus_part='body')


# Here we hook panda3d's logging into our system
line_stream = LineStream()
Notify.ptr().setOstreamPtr(line_stream, 0)


def get_logs(task):
    '''Yanks Panda3D's log pipe and pumps it to logOutput'''
    #if line_stream.hasNewline():
    while line_stream.isTextAvailable():
        logOutput.contents.append(urwid.Text(line_stream.getLine()))
        logOutput.set_focus(len(logOutput) - 1)
    return task.cont


if __name__ == '__main__':
    from direct.showbase.ShowBase import ShowBase
    from math import pi, sin, cos
    from direct.task import Task

    log = DirectNotify().newCategory("SandBox")
    log.info("Sweet")

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
    app.taskMgr.add(spinCameraTask, "SpinCameraTask")

    '''Here are all the steps to add the console to a panda. For now these
    are required to be added manually.'''
    main_loop = PandaMainLoop(fill, event_loop=PandaEventLoop())
    main_loop.screen.start()
    app.taskMgr.add(main_loop.run, 'urwid')
    app.taskMgr.add(get_logs, 'get_logs')


    '''Here is an example of adding a quit command'''
    def quit():
        print_to_command("Attempting to quit")
        app.taskMgr.stop()
        main_loop.pandaCleanup()

    def camera(text=''):
        '''We can't be sure if extra text will be sent'''
        log.info("A camera command")
        if not text:
            print_to_command("Syntax: 'camera start', 'camera stop'")
        elif text.split()[0] == 'start':
            print_to_command("Starting camera")
            app.taskMgr.add(spinCameraTask, "SpinCameraTask")
        elif text.split()[0] == 'stop':
            print_to_command("Stopping camera")
            app.taskMgr.remove("SpinCameraTask")

    add_command('quit', quit)
    add_command('camera', camera)

    app.run()
