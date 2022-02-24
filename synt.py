#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re

def usage():
    print >> sys.stderr, 'Usage:'
    print >> sys.stderr, sys.argv[0], '<file.ll>'
    print >> sys.stderr, 'Author:\nWritten by Andrey Tretyakov (Intel, 2022)'
    sys.exit(1)
ex = 0

if len(sys.argv) != 2:
    print >> sys.stderr, 'Not enough parameters'
    usage()

# no destination
DEST0 = [
 'Capability', 'MemoryModel', 'EntryPoint', 'ExecutionMode', 'Name', 'Decorate', 'MemberDecorate', 'Branch', 'BranchConditional', 'FunctionEnd', 'Return', 'ReturnValue',
 'Line', 'Store', 'Source', 'Extension', 'SourceExtension',
 'AssumeTrueKHR', 'AtomicFlagClear', 'AtomicStore', 'CaptureEventProfilingInfo', 'CommitReadPipe', 'CommitWritePipe', 'ControlBarrier', 'CopyMemorySized', 'DebugValue',#???
 'ImageWrite', 'LifetimeStart', 'LifetimeStop', 'LoopMerge', 'LinkageAttributes',#???
 'MemoryBarrier', 'Switch',
 'GroupCommitReadPipe', 'GroupCommitWritePipe', 'GroupWaitEvents',
 'ReleaseEvent', 'RetainEvent', 'SetUserEventStatus',
 'Unreachable',
]

# destination in 1-st parameter
DEST1 = [
 'ExtInstImport', 'TypeVoid', 'TypeBool', 'TypeInt', 'TypeFloat', 'TypeArray', 'TypeVector', 'TypePointer', 'TypeForwardPointer', 'TypeStruct', 'TypeFunction', 'TypePipe', 'TypePipeStorage',
 'TypeEvent', 'TypeOpaque', 'TypeImage', 'TypeSampledImage', 'TypeSampler', 'TypeDeviceEvent', 'TypeQueue', 'TypeReserveId', 'Type',#~pseudo
 'Label', 'String',
]

