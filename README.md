# assembler
I wrote a single-pass MIPS assembler.


It supports the following MIPS instructions:

  - `add`

  - `addi`

  - `sub`

  - `and`

  - `andi`

  - `or`

  - `ori`

  - `xor`

  - `xori`

  - `nor`

  - `sll`

  - `sra`

  - `srl`

  - `slt`

  - `slti`

  - `beq`

  - `bne`

  - `j`

  - `jal`

  - `jr`

  - `lw`

  - `sw`

  - `nop`

For example, given the following input

    loop: add  $s0,   $s1,    $s2        # $s0 = $s1 + $s2
          lw   $t4,   0($s0)
          lw   $t3,   0($s1)
          bne  $t3,   $t4,    loop
          addi $s0,   $s0,    1          # $0++

my assembler outputs the following machine code:

    02328020
    8e0c0000
    8e2b0000
    156cfffc
    22100001
