import csv, sys

raw = open(sys.argv[1])

md5dict = dict()
for md5 in csv.reader(raw):
    if md5dict.has_key(md5[1]):
        md5dict[md5[1]].append(md5[0])
    else:
        md5dict[md5[1]] = [md5[0]]

for key in md5dict:
    if len(md5dict[key]) > 1:
        print "\n".join(md5dict[key]), '\n'
