class CommandGroup:
    def __init__(self, initial_cmd, contents, close_cmd, parent=None):
        self.initial_cmd = initial_cmd
        self.contents = contents
        self.close_cmd = close_cmd
        self.parent = parent

        self.initial_cmd.parent = self
        self.contents.parent = self
        self.close_cmd.parent = self

    def mark_changed(self):
        self.changed = True
        if self.parent:
            self.parent.mark_changed()

    def get_variables(self):
        if self.parent:
            return self.parent.get_variables()
        return {}

    def __repr__(self):
        return str(self.initial_cmd) + str(self.contents) + str(self.close_cmd)
