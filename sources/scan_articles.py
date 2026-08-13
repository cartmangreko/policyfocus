import re, sys
fname = sys.argv[1]
t = open(fname, encoding='utf-8').read()
for m in re.finditer(r'^Article \d+$', t, re.M):
    print(m.start(), t[m.start():m.start()+25].replace(chr(10), ' | '))
print("TOTAL CHARS:", len(t))
