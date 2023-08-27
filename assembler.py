#!/usr/bin/env python
#
# Template for MIPS assembler.py
#
# Usage:
#    python assembler.py [asm file]

from distutils.errors import LinkError
import sys, re

# Turn a number in binary format into hexadecimal format
def bin_to_hex(x):
    y = hex(int(x,2))[2:]
    if len(y) < 8:
        y = (8-len(y))*"0" + y
    return y

# Turn a number in decimal format into binary with nbits
def dec_to_bin(value, nbits):
    value = int(value)
    fill = "0"
    if value < 0:
        value = (abs(value) ^ 0xffffffff) + 1
        fill = "1"

    value = bin(value)[2:]
    if len(value) < nbits:
        value = (nbits-len(value))*fill + value
    if len(value) > nbits:
        value = value[-nbits:]
    return value

# Array with types of r-type instructions 
rtypes = [
    'add', 'sub', 'and', 'or', 'xor', 'nor', 'sll', 'sra', 'srl', 'slt', 'jr'
]

# The op-code dictionary for each instruction but the rtypes, whose opcode is 6 zeroes. 
op_codes = {
    'addi': dec_to_bin(8, 6),
    'andi': dec_to_bin(12, 6),
    'ori': dec_to_bin(13, 6),
    'xori': dec_to_bin(14, 6),
    'slti': dec_to_bin(10, 6),
    'beq': dec_to_bin(4, 6),
    'bne': dec_to_bin(5, 6),
    'j': dec_to_bin(2, 6),
    'jal': dec_to_bin(3, 6),
    'lw': dec_to_bin(35, 6),
    'sw': dec_to_bin(43, 6)
}

# Function code dictionary for all the r-type instructions 
function_codes = {
    'add': dec_to_bin(32, 6), 
    'sub': dec_to_bin(34, 6), 
    'and': dec_to_bin(36, 6), 
    'or': dec_to_bin(37, 6), 
    'xor': dec_to_bin(38, 6), 
    'nor': dec_to_bin(39, 6), 
    'sll': dec_to_bin(0, 6), 
    'sra': dec_to_bin(3, 6), 
    'srl': dec_to_bin(2, 6), 
    'slt': dec_to_bin(42, 6),
    'jr' : dec_to_bin(8, 6)
}

# The number associated with each register. Register dictionary. 
registers = {
    '$0' : dec_to_bin(00, 5),
    '$zero' : dec_to_bin(00, 5),
    '$1' : dec_to_bin(1, 5),
    '$at': dec_to_bin(1, 5),
    '$2' : dec_to_bin(2, 5),
    '$v0': dec_to_bin(2, 5),
    '$3' : dec_to_bin(3, 5),
    '$v1': dec_to_bin(3, 5),
    '$4' : dec_to_bin(4, 5),
    '$a0': dec_to_bin(4, 5),
    '$5' : dec_to_bin(5, 5),
    '$a1': dec_to_bin(5, 5),
    '$6' : dec_to_bin(6, 5),
    '$a2': dec_to_bin(6, 5),
    '$7' : dec_to_bin(7, 5),
    '$a3': dec_to_bin(7, 5),
    '$8' : dec_to_bin(8, 5),
    '$t0': dec_to_bin(8, 5),
    '$9' : dec_to_bin(9, 5),
    '$t1': dec_to_bin(9, 5),
    '$10': dec_to_bin(10, 5),
    '$t2': dec_to_bin(10, 5),
    '$11': dec_to_bin(11, 5),
    '$t3': dec_to_bin(11, 5),
    '$12': dec_to_bin(12, 5),
    '$t4': dec_to_bin(12, 5),
    '$13': dec_to_bin(13, 5),
    '$t5': dec_to_bin(13, 5),
    '$14': dec_to_bin(14, 5),
    '$t6': dec_to_bin(14, 5),
    '$15': dec_to_bin(15, 5),
    '$t7': dec_to_bin(15, 5),
    '$16': dec_to_bin(16, 5),
    '$s0': dec_to_bin(16, 5),
    '$17': dec_to_bin(17, 5),
    '$s1': dec_to_bin(17, 5),
    '$18': dec_to_bin(18, 5),
    '$s2': dec_to_bin(18, 5),
    '$19': dec_to_bin(19, 5),
    '$s3': dec_to_bin(19, 5),
    '$20': dec_to_bin(20, 5),
    '$s4': dec_to_bin(20, 5),
    '$21': dec_to_bin(21, 5),
    '$s5': dec_to_bin(21, 5),
    '$22': dec_to_bin(22, 5),
    '$s6': dec_to_bin(22, 5),
    '$23': dec_to_bin(23, 5),
    '$s7': dec_to_bin(23, 5),
    '$24': dec_to_bin(24, 5),
    '$t8': dec_to_bin(24, 5),
    '$25': dec_to_bin(25, 5),
    '$t9': dec_to_bin(25, 5),
    '$26': dec_to_bin(26, 5),
    '$k0': dec_to_bin(26, 5),
    '$27': dec_to_bin(27, 5),
    '$k1': dec_to_bin(27, 5),
    '$28': dec_to_bin(28, 5),
    '$gp': dec_to_bin(28, 5),
    '$29': dec_to_bin(29, 5),
    '$sp': dec_to_bin(29, 5),
    '$30': dec_to_bin(30, 5),
    '$fp': dec_to_bin(30, 5),
    '$31': dec_to_bin(31, 5),
    '$ra': dec_to_bin(31, 5)
}