# destination in 2-nd parameter
DEST2 = [
 'Constant', 'ConstantComposite', 'ConstantTrue', 'ConstantFalse', 'ConstantNull', 'SpecConstant', 'SpecConstantComposite', 'ConstantSampler',
 'Variable',
 'Load',
 'All', 'Any', 'AtomicCompareExchange', 'AtomicCompareExchangeWeak', 'AtomicExchange', 'AtomicFlagTestAndSet', 'AtomicLoad',
 'AtomicIAdd', 'AtomicISub', 'AtomicAnd', 'AtomicOr', 'AtomicXor', 'AtomicSMax', 'AtomicSMin', 'AtomicUMax', 'AtomicUMin',
 'Bitcast', 'BitCount', 'BitReverse', 'BitwiseAnd', 'BitwiseOr', 'BitwiseXor', 'BuildNDRange',
 'CompositeExtract', 'CompositeInsert', 'ConstantPipeStorage',
 'ConvertSToF', 'ConvertFToS', 'ConvertUToF', 'ConvertFToU', 'ConvertPtrToU', 'ConvertUToPtr',
 'CreatePipeFromPipeStorage', 'CreateUserEvent', 'CrossWorkgroupCastToPtrINTEL', 'PtrCastToCrossWorkgroupINTEL',#???, ???
 'Dot',
 'EnqueueKernel', 'EnqueueMarker', 'ExpectKHR', 'ExtInst',
 'FConvert',
 'Function', 'FunctionParameter', 'FunctionCall',
 'FAdd', 'FSub', 'FMul', 'FDiv', 'FRem', 'FNegate',
   'FOrdEqual',   'FOrdNotEqual',   'FOrdGreaterThan',   'FOrdGreaterThanEqual',   'FOrdLessThan',   'FOrdLessThanEqual',
 'FUnordEqual', 'FUnordNotEqual', 'FUnordGreaterThan', 'FUnordGreaterThanEqual', 'FUnordLessThan', 'FUnordLessThanEqual',
 'FPGARegINTEL',
 'GenericCastToPtr', 'GenericCastToPtrExplicit', 'GenericPtrMemSemantics',
 'GetKernelNDrangeMaxSubGroupSize', 'GetKernelNDrangeSubGroupCount', 'GetKernelPreferredWorkGroupSizeMultiple', 'GetKernelWorkGroupSize',
 'GetMaxPipePackets', 'GetNumPipePackets',
 'GroupAll', 'GroupAny', 'GroupAsyncCopy', 'GroupBroadcast',
 'GroupNonUniformAll', 'GroupNonUniformAny',
 'GroupNonUniformBallot', 'GroupNonUniformBallotBitCount', 'GroupNonUniformBallotBitExtract', 'GroupNonUniformBallotFindLSB', 'GroupNonUniformBallotFindMSB',
 'GroupNonUniformBroadcastFirst', 'GroupNonUniformElect', 'GroupNonUniformInverseBallot',
 'GroupNonUniformAllEqual', 'GroupNonUniformBitwiseAnd', 'GroupNonUniformBitwiseOr', 'GroupNonUniformBitwiseXor', 'GroupNonUniformBroadcast',
 'GroupNonUniformIAdd', 'GroupNonUniformIMul', 'GroupNonUniformSMax', 'GroupNonUniformSMin', 'GroupNonUniformUMax', 'GroupNonUniformUMin',
 'GroupNonUniformFAdd', 'GroupNonUniformFMul', 'GroupNonUniformFMax', 'GroupNonUniformFMin',
 'GroupNonUniformLogicalAnd', 'GroupNonUniformLogicalOr', 'GroupNonUniformLogicalXor',
 'GroupNonUniformShuffle', 'GroupNonUniformShuffleUp', 'GroupNonUniformShuffleDown', 'GroupNonUniformShuffleXor',
 'GroupIAdd',
 'GroupFMax', 'GroupFMin', 'GroupFAdd',
 'GroupSMax', 'GroupSMin',
 'GroupUMax', 'GroupUMin',
 'GroupReserveReadPipePackets', 'GroupReserveWritePipePackets',
 'IAdd', 'ISub', 'IMul', 'IEqual', 'INotEqual',
 'SDiv',         'SGreaterThan', 'SGreaterThanEqual', 'SLessThan', 'SLessThanEqual',
 'UDiv', 'UMod', 'UGreaterThan', 'UGreaterThanEqual', 'ULessThan', 'ULessThanEqual',
 'IsFinite', 'IsInf', 'IsNan', 'IsNormal',
 'Ordered', 'Unordered',
 'ShiftLeftLogical', 'ShiftRightLogical',
 'ImageRead', 'ImageSampleExplicitLod', 'ImageQueryFormat', 'ImageQueryLevels', 'ImageQueryOrder', 'ImageQuerySizeLod', 'InBoundsPtrAccessChain',
 'IsValidEvent',
 'Phi',
 'PtrAccessChain', 'PtrCastToGeneric',
 'ReadPipe', 'WritePipe', 'ReserveReadPipePackets', 'ReserveWritePipePackets', 'ReservedReadPipe', 'ReservedWritePipe',
 'SRem', 'SampledImage', 'SatConvertSToU', 'SatConvertUToS', 'Select', 'SConvert', 'UConvert', 'SignBitSet', 'SpecConstantTrue', 'SpecConstantFalse', 'SpecConstantOp',
 'VectorExtractDynamic', 'VectorInsertDynamic', 'VectorShuffle', 'Undef',
]

DEST = DEST1 + DEST2
KNOWN = DEST0 + DEST

ADDRMODL = {
 '1': 'Physical32',
 '2': 'Physical64',
}
MEMMODL = {
 '0': 'Simple',
 '2': 'OpenCL',
}

EXECMODL = {
 '6': 'Kernel',
}

