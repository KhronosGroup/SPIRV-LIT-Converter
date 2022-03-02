#!/bin/bash

# replace this path with yours or/and fix other paths
[[ -z "$SPIRV_HOME" ]] && SPIRV_HOME=~/spirv

if [[ -z "$1" ]]; then
  echo "Usage:"
  echo "$0 <file.ll> [cl|spt|tri|tri.|strip|strip.|synt|synt.|llc|llc.|lit] [-cl] [-spt] [-tri] [-strip] [-synt] [-llc] [-lit]"
  echo 'Author:'
  echo 'Written by Andrey Tretyakov (Intel, 2022)'
  exit 1
fi

SDIR="$SPIRV_HOME/llvm-project" # Source Dir
DDIR="$SPIRV_HOME/LLVM-SPIRV-Backend" # Dest Dir
STEST="$SDIR/llvm/projects/SPIRV-LLVM-Translator/test"
DTEST="$DDIR/llvm/test/CodeGen/SPIRV"
SBIN="$SDIR/build/bin"
DBIN="$DDIR/build/bin"

# SLL - source .ll file with relative (to test dir) path
SLL=$1
# Relative path support (if not against test dir with scripts)
if [[ "$SLL" != /* ]]; then
  SLL=${SLL#./}
  SLL=${SLL#/}
  # combine full path with dest dir
  SLL="`pwd`/$SLL"
  # then remove prefix - dest dir
fi
SLL=${SLL#$STEST}
SLL=${SLL#$DTEST}
SLL=${SLL#./}
SLL=${SLL#/}
#echo "$SLL"

WD=`dirname "$0"`
cd "$WD"
WD=`pwd`

# Flags - stages/phases to execute
declare -A FLS
FLS=([cl]=1 [spt]=1 [tri]=1 [strip]=1 [synt]=1 [llc]=1 [lit]=1)
if [[ -n "$2" ]]; then
  shift
  # if first additional parameter after file name is switching on (rather than switching off, i.e. starting with '-')
  # then leave only some of phases and other switch off
  if [[ "$1" != -* ]]; then
    rm -f "${SLL%.*}.bak"* 2> /dev/null
    fl="$1"
    # if after phase is extra character (e.g. "tri."), strip it and remember to switch on next phases later
    [[ -z "${FLS[$fl]}" && -n "${FLS[${fl::-1}]}" ]] && fl="${fl::-1}" # with dot not present, but without is => strip dot
    FLS=([$fl]=1)
    if [[ "$fl" != "$1" ]]; then
      [[ "$fl" == "tri" ]] && FLS+=([strip]=1 [synt]=1 [llc]=1 [lit]=1)
      [[ "$fl" == "strip" ]] && FLS+=([synt]=1 [llc]=1 [lit]=1)
      [[ "$fl" == "synt" ]] && FLS+=([llc]=1 [lit]=1)
      [[ "$fl" == "llc" ]] && FLS+=([lit]=1)
    fi
    shift
  fi
  # switch off unwanted phases (preceded by '-', e.g. "-spt")
  for i in "$@"; do
    [[ "$i" == -* ]] && unset FLS[${i:1}] # =""
  done
fi
#for i in "${!FLS[@]}"; do printf "$i=${FLS[$i]} "; done
#echo "(${#FLS[@]})"

if [[ -n "${FLS[strip]}" ]]; then
  "$WD/strip.py" "$STEST/$SLL" > /dev/null || { EX=$? && echo "Unacceptable test $SLL" && exit $EX; }
fi

S1=`dirname "$SLL"`
#echo "$S1"         # relative path without test name
LL=`basename "$SLL"`
#echo "$LL"
if [[ -n "$S1" ]] && [[ ! -d "$DTEST/$S1" ]]; then
  mkdir -p "$DTEST/$S1" || exit $?
fi
cd "$DTEST/$S1" || exit $?
if [[ -n "${FLS[cl]}" || -n "${FLS[spt]}" || -n "${FLS[tri]}" ]]; then
  cp -p "$STEST/$SLL" . || exit $?
fi

if [[ "$LL" == *.cl ]] && [[ -n "${FLS[cl]}" || -n "${FLS[spt]}" || -n "${FLS[tri]}" || -n "${FLS[strip]}" || -n "${FLS[synt]}" || -n "${FLS[llc]}" ]]; then
  # not process this block, if phases are only "lit" ("cl" already processed on previous run)
  CL="$LL"
  L0="${LL/%.cl/.l0}"
  L1="${LL/%.cl/.l1}"
  LL="${LL/%.cl/.ll}"
  CLPAR=`$WD/cl_par.py "$CL"` || exit $?
  #echo "$CLPAR"
  "$SBIN/clang" -cc1 -nostdsysteminc "$CL" $CLPAR || exit $?
  "$WD/cl2ll.py" "$CL" > "$L0" || exit $?
  if [[ -n "${FLS[cl]}" ]]; then
    mv "$CL" "${CL}1" && "$WD/strip.py" "${CL}1" > "$CL" 2> /dev/null && rm "${CL}1" && mv "$CL" "${CL}1" && "$WD/synt.py" "${CL}1" > "$CL" ; rm "${CL}1"
    #rm "$CL" || exit $?
  fi
  cat "$L0" "$LL" > "$L1" || exit $?
  rm "$L0" "$LL" || exit $?
  mv "$L1" "$LL" || exit $?
fi

if [[ -n "${FLS[spt]}" ]]; then
  "$SBIN/llvm-as" "$LL" || exit $?
  BC="${LL/%.ll/.bc}"
  #echo "$BC"
  "$SBIN/llvm-spirv" -spirv-text "$BC" || exit $?
  rm "$BC" || exit $?
  #rm "${BC/%.bc/.spt}" || exit $?
fi

BAK="${LL/%.ll/.bak}"
if [[ -n "${FLS[tri]}" ]]; then
  [[ -f "$BAK" ]] && echo "$BAK already exists" && exit 3
  mv "$LL" "$BAK" || exit $?
  "$WD/triple.py" "$BAK" > "$LL" || exit $?
  #rm "$BAK" || exit $?
fi

if [[ -n "${FLS[llc]}" ]]; then
  "$DBIN/llc" -O0 "$LL" #|| exit $?
  EX_LLC=$?
  #rm "${LL/%.ll/.s}" || exit $?
fi

if [[ -n "${FLS[strip]}" ]]; then
  [[ -f "${BAK}1" ]] && echo "${BAK}1 already exists" && exit 3
  mv "$LL" "${BAK}1" || exit $?
  "$WD/strip.py" "${BAK}1" > "$LL" 2> /dev/null
  EX=$?
  [[ $EX != 0 ]] && rm "$LL" && mv "${BAK}1" "$LL" && exit $EX
  rm "${BAK}1" || exit $?
fi

if [[ -n "${FLS[synt]}" ]]; then
  mv "$LL" "${BAK}1" || exit $?
  "$WD/synt.py" "${BAK}1" > "$LL"
  EX=$?
  rm "${BAK}1" || exit $?
  [[ $EX != 0 ]] && exit $EX
fi

if [[ -n "${FLS[llc]}" ]]; then
  [[ $EX_LLC != 0 ]] && exit $EX_LLC
  "$DBIN/llc" -O0 "$LL" || exit $?
  #rm "${LL/%.ll/.s}" || exit $?
fi
if [[ -n "${FLS[lit]}" ]]; then
  "$DBIN/llvm-lit" -a "$LL" | less || exit $?
fi
