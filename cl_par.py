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

r_run = re.compile('(\s*//\s*RUN\s*:)(.*)')
r_clang = re.compile('\s*%clang_cc1\s+(.*)')

ll = open(sys.argv[1], 'r')

for line in ll:
    mat = r_run.match(line) # // RUN:*
    if mat:
#        print line,
        cmd = mat.group(2)
#        print cmd
        mat = r_clang.match(cmd) # %clang_cc1 *
        if mat:
            params = mat.group(1)
#            print params
            Pars = params.split()
            o = False
            for param in Pars:
                if o:
                    o = False
                    continue
                if param == '-o':
                    o = True
                    continue
                if param == '%s':
                    continue
                if param == '-emit-llvm-bc':
                    param = '-emit-llvm'
                print param,

ll.close()
