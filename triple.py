#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re

def usage():
    print >> sys.stderr, 'Usage:'
    print >> sys.stderr, sys.argv[0], '<file.ll>'
    print >> sys.stderr, 'Author:\nWritten by Andrey Tretyakov (Intel, 2022)'
    sys.exit(1)

if len(sys.argv) != 2:
    print >> sys.stderr, 'Not enough parameters'
    usage()

r_triple = re.compile('(\s*target\s+triple\s*=\s*")(.*)(".*)')
r_field = re.compile('([A-Za-z_][A-Za-z0-9_]*)-(.*)')

ll = open(sys.argv[1], 'r')

for line in ll:
    mat = r_triple.match(line) # target triple = "*"
    if mat:
#        print line,
        t1 = mat.group(1)
        triple = mat.group(2)
        t2 = mat.group(3)
#        print triple
        cpu = triple
        vendor = 'unknown'
        os = 'unknown'
        mat = r_field.match(triple) # spir-*
        if mat:
            cpu = mat.group(1)
            vendor = mat.group(2)
#            print cpu, vendor
            mat = r_field.match(vendor) # unknown-*
            if mat:
                vendor = mat.group(1)
                os = mat.group(2)
#                print vendor, os
        if cpu == 'spir':
            cpu = 'spirv32'
        if cpu == 'spir64':
            cpu = 'spirv64'
        line = t1 + cpu + '-' + vendor + '-' + os + t2 + '\n'
#        print line,
    print line,

ll.close()
