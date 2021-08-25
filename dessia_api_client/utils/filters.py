

class Filter:
    def __init__(self, attribute, operator, value):
        self.attribute = attribute
        self.operator = operator
        self.value = value

    def to_param(self):
        return {'{}[{}]'.format(self.attribute, self.operator): self.value}


class EqualityFilter(Filter):
    def __init__(self, attribute, value):
        Filter.__init__(self, attribute, 'eq', value)


class LowerFilter(Filter):
    def __init__(self, attribute, value):
        Filter.__init__(self, attribute, 'lt', value)


class LowerOrEqualFilter(Filter):
    def __init__(self, attribute, value):
        Filter.__init__(self, attribute, 'lte', value)


class GreaterFilter(Filter):
    def __init__(self, attribute, value):
        Filter.__init__(self, attribute, 'gt', value)


class GreaterOrEqualFilter(Filter):
    def __init__(self, attribute, value):
        Filter.__init__(self, attribute, 'gte', value)


class InFilter(Filter):
    def __init__(self, attribute, values):
        Filter.__init__(self, attribute, 'in', values)
