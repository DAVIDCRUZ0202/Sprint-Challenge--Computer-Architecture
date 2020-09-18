"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # 256 bytes of memory
        self.reg = [0] * 8 # 8 general purpose registers
        self.pc = 0 # Program Counter
        self.reg[-1] = 0xF4
        self.SP = 7
        self.fl = 0

    def ram_read(self,MAR): # Memory Address Register
        return self.ram[MAR] # register used for addresses

    def ram_write(self, MDR, MAR): # Memory Data Register
        self.ram[MAR] = MDR # register used for data
        return print(f"Writing {MDR} to {MAR} Complete")

    def push_value(self, value):
        # decrement the stack pointer
        self.reg[self.SP] -= 1

        # copy the value to the SP address
        top_of_stack_address = self.reg[self.SP]
        self.ram[top_of_stack_address] = value

    def pop_value(self):
        # Get the top of stack addr
        top_of_stack_address = self.reg[self.SP]

        # Get the value of the top of the stack
        value = self.ram[top_of_stack_address]

        #Increment the stack pointer
        self.reg[self.SP] += 1

        return value

    
    def load(self):
        """Load a program into memory."""

        address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8 Op Code - 
        #     0b00000000, # 0th Index
        #     0b00001000, # Binary for 8
        #     0b01000111, # PRN R0 - Print Index 0 from memory
        #     0b00000000, # 0th Index
        #     0b00000001, # HLT
        # ]
        if len(sys.argv) != 2:
            print("Usage: comp.py filename")
            sys.exit(1)

        try:
            address = 0

            with open(sys.argv[1]) as f:
                for line in f:
                    t = line.split('#')
                    n = t[0].strip()
                    
                    if n == '':
                        continue

                    
                    try:

                        n = int(n, 2)


                    except ValueError:
                        print(f"Invalid Number{n}")
                        sys.exit(1)

                    self.ram[address] = n
                    address += 1

        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}")
            sys.exit()


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 1

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

    def run(self):
        """Run the CPU."""
        while True:
            #self.trace()
            self.IR = self.ram[self.pc] # instruction register
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)
            # Generic Increment for instructions
            byte = self.IR
            pc_instructions = byte >> 6
           

            if self.IR == 0b10000010: # Load directly into
                reg_num = operand_a
                reg_val = operand_b
                self.reg[reg_num] = reg_val

            elif self.IR == 0b01000111: # Print
                reg_num = operand_a
                print(self.reg[reg_num])

            elif self.IR == 0b10100000: # Add
                reg_num1 = operand_a
                reg_num2 = operand_b
                self.alu("ADD", reg_num1, reg_num2)

            elif self.IR == 0b10100010: # Multiply
                reg_num1 = operand_a
                reg_num2 = operand_b
                self.alu("MUL", reg_num1, reg_num2)

            elif self.IR == 0b10100111: # Compare
                reg_num1 = operand_a
                reg_num2 = operand_b
                self.alu("CMP", reg_num1, reg_num2)

            elif self.IR == 0b01010101: # Jump if equal
                # if the flag is set to 1
                if self.fl == 1:
                    # jump to the given register address
                    # Get the value from the operand reg
                    reg_num = operand_a

                    self.pc = self.reg[reg_num]
                else:
                    self.pc += 2

            elif self.IR == 0b01010110:
                if self.fl != 1:
                    reg_num = operand_a
                    self.pc = self.reg[reg_num]
                else:
                    self.pc += 2

            elif self.IR == 0b01010100:
                reg_num = operand_a
                value = self.reg[reg_num]
                self.pc = value



            elif self.IR == 0b00000001:
                self.hlt()

            elif self.IR == 0b01000101: # Push

                # Get the reg number to push to
                reg_num = operand_a

                # Get the value to push to the registry number
                value = self.reg[reg_num]

                # use the helper to push the value
                self.push_value(value)



            elif self.IR == 0b01000110: # Pop
                # Get the register to Pop the value to
                reg_num = operand_a

                # Get the value of the top of the stack
                value = self.pop_value()

                # Store the value in the register
                self.reg[reg_num] = value

            elif self.IR == 0b01010000: # Call
                # Push return addr on stack
                self.push_value(self.pc+2)
                # Get the value from the operand reg
                reg_num = self.ram[operand_a]
                value = self.reg[reg_num]
                # Set the pc to that value
                self.pc = value
                continue

            elif self.IR == 0b00010001: # Return
                # pop the return address from the stack
                return_address = self.pop_value()
                # assign the pc to that value
                self.pc = return_address

            else:
                print(f"Unknown Instruction {bin(self.IR)}")
                self.hlt()

            instructions_set_pc = (self.IR >> 4) & 1 == 1
            
            if not instructions_set_pc:
                self.pc += pc_instructions + 1

    def hlt(self):
        # print(self.pc)
        # print(self.fl)
        print("Program Ended")
        sys.exit(0)



# program = [
#             # From print8.ls8
#          0  0b10000010, # LDI R0,8
#          1  0b00000000, # NOP - Do nothing
#          2  0b00001000, # Binary for 8
#          3  0b01000111, # PRN R0
#          4  0b00000000, # NOP - Do nothing
#          5  0b00000001, # HLT
#         ]