EXECMOD = {
 '17': 'LocalSize',
 '18': 'LocalSizeHint',
 '30': 'VecTypeHint',
 '31': 'ContractionOff',
 '33': 'Initializer',
 '34': 'Finalizer',
 '35': 'SubgroupSize',
 '36': 'SubgroupsPerWorkgroup',
 '4459': 'DenormPreserve',
 '4460': 'DenormFlushToZero',
 '4461': 'SignedZeroInfNanPreserve',
 '4462': 'RoundingModeRTE',
 '4463': 'RoundingModeRTZ',
}

SOURCE = {
 '0': 'Unknown',
 '3': 'OpenCL_C',
}

BUILTIN = {
 '24': 'NumWorkgroups',
 '25': 'WorkgroupSize',
 '26': 'WorkgroupId',
 '27': 'LocalInvocationId',
 '28': 'GlobalInvocationId',
 '29': 'LocalInvocationIndex',
 '30': 'WorkDim',
 '31': 'GlobalSize',
 '32': 'EnqueuedWorkgroupSize',
 '33': 'GlobalOffset',
 '34': 'GlobalLinearId',
 '36': 'SubgroupSize',
 '37': 'SubgroupMaxSize',
 '38': 'NumSubgroups',
 '39': 'NumEnqueuedSubgroups',
 '40': 'SubgroupId',
 '41': 'SubgroupLocalInvocationId',
 '4416': 'SubgroupEqMask',
 '4417': 'SubgroupGeMask',
 '4418': 'SubgroupGtMask',
 '4419': 'SubgroupLeMask',
 '4420': 'SubgroupLtMask',
}

FPARAT = {
 '6': 'NoWrite',
}
FPRM = {
 '0': 'RTE',
 '1': 'RTZ',
 '2': 'RTP',
 '3': 'RTN',
}
FPFMM = { # mask
 0: 'None',
 1: 'NotNaN',
 2: 'NotInf',
 4: 'NSZ',
 8: 'AllowRecip',
 0x10: 'Fast',
 0x10000: 'AllowContractFastINTEL',
 0x20000: 'AllowReassocINTEL',
}

FUNC = { # mask
 0: 'None',
 1: 'Inline',
 2: 'DontInline',
 4: 'Pure',
 8: 'Const',
}

STG = {
 '0': 'UniformConstant',
 '4': 'Workgroup',
 '5': 'CrossWorkgroup',
 '7': 'Function',
 '8': 'Generic',
 '5936': 'DeviceOnlyINTEL',
 '5937': 'HostOnlyINTEL',
}

MEM = { # mask
 0: 'None',
 1: 'Volatile',
 2: 'Aligned',
 4: 'Nontemporal',
}

DIM = {
 '0': '1D',
 '1': '2D',
 '2': '3D',
 '5': 'Buffer',
}
IFMT = {'0': 'Unknown'}
ACS = {
 '0': 'ReadOnly',
 '1': 'WriteOnly',
 '2': 'ReadWrite',
}

SAM = {
 '0': 'None',
 '3': 'Repeat',
}
SFM = {
 '0': 'Nearest',
 '1': 'Linear',
}

GRP = {
 '0': 'Reduce',
 '1': 'InclusiveScan',
 '2': 'ExclusiveScan',
 '3': 'ClusteredReduce',
}

IMOP = { # mask
 2: 'Lod',
 4: 'Grad',
 0x40: 'Sample',
}

LPCTL = { # mask
 1: 'Unroll',
 2: 'DontUnroll',
 0x100: 'PartialCount',
}

def masks(mp, mask):
    res = ''
    imask = int(mask)
    if imask == 0 and imask in mp.keys():
        res = mp[imask]
    for m in mp.keys():
        if m == 0:
            continue
        if imask & m == m:
            imask &= ~m
            if res:
                res += '|'
            res += mp[m]
    if imask != 0:
        print >> sys.stderr, 'Unknown mask:', imask
        return None
    return res


CHECKS = []

r_run = re.compile('\s*(;|//)\s*RUN\s*:(.*)')
r_filecheck = re.compile('\s*FileCheck\s+(.*)')

