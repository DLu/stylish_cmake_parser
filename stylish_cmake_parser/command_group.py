class CommandGroup:
    def __init__(self, initial_cmd, contents, close_cmd):
        self.initial_cmd = initial_cmd
        self.contents = contents
        self.close_cmd = close_cmd

    def __repr__(self):
        return str(self.initial_cmd) + str(self.contents) + str(self.close_cmd)
