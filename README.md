# SPIRV-LIT-Converter
Scripts converting LIT tests from SPIRV-LLVM-Translator format to LLVM-SPIRV-Backend format

## Description / Introduction

This is a set of Python+Bash scripts for half-automated process of conversion lit tests from [SPIRV-LLVM-Translator's](https://github.com/KhronosGroup/SPIRV-LLVM-Translator) format
to [LLVM-SPIRV-Backend's](https://github.com/KhronosGroup/LLVM-SPIRV-Backend) one, i.e. for automatization and simplifying most routine operations.

It's not ideal nor perfect, because some transformations cannot be converted automatically (and several shouldn't be, for one or another reason), so:

    Note: After running scripts on a test, the resulting test should be checked, reviewed and fixed manually
    (if necessary).

Moreover, it's not full, i.e. does not contain every instruction from [SPIR-V's ISA](https://www.khronos.org/registry/SPIR-V/specs/unified1/SPIRV.html) nor every possible values of its parameters -
but only that ones, that occurred in accepted lit tests (i.e. tests that are present both in [SPIRV-LLVM-Translator's](https://github.com/KhronosGroup/SPIRV-LLVM-Translator/tree/master/test)
and [LLVM-SPIRV-Backend's](https://github.com/KhronosGroup/LLVM-SPIRV-Backend/tree/feature/spirv-backend-llvm14/llvm/test/CodeGen/SPIRV) repositories).

So, if new test is to be added with "new" instruction(s)/parameter(s), `synt.py` script should be extended. (See [Extension](#extension) below.)

## Details

Basically, to convert LLVM lit test from [SPIRV-LLVM-Translator's](https://github.com/KhronosGroup/SPIRV-LLVM-Translator) format to [LLVM-SPIRV-Backend's](https://github.com/KhronosGroup/LLVM-SPIRV-Backend),
following steps should be done (managed by main [`run.sh`](run.sh) script):

0. If source lit test is OpenCL (`.cl`), at first obtain lit test in LLVM (`.ll`) format:
    * 0.1. [`./cl_par.py`](cl_par.py) *test*.cl  
    --- get options to be passed to `clang`.
    * 0.2. `clang` -cc1 -nostdsysteminc -triple *spir* -cl-std=CL2.0 *...* -finclude-default-header -emit-llvm *test*.cl  
    --- compile source `.cl` file (using parameters obtained in previous step) and generate LLVM IR file (`.ll`).
        - *It's better to use `clang` built from [llvm-project/SPIRV-LLVM-Translator's](https://github.com/llvm/llvm-project) repository rather than from
        [LLVM-SPIRV-Backend's](https://github.com/KhronosGroup/LLVM-SPIRV-Backend) one due to better compliance of versions.*
    * 0.3. [`./cl2ll.py`](cl2ll.py) *test*.cl > *test.cl*.ll  
    --- make all OpenCL code as comments, convert all C-style comments (`//`) to LLVM-style (`;`) and remove `RUN: %clang_cc1` lit command.
    * 0.4. Combine two files *test*.ll and *test.cl*.ll, obtained in previous steps, into one *test*.ll.
1. [`./triple.py`](triple.py) *test.bak*.ll > *test.bak1*.ll  
--- change target triple from, e.g., `spir-unknown-unknown` to `spirv32-unknown-unknown`, or `spir64` to `spirv64-unknown-unknown` (without this it won't be compiled by `llc` ).
2. [`./strip.py`](strip.py) *test.bak1*.ll > *test.bak2*.ll  
--- search for `llvm-spirv -spirv-text`/`-to-text` and corresponding `FileCheck` "RUN" lit commands ("LLVM => SPIR-V" direction only, text format only, no extensions, etc),
replace all `RUN`s with single  
`RUN: llc -O0 %s -o - | FileCheck %s [...]`,  
collect list of "good" `FileCheck`'s prefixes (e.g. `CHECK` or `CHECK-SPIRV`),
which should be left in the test, and list of "bad" prefixes (e.g. `CHECK-LLVM`, `CHECK-SPV-IR`), and remove latter form the test,
because its won't be accepted by [`synt.py`](synt.py) in the next step.
    - *Note 1. [`strip.py`](strip.py) prints on stderr accepted `llvm-spirv`'s and `FileCheck`'s commands and "good" and "bad" lists (latter denoted with `' ! '`).
    If "good" list (accepted `FileCheck`'s prefixes) is empty, it returns non-zero exit code and empty stdout.*
    - *Note 2. In some rare cases, when prefix falls into both "good" and "bad" lists, or when prefix from one list starts with prefix from another
    (e.g. "good" `CHECK-SPIRV` and "bad" `CHECK-SPIRV-EXT` or `CHECK-SPV` and `CHECK-SPV-FPGA_REG`),
    [`strip.py`](strip.py) leaves these `FileCheck`'s prefixes in the test for the greater good. The resulting test should be reviewed more carefully and unwanted `FileCheck`'s commands removed manually (if decided).
    But usually [`strip.py`](strip.py) removes its automatically.
    This is not a bug, this is a feature. :-)*
3. [`./synt.py`](synt.py) *test.bak2*.ll > *test*.ll  
--- core conversion script --- process all remaining `FileCheck`'s commands, parse SPIR-V instructions, change its' syntax
(extract destination parameter (if any) and move it to left side of assignment) and format (add `%` to id parameters and convert literal parameters to corresponding  symbolic names, if necessary), etc.
    - *Note. [`synt.py`](synt.py) prints on stderr all `FileCheck`'s commands that it could not convert (not SPIR-V instruction or wrong format, new unknown SPIR-V instruction, etc...) and returns non-zero exit code,
    because this test highly likely won't be passed by `llvm-lit` in final step. Keep an eye on stderr to avoid following nuisances.*

Besides, for debugging purposes and convenience of comparison of source and target lit tests and corresponding SPIR-V codes, [`run.sh`](run.sh) executes following actions:

* `llvm-as` *test.bak*.ll  
--- *built from [llvm-project/SPIRV-LLVM-Translator's](https://github.com/llvm/llvm-project) repository* --- compile LLVM text IR to LLVM bitcode (`.bc`).
* `llvm-spirv` -spirv-text *test.bak*.bc  
--- *built from [SPIRV-LLVM-Translator's](https://github.com/KhronosGroup/SPIRV-LLVM-Translator) repository* --- convert LLVM bitcode to SPIR-V in an internal Translator's textual format (`.spt`, checked in source lit test).
* `llc` -O0 *test*.ll  
--- *built from [LLVM-SPIRV-Backend's](https://github.com/KhronosGroup/LLVM-SPIRV-Backend) repository* --- compile LLVM text IR (with converted lit commands and SPIR-V instructions) to SPIR-V assembler (`.s`, checked in target lit test).
* `llvm-lit` *-a* *test*.ll  
--- *built from [LLVM-SPIRV-Backend's](https://github.com/KhronosGroup/LLVM-SPIRV-Backend) repository* --- if all steps above completed successfully, finally run lit test.

Note. All *italicized* parameters/substrings above are given as examples and could vary.

## Prerequisites

Since [`run.sh`](run.sh) invokes many tools, in order to execute its, run and check test rather than simply blindly convert it, repositories should be not only checkout, but also built as well:

* For convenience put all SPIR-V things in one base directory, e.g. `~/spirv`:
```
mkdir ~/spirv && cd ~/spirv
```
* Checkout and build [SPIRV-LLVM-Translator](https://github.com/KhronosGroup/SPIRV-LLVM-Translator) as [LLVM in-tree build](https://github.com/KhronosGroup/SPIRV-LLVM-Translator#llvm-in-tree-build):
```
git clone https://github.com/llvm/llvm-project.git
cd llvm-project/llvm/projects
git clone https://github.com/KhronosGroup/SPIRV-LLVM-Translator.git
cd ../.. && mkdir build && cd build
cmake -G Ninja ../llvm -DLLVM_ENABLE_PROJECTS="clang"
# make llvm-spirv -j`nproc`
cmake --build . -- check-llvm-spirv
```
* Checkout and build [LLVM-SPIRV-Backend](https://github.com/KhronosGroup/LLVM-SPIRV-Backend)
(taken from [SPIR-V Backend's Build and Testing Instructions](https://github.com/KhronosGroup/LLVM-SPIRV-Backend/blob/master/llvm/docs/SPIR-V-Backend.rst)):
```
cd ~/spirv
git clone https://github.com/KhronosGroup/LLVM-SPIRV-Backend.git
cd LLVM-SPIRV-Backend && mkdir build && cd build
cmake -G Ninja -DLLVM_TARGETS_TO_BUILD="SPIRV" -DLLVM_ENABLE_PROJECTS="clang" ../llvm
cmake --build . -- FileCheck count llvm-as llvm-config llvm-dis not clang llc llvm-dwarfdump llvm-objdump llvm-readelf
cd ..
build/bin/llvm-lit llvm/test/CodeGen/SPIRV
```

(Note. If you have no `.cl` tests, you can exclude `clang` from `-DLLVM_ENABLE_PROJECTS` and `cmake --build` and use `clang` from
[llvm-project/SPIRV-LLVM-Translator's](https://github.com/llvm/llvm-project) repository.)

## Installing

Download [`triple.py`](triple.py), [`strip.py`](strip.py), [`synt.py`](synt.py), [`run.sh`](run.sh), [`cl_par.py`](cl_par.py), [`cl2ll.py`](cl2ll.py)
to [LLVM-SPIRV-Backend's](https://github.com/KhronosGroup/LLVM-SPIRV-Backend/tree/feature/spirv-backend-llvm14/llvm/test/CodeGen/SPIRV) test directory, for example.
*Or in some of it's subdirectories. Or in [SPIRV-LLVM-Translator's](https://github.com/KhronosGroup/SPIRV-LLVM-Translator/tree/master/test) test (sub)directory, if it is conveniently.
In general, scripts can be placed anywhere,* but its all should reside in the same directory.
*And outside of test directory relative test paths are not supported, so use full absolute file names in that case.
So, taking into account that its create new and modify `.ll` files,* the most convenient place for its is
[LLVM-SPIRV-Backend's](https://github.com/KhronosGroup/LLVM-SPIRV-Backend/tree/feature/spirv-backend-llvm14/llvm/test/CodeGen/SPIRV) test directory.
*In this case, relative short test names are supported as well.*

Open [`run.sh`](run.sh) in text editor and change `SPIRV_HOME`'s value in first line of code, if you place all your SPIR-V things in different directory rather than `~/spirv`
(alternatively, you can pass `SPIRV_HOME` environment variable before running [`run.sh`](run.sh)).
Also check other paths in heading of script and fix, if its don't match with yours.

## Running

Having changed working directory to [LLVM-SPIRV-Backend/llvm/test/CodeGen/SPIRV](https://github.com/KhronosGroup/LLVM-SPIRV-Backend/tree/feature/spirv-backend-llvm14/llvm/test/CodeGen/SPIRV)
and downloaded scripts here, simply type, for example:
```
./run.sh read_image.cl
```
or:
```
./run.sh transcoding/OpMin.ll
```
You can also specify full absolute path to test (source or target - no matter, it will be taken from [SPIRV-LLVM-Translator's](https://github.com/KhronosGroup/SPIRV-LLVM-Translator/tree/master/test)
test directory anyway):
```
./run.sh /home/user/spirv/llvm-project/llvm/projects/SPIRV-LLVM-Translator/test/transcoding/OpMin.ll
./run.sh /home/user/spirv/LLVM-SPIRV-Backend/llvm/test/CodeGen/SPIRV/transcoding/OpMin.ll
```
If your paths are different from default and you don't want to change `SPIRV_HOME` environment variable in [`run.sh`](run.sh) script, alternatively, you can pass it from command line, e.g:
```
SPIRV_HOME="/home/user/spirv" ./run.sh transcoding/OpMin.ll
```
If test didn't passed or `llvm-lit` didn't run at all and you get on stderr lines with ` ; CHECK...: ...` lit's commands (for e.g., as in `./run.sh simple.ll`),
you have to manually fix the test (e.g., by removing extra `CHECK`s that are not SPIR-V instructions) or extend [`synt.py`](synt.py) otherwise.

## Error codes

If any of invoked tools or scripts is failed, [`run.sh`](run.sh) returns corresponding error code.  
In addition, it returns `3` if `.bak` file for given test is detected (i.e., test is already processed, so, to convert test again simply delete that `.bak`);  
and `2` is also returned by [`strip.py`](strip.py) if test is unaccepted (only `CHECK`s for "SPIR-V => LLVM" direction, or some extension is used, etc).
In this case displaying the list of rejected `CHECK`s on stderr is turned off (for simplifying of generating the list of accepted only tests),
but this behavior can easily be changed by moving condition `if len(Checks_OK) ? 0:` to `sys.exit(2)` in [`strip.py`](strip.py) script.

## Extension

There is no single word to describe it. Some knowledge of [SPIR-V's ISA](https://www.khronos.org/registry/SPIR-V/specs/unified1/SPIRV.html),
[SPIRV-LLVM-Translator's](https://github.com/KhronosGroup/SPIRV-LLVM-Translator/tree/master/test) internal textual format,
how [LLVM-SPIRV-Backend's](https://github.com/KhronosGroup/LLVM-SPIRV-Backend/tree/feature/spirv-backend-llvm14/llvm/test/CodeGen/SPIRV) assembler should look like,
syntax of [llvm-lit's](https://llvm.org/docs/CommandGuide/FileCheck.html) `CHECK` commands
and of course understanding of implementation of [`synt.py`](synt.py) is required. So, it's better to ask the author to add new instruction(s).  
But in general, at first find this new instruction in [SPIR-V's ISA](https://www.khronos.org/registry/SPIR-V/specs/unified1/SPIRV.html) and figure out at which position it's
destination parameter is. There can be no destination at all (e.g., [OpBranch](https://www.khronos.org/registry/SPIR-V/specs/unified1/SPIRV.html#OpBranch)),
or at first parameter (mostly, various types, e.g., [OpTypeBool](https://www.khronos.org/registry/SPIR-V/specs/unified1/SPIRV.html#OpTypeBool))
or, most common case, at second parameter (e.g., [OpFAdd](https://www.khronos.org/registry/SPIR-V/specs/unified1/SPIRV.html#OpFAdd) - see underlined `Result <id>`).
Then add this instruction (without `Op` prefix) somewhere to `DEST0`, `DEST1` or `DEST2` list correspondingly at the beginning of [`synt.py`](synt.py) script.
If all of the parameters of instruction are `id`s (i.e., should be preceded with `%`, as in [OpFAdd](https://www.khronos.org/registry/SPIR-V/specs/unified1/SPIRV.html#OpFAdd)),
that's all - the work is done.  
Otherwise, an exception from common converting rule should be programmed for this instruction (or latter should be added to existing one).
For example, if instruction has `Literal` parameter(s) (e.g., [OpName](https://www.khronos.org/registry/SPIR-V/specs/unified1/SPIRV.html#OpName)), it should be added to
`LIT` map with specifying its position(s) (`n` counting from `1`, but starting next to destination `Result <id>` parameter) closer to the bottom of [`synt.py`](synt.py) script.
If parameter has "named" type (e.g., [Memory_Operands](https://www.khronos.org/registry/SPIR-V/specs/unified1/SPIRV.html#Memory_Operands) in [OpLoad](https://www.khronos.org/registry/SPIR-V/specs/unified1/SPIRV.html#OpLoad)),
then the instruction should be added to corresponding id_number-to-name map (existing, if any, or created new one). Moreover, additional care about possible parameter's values should be taken:
if there is no such value(s), it should be added too.

## Author

Idea, implementation, documentation, manual && (half-)automated conversion of tests:  
***Andrey Tretyakov*** for Intel, © late 2021-2022.
