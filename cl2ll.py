#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re

def usage():
    print >> sys.stderr, 'Usage:'
    print >> sys.stderr, sys.argv[0], '<file.cl>'
    print >> sys.stderr, 'Author:\nWritten by Andrey Tretyakov (Intel, 2022)'
    sys.exit(1)

if len(sys.argv) != 2:
    print >> sys.stderr, 'Not enough parameters'
    usage()

r_comm = re.compile('(\s*)//(.*)')
r_run = re.compile('\s*RUN\s*:(.*)')
r_clang = re.compile('\s*%clang_cc1\s+.*')

ll = open(sys.argv[1], 'r')

for line in ll:
    if line != '\n':
        mat = r_comm.match(line) # //*
        if mat:
            comm = mat.group(2)
            line = mat.group(1) + ';' + comm + '\n'
            mat = r_run.match(comm) # RUN:*
            if mat:
                cmd = mat.group(1)
#                print cmd
                mat = r_clang.match(cmd) # %clang_cc1 *
                if mat:
                    continue
        else:
            line = '; ' + line
    print line,

ll.close()
