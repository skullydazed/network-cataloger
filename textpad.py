"""Simple textbox editing widget with Emacs-like keybindings.

This extends curses.textpad.Textbox because it is not smart enough to let 
me override only one or two keys.
"""

import curses
import curses.ascii
import curses.textpad


class Textbox(curses.textpad.Textbox):
    """Extend curses.textpad.Textbox to allow for binding keys to arbitrary
        commands. This class should not be used directly. Instead you should 
        write your own class that inherits from Textbox.

        To use this class you define functions that perform actions on
        the Textbox widget, then register them with self.register_key().

        **Example**, make F8 log the window contents:

        class MyTextbox(Textbox):
            def debug_key(y, x):
                logging.debug('Current window contents: %s', self.gather())

            def __init__(win, insert_mode=False):
                super().__init__(win, insert_mode)
                self.register_key(curses.KEY_F8, self.debug_key)
    """
    def __init__(self, win, insert_mode=False):
        super().__init__(win, insert_mode)
        self._commands = {}
        self.register_key(curses.KEY_BACKSPACE, self.del_left)         # BS
        self.register_key(curses.KEY_DOWN, self.move_down)             # Down
        self.register_key(curses.KEY_LEFT, self.move_left)             # Left
        self.register_key(curses.KEY_RIGHT, self.move_right)           # Right
        self.register_key(curses.KEY_UP, self.move_up)                 # Up
        self.register_key(curses.ascii.ACK, self.move_right)           # ^F
        self.register_key(curses.ascii.BEL, self.end)                  # ^G
        self.register_key(curses.ascii.BS, self.del_left)              # ^H
        self.register_key(curses.ascii.DLE, self.move_up)              # ^P
        self.register_key(curses.ascii.ENQ, self.end_of_line)          # ^E
        self.register_key(curses.ascii.EOT, self.delch)                # ^D
        self.register_key(curses.ascii.FF, self.refresh)           #     ^L
        self.register_key(curses.ascii.NL, self.newline)               # ^J
        self.register_key(curses.ascii.SOH, self.beginning_of_line)    # ^A
        self.register_key(curses.ascii.STX, self.move_left)            # ^P
        self.register_key(curses.ascii.VT, self.clear_to_end_of_line)  # ^K
        self.register_key(curses.ascii.SO, self.move_down)             # ^N
        self.register_key(curses.ascii.SI, self.insertln)              # ^O

    def register_key(self, key, callback):
        """Register a key as a command.

            :key:
                An integer describing the key that was pressed. You can find
                symbolic names for these keys in curses and curses.ascii.

            :callback:
                The callback that should be called. It will be called with
                the following signature:

                    callback(y, x)

                If you need to know what character was pressed you can check
                self.lastcmd.
        """
        self._commands[key] = callback

    def do_command(self, ch):
        """Process a single editing command.
        """
        (y, x) = self.win.getyx()
        self.lastcmd = ch

        if ch in self._commands:
            return self._commands[ch](y, x)

        if curses.ascii.isprint(ch):
            if y < self.maxy or x < self.maxx:
                self._insert_printable_char(ch)

        return 1

    def gather(self):
        """Collect and return the contents of the window.
        """
        result = super().gather()
        return result.strip() if self.stripspaces else result

    ## The remaining functions are callbacks that do_command calls.
    def beginning_of_line(self, y, x):
        """Move the cursor to the beginning of the line.
        """
        self.win.move(y, 0)
        return 1

    def move_left(self, y, x):
        """Move the cursor one character left.
        """
        if x > 0:
            self.win.move(y, x-1)
        elif y == 0:
            pass
        elif self.stripspaces:
            self.win.move(y-1, self._end_of_line(y-1))
        else:
            self.win.move(y-1, self.maxx)
        return 1

    def del_left(self, y, x):
        """Delete the character to the left of the cursor.
        """
        self.move_left(y, x)
        self.win.delch()
        return 1

    def end_of_line(self, y, x):
        """Move the cursor to the end of the line.
        """
        if self.stripspaces:
            self.win.move(y, self._end_of_line(y))
        else:
            self.win.move(y, self.maxx)
        return 1

    def move_right(self, y, x):
        """Move the cursor one character right.
        """
        if x < self.maxx:
            self.win.move(y, x+1)
        elif y == self.maxy:
            pass
        else:
            self.win.move(y+1, 0)
        return 1

    def end(self, y, x):
        """End text editing.
        """
        return 0

    def ignore(self, y, x):
        """Bind a key to do nothing.
        """
        return 1

    def newline(self, y, x):
        """Terminate if the window is 1 line, otherwise insert newline.
        """
        if self.maxy == 0:
            return 0
        elif y < self.maxy:
            self.win.move(y+1, 0)
        return 1

    def clear_to_end_of_line(self, y, x):
        """Delete from the cursor to the end of the line, or the whole line
        if blank.
        """
        if x == 0 and self._end_of_line(y) == 0:
            self.win.deleteln()
        else:
            # first undo the effect of self._end_of_line
            self.win.move(y, x)
            self.win.clrtoeol()
        return 1

    def move_down(self, y, x):
        if y < self.maxy:
            self.win.move(y+1, x)
            if x > self._end_of_line(y+1):
                self.win.move(y+1, self._end_of_line(y+1))
        return 1

    def move_up(self, y, x):
        """Move the cursor up one line.
        """
        if y > 0:
            self.win.move(y-1, x)
            if x > self._end_of_line(y-1):
                self.win.move(y-1, self._end_of_line(y-1))
        return 1

    def delch(self, y, x):
        """Delete the character under the cursor.
        """
        self.win.delch()
        return True

    def insertln(self, y, x):
        """Insert a newline.
        """
        self.win.insertln()
        return True

    def refresh(self, y, x):
        """Refresh the textbox.
        """
        self.win.refresh()
        return True


if __name__ == '__main__':
    def test_editbox(stdscr):
        ncols, nlines = 20, 2
        uly, ulx = 5, 10
        stdscr.addstr(uly-2, ulx, "Use Ctrl-G to end editing.")
        win = curses.newwin(nlines, ncols, uly, ulx)
        curses.textpad.rectangle(stdscr, uly-1, ulx-1, uly + nlines, ulx + ncols)
        stdscr.refresh()
        return Textbox(win, True).edit()

    contents = curses.wrapper(test_editbox)
    print('Contents of text box:', repr(contents))
