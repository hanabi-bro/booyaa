#!/usr/bin/env python

import sys


def err(t, s):
    sys.stderr.write('err {} "{}\n"'.format(t, s))
    sys.exit(1)


def get_kind(s):
    if s.startswith("- "):
        return "list"
    if ":" in s:
        return "dict"
    return "other"


cut_tail_spc = lambda s: cut_tail_spc(s[:-1]) if s[-1:] in (" ", "\t") else s
top_spc_num = lambda s: 1 + top_spc_num(s[1:]) if s[:1] == " " else 0


def get_idt_kind(s):
    idt = top_spc_num(s)
    return (idt, get_kind(s[idt:]))


def get_dict_v(idt, lines):
    s = lines[0]
    (idt_, kind_) = get_idt_kind(s)

    if kind_ == "dict":
        if idt_ == idt + 2:
            return get_dict(idt_, lines)
        elif idt_ > idt:
            err("indent", s)
    elif kind_ == "list":
        if idt_ == idt + 2 or idt_ == idt:
            return get_list(idt_, lines)
        elif idt_ > idt:
            err("indent", s)
    else:
        if idt_ == idt + 2:
            return get_other(idt_, lines)
        elif idt_ >= idt:
            err("indent", s)
    return None


def get_dict(idt, lines):
    s = lines.pop(0)[idt:]
    (k, v) = s.split(":")
    k = get_value(k.strip())
    v = get_value(v.strip())

    if not v:
        v = None
        if lines:
            v = get_dict_v(idt, lines)
    dic = {k: v}
    if lines:
        s = lines[0]
        (idt_, kind_) = get_idt_kind(s)
        if kind_ == "dict" and idt_ == idt:
            dic.update(get_dict(idt, lines))
    return dic


def get_list(idt, lines):
    idt_ = idt + 2
    kind_ = get_kind(lines[0][idt_:])
    v = get(idt_, kind_, lines)
    lst = [v]
    if lines:
        s = lines[0]
        (idt_, kind_) = get_idt_kind(s)
        if kind_ == "list" and idt_ == idt:
            lst += get_list(idt, lines)
    return lst


def get_value(s):
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass

    (h, t) = (s[:1], s[-1:])
    if h == t and h in ('"', "'"):
        s = s[1:-1]
    return s


def get_other(idt, lines):
    return get_value(lines.pop(0)[idt:])


def get(idt, kind, lines):
    if kind == "dict":
        return get_dict(idt, lines)
    if kind == "list":
        return get_list(idt, lines)
    return get_other(idt, lines)


def load(s):
    lines = s.strip().split("\n")
    lines = list(map(cut_tail_spc, lines))

    objs = []
    while lines:
        s = lines[0]
        (idt, kind) = get_idt_kind(s)
        obj = get(idt, kind, lines)
        objs.append(obj)

    return objs[0] if len(objs) == 1 else objs


###


def dump_dict(dic, idt):
    lines = []
    for (k, v) in dic.items():
        s = dump_other(k, idt) + ":"
        if type(v) == list:
            lines.append(s)
            s = dump_list(v, idt)
        elif type(v) == dict:
            lines.append(s)
            s = dump_dict(v, idt + 2)
        else:
            s += " " + dump_value(v)
        lines.append(s)
    return "\n".join(lines)


def dump_list(lst, idt):
    lines = []
    for obj in lst:
        s = dump_obj(obj, idt + 2)
        s = s[:idt] + "- " + s[idt + 2 :]
        lines.append(s)
    return "\n".join(lines)


def dump_value(obj):
    s = "{}".format(obj)
    if type(obj) == str and type(get_value(s)) != str:
        s = "'" + s + "'"
    return s


def dump_other(obj, idt):
    return (" " * idt) + dump_value(obj)


def dump_obj(obj, idt):
    t = type(obj)
    if t == dict:
        return dump_dict(obj, idt)
    if t == list:
        return dump_list(obj, idt)
    return dump_other(obj, idt)


def dump(obj):
    return dump_obj(obj, 0) + "\n"


if __name__ == "__main__":
    obj = load(sys.stdin.read())
    print("load obj\n{}".format(obj))

    s = dump(obj)
    print("dump\n{}".format(s))
# EOF
