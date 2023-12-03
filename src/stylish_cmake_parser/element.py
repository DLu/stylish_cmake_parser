class CMakeElement:
    def __init__(self, parent=None):
        self.parent = parent
        self.changed = False

    def mark_changed(self):
        self.changed = True
        if self.parent:
            self.parent.mark_changed()

    def get_variables(self):
        if self.parent:
            return self.parent.get_variables()
        return {}
