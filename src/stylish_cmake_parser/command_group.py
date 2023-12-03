from .element import CMakeElement


class CommandGroup(CMakeElement):
    def __init__(self, initial_cmd, contents, close_cmd, parent=None):
        super().__init__(parent)
        self.initial_cmd = initial_cmd
        self.contents = contents
        self.close_cmd = close_cmd
        self.parent = parent

        self.initial_cmd.parent = self
        self.contents.parent = self
        self.close_cmd.parent = self

    def __repr__(self):
        return str(self.initial_cmd) + str(self.contents) + str(self.close_cmd)
