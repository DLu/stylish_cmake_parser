from .element import CMakeElement
from .section import Section


class Command(CMakeElement):
    FORCE_REGENERATION = False

    def __init__(self, command_name, parent=None):
        super().__init__(parent)
        self.command_name = command_name
        self.original = None
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
        self.mark_changed()

    def add(self, section):
        if section:
            self.sections.append(section)
            self.mark_changed()

    def first_token(self):
        for section in self.get_real_sections():
            if section.name:
                return section.name
            elif section.values:
                return section.values[0]
        return ''

    def remove_sections(self, key):
        bad_sections = self.get_sections(key)
        if not bad_sections:
            return
        self.mark_changed()
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
        self.mark_changed()

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
