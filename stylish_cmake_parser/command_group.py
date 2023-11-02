class CommandGroup:
    def __init__(self, initial_tag, contents, close_tag):
        self.initial_tag = initial_tag
        self.contents = contents
        self.close_tag = close_tag

    def __repr__(self):
        return str(self.initial_tag) + str(self.contents) + str(self.close_tag)
