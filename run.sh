#!/bin/bash

# replace this path with yours or/and fix other paths
[[ -z "$SPIRV_HOME" ]] && SPIRV_HOME=~/spirv

if [[ -z "$1" ]]; then
  echo "Usage:"
  echo "$0 <file.ll>"
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

"$WD/strip.py" "$STEST/$SLL" > /dev/null || { EX=$? && echo "Unacceptable test $SLL" && exit $EX; }

S1=`dirname "$SLL"`
#echo "$S1"         # relative path without test name
LL=`basename "$SLL"`
#echo "$LL"
if [[ -n "$S1" ]] && [[ ! -d "$DTEST/$S1" ]]; then
  mkdir -p "$DTEST/$S1" || exit $?
fi
cd "$DTEST/$S1" || exit $?
cp -p "$STEST/$SLL" . || exit $?

if [[ "$LL" == *.cl ]]; then
  CL="$LL"
  L0="${LL/%.cl/.l0}"
  L1="${LL/%.cl/.l1}"
  LL="${LL/%.cl/.ll}"
  CLPAR=`$WD/cl_par.py "$CL"` || exit $?
#  echo "$CLPAR"
  "$SBIN/clang" -cc1 -nostdsysteminc "$CL" $CLPAR || exit $?
  "$WD/cl2ll.py" "$CL" > "$L0" || exit $?
  mv "$CL" "${CL}1" && "$WD/strip.py" "${CL}1" > "$CL" 2> /dev/null && rm "${CL}1" && mv "$CL" "${CL}1" && "$WD/synt.py" "${CL}1" > "$CL" ; rm "${CL}1"
#  rm "$CL" || exit $?
  cat "$L0" "$LL" > "$L1" || exit $?
  rm "$L0" "$LL" || exit $?
  mv "$L1" "$LL" || exit $?
fi

"$SBIN/llvm-as" "$LL" || exit $?
BC="${LL/%.ll/.bc}"
#echo "$BC"
"$SBIN/llvm-spirv" -spirv-text "$BC" || exit $?
rm "$BC" || exit $?
#rm "${BC/%.bc/.spt}" || exit $?

BAK="${LL/%.ll/.bak}"
[[ -f "$BAK" ]] && echo "$BAK already exists" && exit 3
mv "$LL" "$BAK" || exit $?
"$WD/triple.py" "$BAK" > "$LL" || exit $?
#rm "$BAK" || exit $?

"$DBIN/llc" -O0 "$LL" #|| exit $?
EX_LLC=$?
#rm "${LL/%.ll/.s}" || exit $?

[[ -f "${BAK}1" ]] && "${BAK}1 already exists" && exit 3
mv "$LL" "${BAK}1" || exit $?
"$WD/strip.py" "${BAK}1" > "$LL" 2> /dev/null
EX=$?
[[ $EX != 0 ]] && rm "$LL" && mv "${BAK}1" "$LL" && exit $EX
rm "${BAK}1" || exit $?

mv "$LL" "${BAK}1" || exit $?
"$WD/synt.py" "${BAK}1" > "$LL"
EX=$?
rm "${BAK}1" || exit $?
[[ $EX != 0 ]] && exit $EX

[[ $EX_LLC != 0 ]] && exit $EX_LLC
"$DBIN/llc" -O0 "$LL" || exit $?
#rm "${LL/%.ll/.s}" || exit $?
"$DBIN/llvm-lit" -a "$LL" | less || exit $?
