from random import choice

class Schema:
    _base = object

    @classmethod
    def sample(self):
        attrs = [attr for attr in vars(self) if attr[0] != '_']
        initvars = {}
        for attr in attrs:
            val = choice( list( getattr(self, attr) ) )

            if attr == 'cp':
                val = max([180, val])
            
            initvars[attr] = val
        c = self._base(**initvars)
        return c

    @classmethod
    def normalize(self, attr: str = None, val: int = None):
        attr = getattr(self, attr)
        upper = attr.stop
        if attr.start:
            val -= attr.start
            upper -= attr.start
        normVal = val / upper
        normVal *= 2
        normVal -= 1
        return normVal


from . import state
from . import player
from . import recipe
from . import action
from . import trait
from . import environment
from . import observation
from . import gear