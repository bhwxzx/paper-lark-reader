import sys

src = sys.argv[1]
dst = sys.argv[2]

with open(src, 'r', encoding='utf-8') as fs:
    content = fs.read()

with open(dst, 'a', encoding='utf-8') as fd:
    fd.write(content)