def main():
    me, fname = sys.argv

    f = open(fname, "r")
    labels = {}        # Map from label to its address.
    parsed_lines = []  # List of parsed instructions.
    address = -4        # Track the current address of the instruction. Modified to begin at -4 so first address is 0. Could easily implement differently as well
    line_count = 0     # Number of lines.
    for line in f:
        line_count = line_count + 1
        address = address + 4

        # Stores attributes about the current line of code, like its label, line
        # number, instruction, and arguments.
        line_attr = {}

        # Handle comments, whitespace.
        line.strip()

        # Get rid of comment 
        if '#' in line:
            indexOfComment = line.find("#")
            line = line[:indexOfComment]
        
        ' '.join(line.split())


        if line:
            # Through line_attr, we mark attributes like count and address 
            line_attr['line_number'] = line_count
            line_attr['address'] = address

            line_array = line.split()

            # Handle labels
            if ":" in line:
                labels[line_array[0].replace(':','')] = address
                line_array.pop(0)

            # Parse the rest of the instruction and its register arguments.
            # arg1 will be the first argument, arg2 next, and so on if necessary
            line_attr['instruction'] = line_array[0]
            line_array.pop(0)
            counter = 1
            for argument in line_array:
                argument = argument.replace(',', '')
                line_attr["arg" + str(counter)] = argument; 
                counter = counter + 1

            # Finally, add this dict to the complete list of instructions.
            parsed_lines.append(line_attr)
    f.close()

    machine = ""  # Current machine code word.
    startingAddressDecimal = 4194304

    for line in parsed_lines:
        if line['instruction'] == 'nop':
            print (8*'0')

        elif line['instruction'] in rtypes:
            bin_num = '000000'

            if (line['instruction'] in {'add', 'sub', 'and', 'or', 'xor', 'nor', 'slt'}):
                bin_num = bin_num + registers[line['arg2']] + registers[line['arg3']] + registers[line['arg1']] + '00000' + function_codes[line['instruction']]
            
            # Another if statement because shamt will be different for shifts, dependent on argument
            elif (line['instruction'] in {'sll', 'srl', 'sra'}):
                bin_num = bin_num + '00000' + registers[line['arg2']] + registers[line['arg1']] + dec_to_bin(line['arg3'],5) + function_codes[line['instruction']]
            
            # Only r-type instruction left is jr
            else:
                bin_num = bin_num + registers[line['arg1']] + '00000' + '00000' + '00000' + function_codes[line['instruction']]
            
            print(bin_to_hex(bin_num))

        
        else:
            bin_num = ''

            # The immediate will occupy 16 bits 
            if (line['instruction'] in {'addi', 'andi', 'ori', 'xori', 'slti', 'slt'}):
                bin_num = op_codes[line['instruction']] + registers[line['arg2']] + registers[line['arg1']] + dec_to_bin(line['arg3'], 16)

            elif (line['instruction'] in {'lw', 'sw'}): 
                # Some string manipulation to isolate the offset and the base address from a register
                secondArg = line['arg2'].split('(')
                immediate = secondArg[0]
                secondArg[1] = secondArg[1].replace(')', '')

                # With manipulation complete, form the machine code. Second arg[1] is just the base address register
                bin_num = op_codes[line['instruction']] + registers[secondArg[1]] + registers[line['arg1']] + dec_to_bin(immediate, 16)
                
            # Here, the immediate offset is the difference between the label line and the program counter line. 
            # Keep in mind by the time this instruction is read, the program counter has already incremented 
            # so the offset difference will be 1 greater than what you might expect. 
            elif (line['instruction'] in {'beq', 'bne'}):
                jumpToAddress = (labels[line['arg3']]/4 + 1) - line['line_number'] - 1 # Keeping the + 1 - 1 to emphasize that this is the offset from the program counter that has already incremented 
                bin_num = op_codes[line['instruction']] + registers[line['arg1']] + registers[line['arg2']] + dec_to_bin(jumpToAddress, 16)
                
            else:
                jumpToAddress = (startingAddressDecimal + labels[line['arg1']])/4
                bin_num = op_codes[line['instruction']] + dec_to_bin(jumpToAddress, 26)
            
            print(bin_to_hex(bin_num))    

if __name__ == "__main__":
    main()
