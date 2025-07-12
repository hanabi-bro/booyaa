from rich import print, pretty
import re
import yaml

pretty.install()


with open("new.conf", "r", encoding="utf-8-sig") as f:
    l = f.readlines()


re_indent_root = re.compile(r"^((config|end).*)$")
re_indent_config = re.compile(r"^(\s+)((config|edit) .*)$")
re_indent = re.compile(r"^(\s+)(\w.*)$")

re_cert = re.compile(r'(\s+)(set (private-key|certificate))( ".*)')
re_cert_end = re.compile(r'(.*")$')

str = ""

cert_flg = False
cert_indent = 0

for line in l:
    if cert_flg:
        if re_cert_end.match(line):
            str = str + ((" " * (cert_indent + 4)) + line)
            cert_flg = False
            continue
        else:
            str = str + ((" " * (cert_indent + 4)) + line)
            continue

    if re_cert.match(line):
        cert_flg = True
        cert_indent = len(line) - len(line.lstrip(" "))
        str = str + re_cert.sub(r"\1- \2: |\n\1   \4", line)
        continue

    if re_indent_root.match(line):
        str = str + re_indent_root.sub(r"- \1:", line)
    elif re_indent_config.match(line):
        str = str + re_indent_config.sub(r"\1- \2:", line)
    else:
        str = str + re_indent.sub(r"\1- \2", line)

str_obj = yaml.safe_load(str)
print(str_obj)

"""
def check_indent(line):
    return len(line) - len(line.lstrip(" "))


previous_indent = 0

for line in l:
    my_indent = check_indent(line)
    if previous_indent == my_indent:
        print("flat")
    elif previous_indent < my_indent:
        print("up")
    else:
        print("down")

    previous_indent = my_indent
"""


"""
cut_tail_spc = lambda s: cut_tail_spc(s[:-1]) if s[-1:] in (" ", "\t") else s

l = list(map(cut_tail_spc, l))


aa = l[0]
print(aa[:-1])

"""