ll = open(sys.argv[1], 'r')

for line in ll:
    mat = r_run.match(line) # ; RUN:*
    if mat:
#        print >> sys.stderr, line,
        cmd = mat.group(2)
#        print >> sys.stderr, cmd
        cmds = re.split('\|', cmd)
        for cmd in cmds:
#            print >> sys.stderr, cmd
            mat = r_filecheck.match(cmd) # FileCheck *
            if mat:
                params = mat.group(1)
#                print >> sys.stderr, params
                nxt = False
                prefix = ''
                Pars = params.split()
                for param in Pars:
#                    print >> sys.stderr, param
                    if nxt:
                        nxt = False
                        prefix = param
                        continue
                    if param.startswith('--'):
                        param = param[1:]
                    if param == '-check-prefix' or param == '-check-prefixes':
                        nxt = True
                        continue
                    if param.startswith('-check-prefix='):
                        prefix = param[14:]
                        continue
                    if param.startswith('-check-prefixes='):
                        prefix = param[16:]
                        continue
#                print >> sys.stderr, prefix
                if not prefix:
                    prefix = 'CHECK'
                prefixes = re.split(',', prefix)
#                print >> sys.stderr, prefixes
                for p in prefixes:
                    if not p in CHECKS:
                        CHECKS += [p]

ll.close()

if len(CHECKS) == 0:
    CHECKS += ['CHECK']
#print >> sys.stderr, 'CHECKS =', CHECKS


#r_check = re.compile('(\s*)(;|//)(\s*' + CHECK + '.*:\s*)(.*)')
r_check = re.compile('(\s*)(;|//)(\s*)(\S+)(\s*:\s*)(.*)')
r_sz = re.compile('[0-9]+\s+(.*)')
r_szs = re.compile('{{\[0-9\](\+|\*)}}\s+(.*)')
r_opcode = re.compile('([A-Za-z_][A-Za-z0-9_]*)(.*)')
r_lspace = re.compile('(\s*)(.*)')
r_param0 = re.compile('(\S+)(.*)')
r_param = re.compile('(\S+\s*)(.*)')
r_rspace = re.compile('\S+(\s*)')
r_params_only = re.compile('(\[\[\S+\]\]\s*)+$')

ll = open(sys.argv[1], 'r')

def is_check(s):
    if s == 'RUN':
        return False
    for x in CHECKS:
        if s.startswith(x):
            return True
    return False

c_line = 0
for line in ll:
    c_line += 1
    mat = r_check.match(line) # ; *: *
    if mat and is_check(mat.group(4)):
