import six
from six.moves import xrange as range


class IntegerRange:
    def __init__(self, includes, excludes):
        self.includes = set(includes)
        self.excludes = set(excludes)

    @classmethod
    def parse(cls, atoms):
        includes = set()
        excludes = set()
        for atom in atoms:
            if isinstance(atom, int):
                includes.add((atom,))
                continue
            if isinstance(atom, six.string_types):
                if atom[0] == '!':
                    negate = True
                    atom = atom[1:]
                else:
                    negate = False
                target = (excludes if negate else includes)
                atom = atom.lstrip('#')
                if atom.isdigit():
                    target.add((int(atom),))
                    continue
                elif '-' in atom:
                    start, end = map(int, atom.split('-', 1))
                    target.add(range(start, end + 1))
                    continue
            raise ValueError('Not a valid range atom: %s' % atom)  # pragma: no cover
        return cls(includes=includes, excludes=excludes)

    def as_set(self):
        values = set()
        for inc in self.includes:
            values |= set(inc)
        for exc in self.excludes:
            values -= set(exc)
        return values
