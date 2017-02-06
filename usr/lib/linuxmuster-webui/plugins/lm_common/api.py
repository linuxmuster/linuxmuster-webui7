import os
import time


class CSVSpaceStripper:
    def __init__(self, file, encoding='utf-8'):
        self.f = file
        self.encoding = encoding

    def close(self):
        self.f.close()

    def __iter__(self):
        return self

    def next(self):
        return self.f.next().decode(self.encoding, errors='ignore').strip()


def lm_backup_file(path):
    if not os.path.exists(path):
        return

    dir, name = os.path.split(path)
    backups = sorted([x for x in os.listdir(dir) if x.startswith('.%s.bak.' % name)])
    while len(backups) > 4:
        os.unlink(os.path.join(dir, backups[0]))
        backups.pop(0)

    with open(dir + '/.' + name + '.bak.' + str(int(time.time())), 'w') as f:
        f.write(open(path).read())
