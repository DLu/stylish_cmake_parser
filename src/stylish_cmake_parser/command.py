from .section import Section


class Command:
    FORCE_REGENERATION = False

    def __init__(self, command_name):
        self.command_name = command_name
        self.original = None
        self.changed = False
        self.pre_paren = ''
        self.sections = []

    def get_real_sections(self):
        return [s for s in self.sections if not isinstance(s, str)]

    def get_section(self, key):
        for s in self.get_real_sections():
            if s.name == key:
                return s

    def get_sections(self, key):
        return [s for s in self.get_real_sections() if s.name == key]

    def add_section(self, key, values=None, style=None):
        self.sections.append(Section(key, values, style, self))
        self.changed = True

    def add(self, section):
        if section:
            self.sections.append(section)
            self.changed = True

    def first_token(self):
        return self.get_real_sections()[0].values[0]

    def remove_sections(self, key):
        bad_sections = self.get_sections(key)
        if not bad_sections:
            return
        self.changed = True
        self.sections = [section for section in self.sections if section not in bad_sections]
        if len(self.sections) == 1 and isinstance(self.sections[0], str):
            self.sections = []

    def get_tokens(self, include_name=False):
        tokens = []
        for section in self.get_real_sections():
            if include_name and section.name:
                tokens.append(section.name)
            tokens += section.values
        return tokens

    def add_token(self, s):
        sections = self.get_real_sections()
        if len(sections) == 0:
            self.add(Section(values=[s], parent=self))
        else:
            last = sections[-1]
            last.values.append(s)
        self.changed = True

    def __repr__(self):
        if self.original and not self.changed and not Command.FORCE_REGENERATION:
            return self.original

        s = self.command_name + self.pre_paren + '('
        for section in map(str, self.sections):
            if s[-1] not in '( \n' and section[0] not in ' \n':
                s += ' '
            s += section
        if '\n' in s and s[-1] != '\n':
            s += '\n'
        s += ')'
        return s
