from vinegar.ast import Atom, Then, Else


class Result:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.value)


class Failure(Result):
    pass


class OK(Result):
    pass


def b_swap(stack, **kwargs):
    if len(stack) < 2:
        return Failure('underflow')
    n = stack[:]
    a = n[-1]
    n[-1] = n[-2]
    n[-2] = a
    return OK(n)


def b_dup(stack, **kwargs):
    if len(stack) < 1:
        return Failure('underflow')
    n = stack[:]
    n.append(n[-1])
    return OK(n)


def b_str(stack, ancillary_text=None):
    n = stack[:]
    n.append(ancillary_text)
    # TODO think of a contrived way in which this can fail
    return OK(n)


def b_int(stack, ancillary_text=None):
    try:
        n = stack[:]
        n.append(int(ancillary_text))
        return OK(n)
    except Exception as e:
        return Failure(str(e))


def b_eq(stack, **kwargs):
    if len(stack) < 2:
        return Failure('underflow')
    n = stack[:]
    b = n.pop()
    a = n.pop()
    if a == b:
        return OK(n)
    else:
        return Failure('unequal')


def b_gt(stack, **kwargs):
    if len(stack) < 2:
        return Failure('underflow')
    n = stack[:]
    b = n.pop()
    a = n.pop()
    if a > b:
        return OK(n)
    else:
        return Failure('not greater than')


def b_pop(stack, **kwargs):
    if len(stack) < 1:
        return Failure('underflow')
    n = stack[:]
    a = n.pop()
    return OK(n)


def b_mul(stack, **kwargs):
    if len(stack) < 2:
        return Failure('underflow')
    n = stack[:]
    a = n.pop()
    b = n.pop()
    n.append(b * a)
    return OK(n)


def b_sub(stack, **kwargs):
    if len(stack) < 2:
        return Failure('underflow')
    n = stack[:]
    a = n.pop()
    b = n.pop()
    n.append(b - a)
    return OK(n)


BUILTINS = {
    'swap': b_swap,
    'dup': b_dup,
    'str': b_str,
    'int': b_int,
    'eq!': b_eq,
    'gt!': b_gt,
    'pop': b_pop,
    'mul': b_mul,
    'sub': b_sub,
}


def interpret(definitions, stack, expr):
    # print('>>> {}'.format(expr))
    if isinstance(expr, Atom):
        entry = definitions[expr.word]
        if callable(entry):
            return entry(stack, ancillary_text=expr.ancillary_text)
        else:
            return interpret(definitions, stack, entry)
    elif isinstance(expr, Then):
        result = interpret(definitions, stack, expr.a)
        if isinstance(result, OK):
            stack = result.value
            return interpret(definitions, stack, expr.b)
        elif isinstance(result, Failure):
            return result
        else:
            raise NotImplementedError(result)
    elif isinstance(expr, Else):
        result = interpret(definitions, stack, expr.a)
        if isinstance(result, OK):
            return result
        elif isinstance(result, Failure):
            stack2 = stack[:]
            stack2.append(result)
            return interpret(definitions, stack2, expr.b)
        else:
            raise NotImplementedError(result)
    else:
        raise NotImplementedError('Expected atom or operation, got {}'.format(expr))
