from mcn.core.types import Meta


def gen_dotted(root, dotted=""):
    for k in sorted(root):
        field = k if not dotted else dotted + "." + k
        if isinstance(root[k], dict):
            for kk, vv in gen_dotted(root[k], field):
                yield kk, vv
        elif isinstance(root[k], Meta):
            for kk, vv in gen_dotted(dict(root[k]), field):
                yield kk, vv
        elif hasattr(root[k], "_asdict"):
            for kk, vv in gen_dotted(root[k]._asdict(), field):
                yield kk, vv
        else:
            yield field, root[k]


def to_dotted(data):
    return dict(gen_dotted(data))