#        print line,
        chk = mat.group(1) + mat.group(2) + mat.group(3) + mat.group(4) + mat.group(5)
        insn = mat.group(6)
        # remove number before OpCode
        mat = r_sz.match(insn) # NN *
        if mat:
            insn = mat.group(1)
        else:
            mat = r_szs.match(insn) # {{[0-9]+}} *
            if mat:
                insn = mat.group(2)
        mat = r_opcode.match(insn) # Code*
        if mat:
            opcode = mat.group(1) # no spaces
            sp1 = ''
            params = mat.group(2)
            dest = '' # [will be] space from right

            # if DEST in 2-nd param ("DEST2"), split 1-st ("param0") and reduce do case where DEST in 1-st param ("DEST1")
            sp0 = ''
            param0 = '' # no spaces
            if opcode in DEST2:
                # remove leading whitespaces before parameters
                mat = r_lspace.match(params) # " params"
                if mat:
                    sp0 = mat.group(1)
                    params = mat.group(2) # no left space
                    mat = r_param0.match(params) # PARAM0*
                    if mat:
                        param0 = mat.group(1)
                        params = mat.group(2)

            # remove leading whitespaces before parameters
            mat = r_lspace.match(params) # " params"
            if mat:
                sp1 = mat.group(1)
                params = mat.group(2) # no left space
            if opcode in DEST:
                mat = r_param.match(params) # DEST *
                if mat:
                    dest = mat.group(1)
                    params = mat.group(2)
                    if not params:
                        dest += sp1
                        sp1 = ''
                    dest = '%' + dest + '= '
            # synthesize back again
            if opcode in KNOWN:
                if param0:
                    param0 = '%' + param0

                # iterate through all rest parameters and add '%' to it (if neccessary)
                pparams = ''
                prev_par = ''
                n = 0 # number of parameter, not counting param0 and dest.
                while params:
                    mat = r_param.match(params) # PARAM *
                    if mat:
                        n += 1 # n == 1 is next after dest.
                        pparam = mat.group(1)
                        params = mat.group(2)
                        rsp = ''
                        mat = r_rspace.match(pparam) # PARAM 
                        if mat:
                            rsp = mat.group(1)
                            pparam = pparam.strip()
                        LIT = {}
                        MAP = None
                        if ( # exeptions from adding '%'
                            opcode == 'Capability' or
                            opcode == 'ExtInstImport' or
                            opcode == 'EntryPoint' and n != 2 or
                            opcode == 'ExecutionMode' and n != 1 or
                            opcode == 'Source' and (n == 2 or n == 4) or
                            opcode == 'Extension' or opcode == 'SourceExtension' or
                            opcode == 'Name' and n == 2 or
                            opcode == 'Decorate' and n > 1 or
                            opcode == 'MemberDecorate' and n > 1 or
                            opcode == 'TypeInt' or opcode == 'TypeFloat' or
                            opcode == 'TypeVector' and n > 1 or
                            opcode == 'TypeOpaque' or
                            opcode == 'TypeImage' and n > 1 or
                            opcode == 'Constant' or opcode == 'SpecConstant' or
                            opcode == 'Function' and n == 1 or
                            opcode == 'BranchConditional' and n > 3 or
                            opcode == 'ExtInst' and n == 2 or
                            opcode == 'Line' and n > 1 or
                            opcode == 'Load' and n > 1 or
                            opcode == 'Store' and n > 2 or
                            opcode == 'String' or
                            opcode == 'Switch' and n > 2 and n % 2 == 1 or
                            opcode == 'CompositeExtract' and n > 1 or
                            opcode == 'CompositeInsert' and n > 2 or
                            opcode == 'ConstantPipeStorage' or
                            (opcode == 'LifetimeStart' or opcode == 'LifetimeStop') and n == 2 or
                            opcode == 'LinkageAttributes' or
                            opcode == 'SpecConstantOp' and n == 1 or
                            opcode == 'VectorShuffle' and n > 2 or
                            False
                            ):
                            MAP = LIT
                        if opcode == 'MemoryModel':
                            if n == 1:
                                MAP = ADDRMODL
                            if n == 2:
                                MAP = MEMMODL
                        if opcode == 'EntryPoint' and n == 1:
                            MAP = EXECMODL
                        if opcode == 'ExecutionMode' and n == 2:
                            MAP = EXECMOD
                        if opcode == 'Source' and n == 1:
                            MAP = SOURCE
                        if opcode == 'Decorate' and n == 3:
                            if prev_par == 'BuiltIn':
                                MAP = BUILTIN
                            if prev_par == 'FuncParamAttr':
                                MAP = FPARAT
                            if prev_par == 'FPRoundingMode':
                                MAP = FPRM
                            if prev_par == 'FPFastMathMode':
                                MAP = FPFMM
                        if opcode == 'Function' and n == 1:
                            MAP = FUNC
                        if (opcode == 'TypePointer' or opcode == 'TypeForwardPointer' or opcode == 'Variable') and n == 1 or opcode == 'GenericCastToPtrExplicit' and n == 2:
                            MAP = STG
                        if (opcode == 'Load' and n == 2 or opcode == 'Store' and n == 3 or opcode == 'CopyMemorySized' and n > 3):
                            MAP = MEM
                        if opcode == 'TypePipe' and n == 1:
                            MAP = ACS
                        if opcode == 'TypeImage':
                            if n == 2:
                                MAP = DIM
                            if n == 7:
                                MAP = IFMT
                            if n == 8:
                                MAP = ACS
                        if opcode == 'ConstantSampler':
                            if n == 1:
                                MAP = SAM
                            if n == 2:
                                MAP = LIT
                            if n == 3:
                                MAP = SFM
                        if (opcode == 'GroupNonUniformBitwiseAnd' or opcode == 'GroupNonUniformBitwiseOr' or opcode == 'GroupNonUniformBitwiseXor'
                            or opcode == 'GroupNonUniformBallotBitCount'
                            or opcode == 'GroupNonUniformIAdd' or opcode == 'GroupNonUniformIMul' or opcode == 'GroupIAdd'
                            or opcode == 'GroupNonUniformSMax' or opcode == 'GroupNonUniformSMin' or opcode == 'GroupNonUniformUMax' or opcode == 'GroupNonUniformUMin'
                            or opcode == 'GroupNonUniformFAdd' or opcode == 'GroupNonUniformFMul' or opcode == 'GroupNonUniformFMax' or opcode == 'GroupNonUniformFMin'
                            or opcode == 'GroupNonUniformLogicalAnd' or opcode == 'GroupNonUniformLogicalOr' or opcode == 'GroupNonUniformLogicalXor'
                            or opcode == 'GroupFMax' or opcode == 'GroupFMin' or opcode == 'GroupFAdd'
                            or opcode == 'GroupSMax' or opcode == 'GroupSMin' or opcode == 'GroupUMax' or opcode == 'GroupUMin') and n == 2:
                            MAP = GRP
                        if (opcode == 'ImageRead' and n == 3 or opcode == 'ImageSampleExplicitLod' and n == 3 or opcode == 'ImageWrite' and n == 4):
                            MAP = IMOP
                        if opcode == 'LoopMerge':
                            if n == 3:
                                MAP = LPCTL
                            if n > 3:
                                MAP = LIT
                        if MAP == MEM and 'Aligned' in prev_par:
                            MAP = LIT

                        if MAP == None: # not an exception
                            pparam = '%' + pparam
                        else:
                            if MAP != LIT:
                                if pparam == '{{[0-9]+}}' or pparam == '{{[0-9]*}}':
                                    pparam = '{{.*}}'
                                if pparam != '{{.*}}':
                                    if MAP == FPFMM or MAP == FUNC or MAP == MEM or MAP == IMOP or MAP == LPCTL:
                                        res = masks(MAP, pparam)
                                        if res != None:
                                            pparam = res
                                        else:
                                            print >> sys.stderr, '%d: %s:' % (c_line, opcode), line,
                                            ex = 1
                                    else:
                                        if pparam in MAP:
                                            pparam = MAP[pparam]
                                        else:
                                            print >> sys.stderr, '%d: %s: unknown key %s:' % (c_line, opcode, pparam), line,
                                            ex = 1
                        pparams += pparam + rsp
                        prev_par = pparam
                    else:
                        print >> sys.stderr, 'Some error has happened during iteration of parameters (%s):\n%d:' % (params, c_line), line
                        break

                # add 'Op' to OpCode
                opcode = 'Op' + opcode
                insn = dest + opcode + sp0 + param0 + sp1 + pparams
            else:
                print >> sys.stderr, '%d: %s:' % (c_line, opcode), line,
                ex = 1
        else:
            #experimental; could be commented out
            mat = r_params_only.match(insn) # [[param1]] [[param2]] ...
            if mat:
                params = insn
                # iterate through all parameters and add '%' to it
                pparams = ''
                while params:
                    mat = r_param.match(params) # PARAM *
                    if mat:
                        pparam = '%' + mat.group(1)
                        params = mat.group(2)
                        pparams += pparam
                insn = pparams
            else: # end of experimental
                print >> sys.stderr, '%d:' % c_line, line,
                ex = 1
        line = chk + insn + '\n'
#        print line
    print line,

ll.close()

if ex != 0:
    sys.exit(ex)
