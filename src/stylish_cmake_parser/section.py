class SectionStyle:
    def __init__(self, prename='', name_val_sep=' ', val_sep=' '):
        self.prename = prename
        self.name_val_sep = name_val_sep
        self.val_sep = val_sep

    def __repr__(self):
        return f'SectionStyle({repr(self.prename)}, {repr(self.name_val_sep)}, {repr(self.val_sep)})'


class Section:
    def __init__(self, name='', values=None, style=None, parent=None):
        self.name = name
        self.parent = parent
        if values is None:
            self.values = []
        else:
            self.values = list(values)
        if style:
            self.style = style
        else:
            self.style = SectionStyle()

    def add(self, v):
        self.values.append(v)

    def add_values(self, new_values, alpha_order=True):
        """Add the new_values to the values.

        If alpha_order is true AND the existing values are already alphabetized,
        add the new values in alphabetical order.
        """
        # Check if existing values are sorted
        if alpha_order and self.values == sorted(self.values):
            all_values = self.values + list(new_values)
            self.values = sorted(all_values)
        else:
            self.values += sorted(new_values)

    def is_valid(self):
        return len(self.name) > 0 or len(self.values) > 0

    def mark_changed(self):
        if self.parent:
            self.parent.changed = True

    def __repr__(self):
        s = self.style.prename
        if len(self.name) > 0:
            s += self.name
            if len(self.values) > 0 or '\n' in self.style.name_val_sep:
                s += self.style.name_val_sep
        s += self.style.val_sep.join(self.values)
        return s
