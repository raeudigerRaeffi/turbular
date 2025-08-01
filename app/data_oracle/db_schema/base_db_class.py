class BaseDbObject:
    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))
