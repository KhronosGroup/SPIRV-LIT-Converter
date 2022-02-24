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

r_run = re.compile('(\s*)(;|//)(\s*RUN\s*:)(.*)')
r_clang = re.compile('\s*%clang_cc1\s+(.*)')
r_triple_field = re.compile('([A-Za-z_][A-Za-z0-9_]*)-(.*)')
r_spirv = re.compile('\s*llvm-spirv\s+(.*)')
r_bc = re.compile('%t\S*\.bc')
r_spv = re.compile('%t\S*\.spv\S*')
r_filecheck = re.compile('\s*FileCheck\s+(.*)')

clang_params = ''
Spv_out = ''
Spv_ext = ''
Spt = ''
Checks_OK = []
Checks_NOT = []

ll = open(sys.argv[1], 'r')

for line in ll:
    prted = False
    mat = r_run.match(line) # ; RUN:*
    if mat:
#        print >> sys.stderr, line,
        cmd = mat.group(4)
#        print >> sys.stderr, cmd
        cmds = re.split('\|', cmd)
        for cmd in cmds:
#            print >> sys.stderr, cmd
            mat = r_clang.match(cmd) # %clang_cc1 *
            if mat:
                params = mat.group(1)
#                print >> sys.stderr, params
                clang_params = ' clang -cc1 -nostdsysteminc'
                Pars = params.split()
                tr = False
                tr_spir = ''
                tr_spirv = ''
                o = False
                for param in Pars:
#                    print >> sys.stderr, param
                    if tr:
                        tr = False
                        tr_spir = param
                        cpu = tr_spir
                        vendor = 'unknown'
                        os = 'unknown'
                        mat = r_triple_field.match(tr_spir) # spir-*
                        if mat:
                            cpu = mat.group(1)
                            vendor = mat.group(2)
#                            print cpu, vendor
                            mat = r_triple_field.match(vendor) # unknown-*
                            if mat:
                                vendor = mat.group(1)
                                os = mat.group(2)
#                                print vendor, os
                        if cpu == 'spir':
                            cpu = 'spirv32'
                        if cpu == 'spir64':
                            cpu = 'spirv64'
                        tr_spirv = cpu + '-' + vendor + '-' + os
                    if param == '-triple':
                        tr = True
                    if o:
                        o = False
                        param = '-'
                    if param == '-o':
                        o = True
                    if param == '-emit-llvm-bc':
                        param = '-emit-llvm'
                    clang_params += ' ' + param
                clang_params += ' | sed -Ee \'s#target triple = "' + tr_spir + '"#target triple = "' + tr_spirv + '"#\' |'
            mat = r_spirv.match(cmd) # llvm-spirv *
            if mat:
                params = mat.group(1)
#                print >> sys.stderr, params
                Pars = params.split()
                reverse = False
                spirv_text = False
                to_text = False
                text = False
                ext = False
                for param in Pars:
#                    print >> sys.stderr, param
                    if param == '-r':
                        reverse = True
                    if param.startswith('--'):
                        param = param[1:]
                    if param == '-to-binary':
                        reverse = True
                    if param.startswith('-spirv-ext='):
                        ext = True
                    if param == '-spirv-text':
                        spirv_text = True
                    if param == '-to-text':
                        to_text = True
                    if spirv_text or to_text:
                        text = True
#                if text and not reverse and not ext:
                if not reverse:
#                    print cmd
#                    if not ext:
#                        if text:
#                            print >> sys.stderr, line,
#                            prted = True
#                    else:
#                        print >> sys.stderr, ' !', line,
#                        prted = True
                    spv_in = ''
                    out = ''
                    o = False
                    def_file = ''
                    for param in Pars:
                        if o:
                            o = False
                            out = param
                            continue
                        if param == '-o':
                            o = True
                            continue
                        if param.startswith('--'):
                            param = param[1:]
                        if param == '-spirv-text' or param == '-to-text' or param.startswith('-spirv-ext='):
                            continue
                        mat = r_bc.match(param) # %t*.bc
                        if mat and not to_text:
                            def_file = param
                            continue
                        mat = r_spv.match(param) # %t*.spv*
                        if mat and to_text:
                            spv_in = param
                            def_file = param
                            continue
                        if param.startswith('-spirv-max-version=') or param == '-preserve-ocl-kernel-arg-type-metadata-through-string':
                            continue
                        if not text:
                            if param.startswith('-spirv-fp-contract=') or param == '-spirv-mem2reg' or param.startswith('-spirv-allow-unknown-intrinsics') or param == '-s' \
                               or param.startswith('-spirv-debug-info-version=') or param == '-spirv-allow-extra-diexpressions' or param.startswith('-spirv-replace-fmuladd-with-ocl-mad=') or param == '-spec-const-info':
                                continue
                        print >> sys.stderr, 'Warning: llvm-spirv: unknown option \'' + param + '\' in: ' + line,
#                    print >> sys.stderr, 'out = \'' + out + '\''
                    if def_file:
#                        print >> sys.stderr, def_file,
                        ridx = def_file.rfind('.')
                        if ridx > -1:
                            def_file = def_file[:ridx]
                        if text:
                            sp = '.spt'
                        else:
                            sp = '.spv'
                        def_file += sp
#                        print >> sys.stderr, def_file
                    if not text:
                        if out:
                            Spv_out = out
                        else:
                            Spv_out = def_file
                        if ext:
                            Spv_ext = Spv_out
                        else:
                            if Spv_ext == Spv_out:
                                Spv_ext = ''
                    if to_text and spv_in != Spv_out and spv_in != Spv_ext:
                        print >> sys.stderr, 'Warning: llvm-spirv: \'' + spv_in + '\' not matched (expected \'' + Spv_out + '\') in: ' + line,
                    if to_text and Spv_ext and spv_in == Spv_ext:
                        ext = True
                    if not ext:
                        if text:
                            print >> sys.stderr, line,
                            prted = True
