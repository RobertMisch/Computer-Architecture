"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.running=True
        self.FL = 5
        #stack pointer
        #register of SP, 7th
        self.SP = 6
        #actual pointer
        self.reg[self.SP] = 0xF4

        #available functions
        self.branchtable={}
        self.branchtable[0b00000001]=self.HLT 
        self.branchtable[0b10000010]=self.LDI
        self.branchtable[0b01000111]=self.PRN
        self.branchtable[0b10100010]=self.MULT
        self.branchtable[0b10100000]=self.ADD
        self.branchtable[0b01000101]=self.PUSH
        self.branchtable[0b01000110]=self.POP
        self.branchtable[0b01010000]=self.CALL
        self.branchtable[0b00010001]=self.RET
        self.branchtable[0b10100111]=self.CMP
        # self.branchtable[0b00010001]=self.JMP
        # self.branchtable[0b00010001]=self.JEQ
        # self.branchtable[0b00010001]=self.JNE

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("usage: ls8.py filename")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    try:
                        line = line.split("#",1)[0]
                        line = int(line, 2)  # int() is base 10 by default
                        self.ram[address] = line
                        address += 1
                    except ValueError:
                        pass

        except FileNotFoundError:
            print(f"Couldn't find file {sys.argv[1]}")
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MULT":
            self.reg[reg_a] = self.reg[reg_a] * self.reg[reg_b]
        elif op == "CMP":
            #LGE
            if self.reg[reg_a] < self.reg[reg_b]:
                self.reg[self.FL] = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.reg[self.FL] = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.reg[self.FL] = 0b00000001

        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    #mar is memory address register, and is the address we want. mdr is the data we want in a register
    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def HLT(self):
        print('halted successfully')
        self.running = False

    def LDI(self):
        reg_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[reg_num] = value
        self.pc += 3

    def PRN(self):
        reg_num = self.ram_read(self.pc + 1)
        self.pc += 2
        print(self.reg[reg_num])

    def MULT(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("MULT", reg_a, reg_b)
        self.pc += 3

    def ADD(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("ADD", reg_a, reg_b)
        self.pc += 3

    def PUSH(self):
        self.reg[self.SP] -= 1
        target_reg = self.ram_read(self.pc + 1)
        # print(f'pushed {self.reg[target_reg]} onto stack at {self.reg[self.SP]}')
        self.ram_write(self.reg[self.SP], self.reg[target_reg])
        self.pc += 2

    def POP(self):
        store_reg = self.ram_read(self.pc + 1)
        value = self.ram_read(self.reg[self.SP])
        # print(f'took {value} off stack at {self.reg[self.SP]}')
        self.reg[store_reg]= value
        self.reg[self.SP] += 1
        self.pc += 2

    def CALL(self):
        new_pc = self.ram_read(self.pc + 1)
        ret_addr = self.pc + 2

        #push ret onto stack to get back with RET
        self.reg[self.SP] -= 1
        self.ram_write(self.reg[self.SP], ret_addr)

        self.pc = self.reg[new_pc]
        # print(f'pushed {ret_addr} onto stack at {self.reg[self.SP]}')

    def RET(self):
        #pop from stack into pc
        self.pc = self.ram_read(self.reg[self.SP])
        # print(f'took {self.pc} off stack at {self.reg[self.SP]}')
        self.reg[self.SP] += 1

    def CMP(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("CMP", reg_a, reg_b)
        self.pc += 3

    def run(self):
        """Run the CPU."""
        while self.running:
            if self.ram_read(self.pc) in self.branchtable:
                self.branchtable[self.ram_read(self.pc)]()
            else:
                print(f"unknown instruction {self.ram_read(self.pc)}")
                self.pc += 1