#                    else:
#                        print >> sys.stderr, ' !', line,
#                        prted = True
                    if text and not ext:
                        if out:
                            Spt = out
                        else:
                            if def_file:
                                Spt = def_file
                            else:
                                Spt = '-'
#                        if Spt != '-':
#                            print >> sys.stderr, 'out = \'' + Spt + '\''
            else:
                mat = r_filecheck.match(cmd) # FileCheck *
                if mat:
                    params = mat.group(1)
#                    print >> sys.stderr, params
                    lt = False
                    matched = False
                    if Spt == '-':
                        Spt = ''
                        matched = True
                    nxt = False
                    prefix = ''
                    Pars = params.split()
                    for param in Pars:
#                        print >> sys.stderr, param
                        if lt:
                            lt = False
                            if param == Spt:
                                matched = True
                            continue
                        if nxt:
                            nxt = False
                            prefix = param
                            continue
                        if param.startswith('--'):
                            param = param[1:]
                        if param == '<' or param == '-input-file':
                            lt = True
                            continue
                        if Spt and (param == '<' + Spt or param == '-input-file=' + Spt):
                            matched = True
                            continue
                        if param.startswith('-input-file='):
                            # = param[12:]
                            continue
                        if param == '%s':
                            continue
                        if param == '-check-prefix' or param == '-check-prefixes':
                            nxt = True
                            continue
                        if param.startswith('-check-prefix='):
                            prefix = param[14:]
                            continue
                        if param.startswith('-check-prefixes='):
                            prefix = param[16:]
                            continue
                        print >> sys.stderr, 'Warning: FileCheck: unknown option \'' + param + '\' in: ' + line,
#                    print >> sys.stderr, prefix
                    if not prefix:
                        prefix = 'CHECK'
                    prefixes = re.split(',', prefix)
#                    print >> sys.stderr, prefixes
                    if matched:
                        if not prted:
                            print >> sys.stderr, line,
                            prted = True
#                        Checks_OK.extend(prefixes)
                        for p in prefixes:
                            if not p in Checks_OK:
                                Checks_OK += [p]
#                        print Checks_OK
#                        Checks_OK = []
#                        Spv_out = ''
#                        Spv_ext = ''
#                        Spt = ''
                    else:
#                        if not prted:
#                            print >> sys.stderr, ' !', line,
#                            prted = True
#                        Checks_NOT.extend(prefixes)
                        for p in prefixes:
                            if not p in Checks_NOT and not p in Checks_OK:
                                Checks_NOT += [p]
    if Spt == '-':
        Spt = ''

ll.close()

Checks_NOT = [x for x in Checks_NOT if not x in Checks_OK]

if len(Checks_OK) > 0:
    print >> sys.stderr, Checks_OK
    if len(Checks_NOT) > 0:
        print >> sys.stderr, ' !', Checks_NOT
else:
#if len(Checks_OK) == 0:
    sys.exit(2)


r_check = re.compile('(\s*)(;|//)(\s*)(.*)(\s*:\s*)(.*)')

replaced = False
# number of empty lines to remove (minimum of lines before and after block)
emp_bef = 0
emp_aft = 0
emp_bef_saved = 0

ll = open(sys.argv[1], 'r')

for line in ll:
    emp_bef0 = emp_bef # save old values (for previous line) of variables
    emp_aft0 = emp_aft
    emp_bef_saved0 = emp_bef_saved
    if line == '\n':
        emp_bef += 1 # space before block
        if emp_aft > 0: # was space and block to remove and now one more space
            emp_aft -= 1
            continue
    else:
        emp_bef = 0 # reset for any reason (will restore lately if needed)
        emp_aft = 0
        emp_bef_saved = 0
    mat = r_run.match(line) # ; RUN:*
    if mat:
#        print line,
        if not replaced:
            s = '%s '
            if clang_params:
                s = ''
            line = mat.group(1) + mat.group(2) + mat.group(3) + clang_params + ' llc -O0 ' + s + '-o - | FileCheck %s'
            replaced = True
            if not (len(Checks_OK) == 1 and Checks_OK[0] == 'CHECK'):
                line += ' --check-prefix'
                if len(Checks_OK) > 1:
                    line += 'es'
                line += '=' + ','.join(Checks_OK)
            line += '\n'
        else:
            continue
    else:
        mat = r_check.match(line) # ; CHECK*: *
        if mat:
            chk = mat.group(4)
#            print chk
            f_in = False
            for x in Checks_NOT:
                if chk.startswith(x):
                    f_in = True
                    break
            t_in = False
            for x in Checks_OK:
                if chk.startswith(x):
                    t_in = True
                    break
#            if chk in Checks_NOT and chk not in Checks_OK:
            if f_in and not t_in:
                emp_bef = emp_bef0 # restore reseted values
                emp_aft = emp_aft0
                emp_bef_saved = emp_bef_saved0
                if emp_bef != 0:
                    if emp_bef < emp_bef_saved: # was little space between two removed blocks
                        emp_bef = emp_bef_saved # restore previous value as if it was one single block
                    emp_aft = emp_bef # how many spaces were before block, so much spaces to remove after block (with itself)
                    emp_bef_saved = emp_bef # save for future use (when little space between two removed blocks)
                    emp_bef = 0
                continue
    print line,

ll.close()
