# Abstract Machine Interpreter
# By: Carlos Guanzon


from collections import defaultdict, deque
import tkinter as tk
from tkinter import filedialog


output_gui = []
output_gui_stacks = []
output_head_list = []
turn_num = 0
turn_num_stack = 0
curr_head = 0
branch_num = 0
branch_counter = 0
final_state = ""
accepted_branch_num = 0
is_last_branch = False
machine_definition = "q0] R (1/1,q0), (0/#,q0), (#/#,accept)"
curr_direction = "right"
stack_1 = []
stack_2 = []
curr_print_stack = []
print_stack = []
number_of_stacks = 0
number_of_tapes = 0
color = "#008000"


class Stack:

    def __init__(self, blank, string='', head=0, name = ''):
        self.lastCommand = ' _ '
        global curr_head
        self.blank = blank
        self.loadString(string, head)
        self.name = name



    def changeCommand(self, string):
        self.lastCommand = string

    def loadString(self, string, head):
        global branch_num, output_gui_stacks

        self.symbols = list(string)
        self.symbols.append('`')
        self.head = head

        if self.symbols != []:
            output_gui_stacks.append([])


    def readSymbol(self):

        if self.head < len(self.symbols):
            return self.symbols[self.head]

        else:
            return self.blank

    def writeSymbol(self, symbol):

        if self.head < len(self.symbols):
            self.symbols[self.head] = symbol

        else:
            self.symbols.append(symbol)

    def moveHead(self, direction):
        if direction == 'W1' or direction == 'W2' or direction == 'W':
            inc = 1
        elif direction == 'Read1' or direction == 'Read2' or direction == 'Read':
            inc = -1
        else:
            inc = 0
        print('current pointer head: ', self.head)
        self.head += inc
        if self.head < 0:
            self.head = 0




    def clone(self):
        global curr_head, new_branch
        curr_head = self.head
        new_branch = True
        return Tape(self.blank, self.symbols, self.head)



    def __str__(self):
        global curr_head
        curr_head = self.head
        return str(self.symbols[:self.head]) + \
               str(self.symbols[self.head:])

class Tape:

    def __init__(self, blank, string='', head=0, name='T1'):
        global curr_head
        self.lastCommand = ' _ '
        self.blank = blank
        self.loadString(string, head)
        self.name = name


    def changeCommand(self, string):
        self.lastCommand = string


    def loadString(self, string, head):
        global branch_num

        self.symbols = list(string)
        self.symbols.append('#')
        self.head = head

        if self.symbols != []:
            output_gui.append([])
            output_head_list.append([])
            print_stack.append([])
            stack_1.append([])

            branch_num += 1


    def readSymbol(self):

        if self.head < len(self.symbols):
            return self.symbols[self.head]

        else:
            return self.blank

    def writeSymbol(self, symbol):

        if self.head < len(self.symbols):

            self.symbols[self.head] = symbol

        else:
            self.symbols.append(symbol)



    def moveHead(self, direction):
        global curr_head, curr_direction
        if direction == 'L':
            inc = -1
            curr_direction = 'left'
        elif direction == 'R':
            inc = 1
            curr_direction = 'right'
        else:
            inc = 0
        self.head += inc

        curr_head = self.head




    def clone(self):
        global curr_head, new_branch
        curr_head = self.head
        new_branch = True
        return Tape(self.blank, self.symbols, self.head)



    def __str__(self):
        global curr_head
        curr_head = self.head
        return str(self.symbols[:self.head]) + \
               str(self.symbols[self.head:])


class AMI:

    def __init__(self, start, final, stack1_name = ['S1'], tape_name = ['T1'], blank='#', ntapes=1, stacks=1):
        self.start = self.state = start
        self.final = final
        self.tapes = [Tape(blank, name=tape_name[idx]) for idx, _ in enumerate(range(ntapes))]
        self.trans = defaultdict(list)
        self.transKey = defaultdict(list)
        self.transKeyStack = defaultdict(list)
        self.stacks = [Stack('`', name= stack1_name[idx]) for idx, _ in enumerate(range(stacks))]
        self.lastPosScan = 'R'
        self.lastPosWrite = ''
        self.changed = False
        self.ntapes = ntapes
        self.tapeIndex = 0


    def restart(self, string):
        self.state = self.start
        if self.ntapes > 1:
            temp_string = string.split('#')

            temp_length = len(temp_string)

            for idx, tape in enumerate(self.tapes):
                if temp_length > idx:
                    tape.loadString(temp_string[idx], 0)
                else:
                    tape.loadString('', 0)
        else:
            self.tapes[0].loadString(string, 0)
            for tape in self.tapes[1:]:
                tape.loadString('', 0)

        if len(self.stacks) != 0:
            self.stacks[0].loadString('', 0)

        for stack in self.stacks[1:]:
            stack.loadString('', 0)


    def addTransKey(self, state, read_sym, new_state, moves):
        self.transKey[state].append(moves[0][1])

    def addStackKey(self, state, read_sym, new_state, moves):
        self.transKeyStack[state].append(moves[0][1])

    def readSymbols(self):
        return tuple(tape.readSymbol() for tape in self.tapes)

    def readStack(self):
        return tuple(stack.readSymbol() for stack in self.stacks)

    def readStack2(self):
        return tuple(stack.readSymbol() for stack in self.stacks2)

    def addTrans(self, state, read_sym, new_state, moves):
        self.trans[(state, read_sym)].append((new_state, moves))


    def getTrans(self):
        temp_var = self.transKey[self.state]

        if(len(temp_var) > 0):
            if(temp_var[0].split('_')[0] == 'W' or temp_var[0].split('_')[0] == 'Read'):
                for stack in self.stacks:
                    if(temp_var[0].split('_')[1] == stack.name):
                        key = (self.state, tuple(stack.readSymbol()))
                        print('key: ', key)
                        print('self.trans: ', self.trans)
                        if key in self.trans:
                            return self.trans[key]

                return None
            elif temp_var[0] == 'Print':
                key = (self.state, tuple('#'))
                return self.trans[key]
            else:
                for tape in self.tapes:
                    if(temp_var[0].split('_')[1] == tape.name):
                        key = (self.state, tuple(tape.readSymbol()))
                        print('i am key: ', key)
                        print(self.trans)
                        if key in self.trans:
                            return self.trans[key]

                return None
        else:
            return None

    def execTrans(self, trans):
        global curr_head, branch_counter, curr_direction, print_stack


        if branch_counter < branch_num:

            for idx, output_tape in enumerate(self.tapes):
                output_tape = str(output_tape)
                output_tape = output_tape.replace('[', '')
                output_tape = output_tape.replace(']', '')
                output_tape = output_tape.replace("'", '')
                output_tape = output_tape.replace(',', '')

                output_tape = output_tape.replace('\n', '')
                output_tape = output_tape.replace(' ', '')
                output_tape = str(self.state) + ':' + output_tape
                head_num = (len(self.state) + 1) + curr_head
                output_head = output_tape[0:head_num] + 'V' + output_tape[head_num + 1:]

                for i, let in enumerate(output_head):
                    if let != 'V':
                        let = ' '
                        output_head = output_head[0:i] + let + output_head[i + 1:]

                output_gui[branch_counter].append(output_tape)
                output_head_list[branch_counter].append(output_head)

                stripped_list = map(str.strip, curr_print_stack)
                temp_string = ''.join(stripped_list)

                print_stack[branch_counter].append(temp_string)


            for idx, temp_stack in enumerate(self.stacks):
                stack_string = str(temp_stack)
                stack_string = stack_string.replace('[', '')
                stack_string = stack_string.replace(']', '')
                stack_string = stack_string.replace("'", '')
                stack_string = stack_string.replace(',', '')

                stack_string = stack_string.replace('\n', '')
                stack_string = stack_string.replace(' ', '')
                stack_string = stack_string.replace('`', '')

                stack_1[branch_counter].append(str(stack_string))


        self.state, moves = trans

        for move in (moves):
            symbol, direction = move

            temp_var = self.transKey[self.state]

            temp_stack_name = 'None'


            if (len(temp_var) != 0):
                print('Direction: ', direction)
                print('DIrection concatenated: ', direction.split('_')[0])
                if temp_var[0].split('_')[0] == 'Read' or temp_var[0].split('_')[0] == 'W':
                    temp_stack_name = temp_var[0].split('_')[1]
                else:
                    temp_stack_name = 'None'
                if temp_var[0].split('_')[0] == 'R' or temp_var[0].split('_')[0] == 'L':
                    temp_tape_name = temp_var[0].split('_')[1]
                else:
                    temp_tape_name = 'None'





                if(direction == 'Print'):
                    curr_print_stack.append(symbol)

                elif (direction.split('_')[0] == 'R' and temp_var[0].split('_')[0] == 'L' and temp_tape_name == direction.split('_')[1]):

                    for temp_tape in self.tapes:
                        if temp_var[0].split('_')[1] == temp_tape.name:
                            temp_tape.writeSymbol(symbol)
                            temp_tape.moveHead('L')
                            self.lastPosScan = 'L'
                            temp_tape.changeCommand('L' + '_' + temp_var[0].split('_')[1])
                elif (direction.split('_')[0] == 'L' and temp_var[0].split('_')[0] == 'R' and temp_tape_name == direction.split('_')[1]):
                    for temp_tape in self.tapes:
                        if temp_var[0].split('_')[1] == temp_tape.name:
                            temp_tape.writeSymbol(symbol)
                            temp_tape.moveHead('R')
                            self.lastPosScan = 'R'
                            temp_tape.changeCommand('R' + '_' + temp_var[0].split('_')[1])
                elif (direction.split('_')[0] == 'L' or direction.split('_')[0] == 'R'):
                    for temp_tape in self.tapes:
                        if direction.split('_')[1] == temp_tape.name:
                            temp_tape.writeSymbol(symbol)
                            temp_tape.moveHead(direction.split('_')[0])
                            self.lastPosScan = direction
                            temp_tape.changeCommand(direction)

                else:

                    if ((temp_var[0].split('_')[0] == 'Read' and direction.split('_')[0] == 'W' and temp_stack_name == direction.split('_')[1])):
                        for temp_stack in self.stacks:
                            print('i am triggering: ', temp_stack)
                            if temp_var[0].split('_')[1] == temp_stack.name:
                                temp_stack.writeSymbol(symbol)
                                temp_stack.moveHead('Read')
                                self.lastPosWrite = 'Read' + '_' + temp_var[0].split('_')[1]
                                temp_stack.changeCommand('Read' + '_' + temp_var[0].split('_')[1])



                    elif ((direction.split('_')[0] == 'Read' or direction.split('_')[0] == 'W') ):
                        for temp_stack in self.stacks:
                            print('i am triggering: ', temp_stack)
                            if direction.split('_')[1] == temp_stack.name:
                                temp_stack.writeSymbol(symbol)
                                temp_stack.moveHead(direction.split('_')[0])
                                self.changed = True
                                self.lastPosWrite = direction
                                temp_stack.changeCommand(direction)

                for temp_stack in self.stacks:

                    if ((temp_var[0].split('_')[0] == 'Read' and temp_stack.lastCommand.split('_')[0] == 'W' and temp_stack_name == temp_stack.lastCommand.split('_')[1])):

                            if temp_stack.name == temp_stack_name:
                                temp_stack.moveHead('Read')
                                self.lastPosWrite = 'Read' + '_' + temp_var[0].split('_')[1]
                                temp_stack.changeCommand('Read')

                    elif ((temp_var[0].split('_')[0] == 'W' and temp_stack.lastCommand.split('_')[
                        0] == 'Read' and temp_stack_name == temp_stack.lastCommand.split('_')[1])):

                        if temp_stack.name == temp_stack_name:
                            temp_stack.moveHead('W')
                            self.lastPosWrite = 'W' + '_' + temp_var[0].split('_')[1]
                            temp_stack.changeCommand('W' + '_' + temp_var[0].split('_')[1])


                for temp_tape in self.tapes:

                    if ((temp_var[0].split('_')[0] == 'R' and temp_tape.lastCommand.split('_')[0] == 'L' and temp_tape_name == temp_tape.lastCommand.split('_')[1])):

                            if temp_tape.name == temp_tape_name:
                                temp_tape.moveHead('R')
                                temp_tape.moveHead('R')
                                self.lastPosWrite = 'R' + '_' + temp_var[0].split('_')[1]
                                temp_tape.changeCommand('R' + '_' + temp_var[0].split('_')[1])

                    elif ((temp_var[0].split('_')[0] == 'L' and temp_tape.lastCommand.split('_')[0] == 'R' and temp_tape_name == temp_tape.lastCommand.split('_')[1])):

                        if temp_tape.name == temp_tape_name:
                            temp_tape.moveHead('L')
                            temp_tape.moveHead('L')
                            self.lastPosWrite = 'L' + '_' + temp_var[0].split('_')[1]
                            temp_tape.changeCommand('L' + '_' + temp_var[0].split('_')[1])



            else:

                if (direction.split('_')[0] == 'Read' or direction.split('_')[0] == 'W'):
                    for temp_stack in self.stacks:

                        if direction.split('_')[1] == temp_stack.name:
                            temp_stack.writeSymbol(symbol)
                            temp_stack.moveHead(direction.split('_')[0])
                            self.lastPosWrite = direction
                else:
                    for tape in self.tapes:
                        tape.writeSymbol(symbol)
                        tape.moveHead(direction)




        if branch_counter < branch_num:

            for idx, output_tape in enumerate(self.tapes):
                output_tape = str(output_tape)
                output_tape = output_tape.replace('[', '')
                output_tape = output_tape.replace(']', '')
                output_tape = output_tape.replace("'", '')
                output_tape = output_tape.replace(',', '')

                output_tape = output_tape.replace('\n', '')
                output_tape = output_tape.replace(' ', '')
                output_tape = str(self.state) + ':' + output_tape
                head_num = (len(self.state) + 1) + curr_head
                output_head = output_tape[0:head_num] + 'V' + output_tape[head_num + 1:]

                for i, let in enumerate(output_head):
                    if let != 'V':
                        let = ' '
                        output_head = output_head[0:i] + let + output_head[i + 1:]

                output_gui[branch_counter].append(output_tape)
                output_head_list[branch_counter].append(output_head)

                stripped_list = map(str.strip, curr_print_stack)
                temp_string = ''.join(stripped_list)

                print_stack[branch_counter].append(temp_string)

            for idx, temp_stack in enumerate(self.stacks):
                stack_string = str(temp_stack)
                stack_string = stack_string.replace('[', '')
                stack_string = stack_string.replace(']', '')
                stack_string = stack_string.replace("'", '')
                stack_string = stack_string.replace(',', '')

                stack_string = stack_string.replace('\n', '')
                stack_string = stack_string.replace(' ', '')
                stack_string = stack_string.replace('`', '')

                stack_1[branch_counter].append(str(stack_string))

            branch_counter += 1




            if branch_counter == branch_num:
                branch_counter = 0

        return self

    def clone(self):
        tm = AMI(self.start, self.final)
        tm.state = self.state
        tm.tapes = [tape.clone() for tape in self.tapes]
        tm.stacks = [stack.clone() for stack in self.stacks]
        tm.trans = self.trans
        tm.transKey = self.transKey
        return tm


    def accepts(self, string):
        self.restart(string)
        queue = deque([self])
        counter = 0
        while len(queue) > 0:
            counter += 1
            tm = queue.popleft()
            print('tm: ', tm)
            transitions = tm.getTrans()

            print(transitions)

            if transitions is None:

                if tm.state == tm.final: return tm
            else:
                for trans in transitions[1:]:

                    queue.append(tm.clone().execTrans(trans))


                queue.append(tm.execTrans(transitions[0]))

            if counter == 50000:
                return "Non-Termination"

        return None

    def __str__(self):
        out = ''
        for tape in self.tapes:
            out += self.state + ': ' + str(tape) + '\n'


        return out



    @staticmethod
    def parse(input):
        global final_state, number_of_stacks, number_of_tapes
        tm = None
        name_stack1 = []
        name_tape = []
        line = input.split('\n')
        start = ''
        i = 0
        program_state = 'LOGIC'

        while start == '':
            if line[i] == '.LOGIC':
                start = str(line[i + 1])
            i += 1

        for line in input.split('\n'):
            spec = line.strip()
            if len(spec) == 0 or spec[0] == '%': continue

            if spec == '.DATA':
                program_state = 'DATA'

            if program_state == 'DATA':
                if spec == '.DATA': continue
                first_new_line = line.split(' ')
                if first_new_line[0] == 'STACK':
                    name_stack1.append(first_new_line[1])
                elif first_new_line[0] == 'TAPE':
                    name_tape.append(first_new_line[1])

        number_of_stacks = len(name_stack1)


        if name_stack1 == []:
            name_stack1.append('')
        if name_tape == []:
            name_tape.append('T1')

        number_of_tapes = len(name_tape)
        start = start.split("] ")
        start = str(start[0])
        final = "accept"
        final_state = final

        tm = AMI(start, final, stack1_name=name_stack1, tape_name=name_tape, ntapes=number_of_tapes, stacks=len(name_stack1))
        program_state = 'LOGIC'

        for line in input.split('\n'):
            spec = line.strip()
            if len(spec) == 0 or spec[0] == '%': continue

            print('spec: ', spec)

            if spec == '.DATA':
                program_state = 'DATA'
            elif spec == '.LOGIC':
                program_state = 'LOGIC'

            if program_state == 'DATA':
                print("I am in data")
            elif program_state == 'LOGIC':
                if spec == '.LOGIC': continue
                first_new_line = line.split(' ')
                state = first_new_line[0]
                state = state.split("]")
                state = state[0]
                line_direction = first_new_line[1]
                new_line = first_new_line[2:]
                # Take Command

                if (first_new_line[2] == 'RIGHT'):
                    temp_direction = 'R'
                    new_line = first_new_line[3:]
                elif (first_new_line[2] == 'LEFT'):
                    temp_direction = 'L'
                    new_line = first_new_line[3:]
                elif(line_direction.split('(')[0] == 'UP'):
                    temp_tape = line_direction.split('(')[1]
                    temp_tape = temp_tape.split(')')[0]
                    temp_direction = 'Up'
                elif(line_direction.split('(')[0] == 'DOWN'):
                    temp_tape = line_direction.split('(')[1]
                    temp_tape = temp_tape.split(')')[0]
                    temp_direction = 'Down'
                elif(line_direction.split('(')[0] == 'RIGHT'):
                    temp_tape = line_direction.split('(')[1]
                    temp_tape = temp_tape.split(')')[0]
                    temp_direction = 'R'
                elif(line_direction.split('(')[0] == 'LEFT'):
                    temp_tape = line_direction.split('(')[1]
                    temp_tape = temp_tape.split(')')[0]
                    temp_direction = 'L'
                elif (line_direction.split('(')[0] == 'WRITE'):
                    temp_stack = line_direction.split('(')[1]
                    temp_stack = temp_stack.split(')')[0]
                    temp_direction = 'W'
                elif (line_direction.split('(')[0] == 'READ'):
                    temp_stack = line_direction.split('(')[1]
                    temp_stack = temp_stack.split(')')[0]
                    temp_direction = 'Read'
                elif (line_direction == 'PRINT'):
                    temp_direction = 'Print'
                else:
                    temp_direction = 'R'

                stripped_list = map(str.strip, new_line)
                line = ' '.join(stripped_list)
                for transition in line.split(', '):
                    transition = transition.replace("(", "")
                    transition = transition.replace(")", "")
                    fields = transition.split(',')
                    new_st = fields[1]
                    temp_symbols = str(fields[0])
                    temp_symbols = temp_symbols.split('/')
                    symbols = tuple(temp_symbols[0])
                    if(len(temp_symbols) > 1):
                        final_direction = temp_direction + '_' + temp_tape
                        temp_moves = [temp_symbols[1], final_direction]
                    elif(temp_direction == 'W'):
                        symbols = tuple('`')
                        final_direction = temp_direction + '_' + temp_stack
                        temp_moves = [temp_symbols[0], final_direction]
                    elif(temp_direction == 'Read'):
                        print('i am in read')
                        final_direction  = temp_direction + '_' + temp_stack
                        temp_moves = ['`', final_direction ]
                    elif(temp_direction == 'Print'):
                        symbols = tuple('#')
                        temp_moves = [temp_symbols[0], temp_direction]
                    else:
                        final_direction = temp_direction + '_' + name_tape[0]
                        temp_moves = [temp_symbols[0], final_direction]
                    stripped_list = map(str.strip, temp_moves)
                    temp_moves = ' '.join(stripped_list)
                    temp_moves = [temp_moves]
                    print('in temp moves: ', temp_moves)
                    moves = tuple(tuple(m.split(' ')for m in temp_moves))

                    tm.addTrans(state, symbols, new_st, moves)
                    print('this is in read or write: ', state, symbols, new_st, moves)
                    tm.addTransKey(state, symbols, new_st, moves)
                    if(temp_direction == 'Read' or temp_direction == 'W'):
                        tm.addStackKey(state, symbols, new_st, moves)

        return tm

def display_text():
        global branch_counter, is_last_branch, accepted_branch_num, color
        num_of_branches = 0
        list_len = 0

        num_inp = input_text.get("1.0",'end-1c')
        machine_definition = machine_text.get("1.0",'end-1c')

        tm = AMI.parse(machine_definition)
        acc_tm = tm.accepts(num_inp)


        if acc_tm == "Non-Termination":
            label.config(
                text="Non-Termination",
                fg="#FF0000")
            reset_btn['state'] = tk.NORMAL
            compute_btn['state'] = tk.DISABLED
        elif acc_tm:
            branch_counter = 0

            reset_btn['state'] = tk.NORMAL
            compute_btn['state'] = tk.DISABLED



            for idx, item in enumerate(output_gui):
                if item != []:

                    num_of_branches += 1
                    temp_result = [i for i in item if i.startswith(final_state)]
                    if temp_result != []:
                        final_result = temp_result[0]
                        final_result = str(final_result)
                        final_result = final_result.replace('[', '')
                        final_result = final_result.replace(']', '')
                        final_result = final_result.replace("'", '')
                        final_result = final_result.replace(',', '')

                        final_result = final_result.replace('\n', '')
                        final_result = final_result.replace(' ', '')
                        accepted_branch_num = idx



            if num_of_branches != 0:
                steps_btn['state'] = tk.NORMAL
                for item in output_gui[accepted_branch_num]:
                    list_len += 1

                color = "#008000"
                label.config(text="Final String and State = "+ str(final_result) + " (ACCEPTED)", fg="#008000")
                text = 'Print (if any): ' + print_stack[accepted_branch_num][-1]
                instructions_text.config(text=text, fg="#000000")
                if branch_num <= 1:
                    is_last_branch = True
            else:
                label.config(
                    text="Final String and State = λ" + " (ACCEPTED)",
                    fg="#008000")
        else:
            label.config(
                text="REJECTED",
                fg="#FF0000")
            color = "#FF0000"
            reset_btn['state'] = tk.NORMAL
            compute_btn['state'] = tk.DISABLED
            steps_btn['state'] = tk.NORMAL



def display_steps():
        global turn_num, branch_counter, turn_num_stack
        list_len = 0

        head_label.config(text=output_head_list[branch_counter][turn_num])
        label.config(text=output_gui[branch_counter][turn_num] , fg="#000000")

        text = 'Print (if any): ' + print_stack[branch_counter][turn_num]

        if number_of_stacks > 0:
            text += '\n'

        for i in range(number_of_tapes):
            text += '\n'
            text += '     ' + '   ' + output_head_list[branch_counter][turn_num + i]
            text += '\n'
            text += 'Tape ' + str(i + 1) + ': ' + output_gui[branch_counter][turn_num+i]

        for j in range(number_of_stacks):
            text += '\n'
            text += 'Stack ' + str(j + 1) + ': ' + stack_1[branch_counter][turn_num_stack+j]

        instructions_text.config(text=text, fg="#000000")

        if is_last_branch == False:
            next_branch_btn['state'] = tk.NORMAL
            if color != "#FF0000":
                accepted_branch_btn['state'] = tk.NORMAL

        for item in output_gui[branch_counter]:
            list_len += 1

        if turn_num > list_len - 3:
            turn_num += number_of_tapes
            turn_num_stack += number_of_stacks
        else:
            turn_num += number_of_tapes
            turn_num_stack += number_of_stacks

        if turn_num == list_len:
            if branch_counter == accepted_branch_num:
                label.config(text=output_gui[branch_counter][turn_num-1], fg=color)

            steps_btn['state'] = tk.DISABLED
            turn_num = 0
            turn_num_stack = 0




def reset():
    global turn_num, output_gui, output_head_list, curr_head, branch_counter,branch_num, is_last_branch, final_state, accepted_branch_num, print_stack, curr_print_stack, stack_1, number_of_stacks, turn_num_stack, number_of_tapes, color
    turn_num = 0
    branch_counter = 0
    branch_num = 0
    output_gui = []
    output_head_list = []
    curr_head = 0
    final_state = ""
    accepted_branch_num = 0
    is_last_branch = False
    label.config(text="", fg="#000000")
    head_label.config(text="", fg="#000000")
    steps_btn['state'] = tk.DISABLED
    reset_btn['state'] = tk.DISABLED
    compute_btn['state'] = tk.NORMAL
    next_branch_btn['state'] = tk.DISABLED
    accepted_branch_btn['state'] = tk.DISABLED
    curr_print_stack = []
    print_stack = []
    stack_1 = []
    number_of_stacks = 0
    turn_num_stack = 0
    number_of_tapes = 0
    color = "#008000"

    instructions_text.config(text="INSTRUCTIONS\n\n"
                                      "<Compute> - Computes your designated input with the machine file you submitted\n"
                                      "<Next> - Proceeds to the next step of the current configuration branch\n"
                                      "<Next Branch> - Proceeds to the next computed branch (for nondeterministic machines only)\n"
                                      "<Accepted Branch> - Skips to the accepted branch (for nondeterministic machines only)\n"
                                      "<Reset> - Resets the program (Must be pressed first before computing for another machine and/or input)\n\n\n"
                                      "NOTE: Due to the nondeterministic nature of the machine, there may be multiple accepted branches.\n"
                                      "This program computes all the branches of the same level in the tree, simultaneously,\n"
                                      "and stops when a branch/branches in a level have reached an accepting state.\n"
                                      "It is completely possible to have multiple accepted branches, but for the purpose of this program,\n"
                                      "only the first branch that gets accepted will appear.\n\n"
                                      "It is also important to note that the 'Accepted Branch' may only contain a portion of the steps\n"
                                      "computed to get to the accepted state. This is because it is possible that the 'Accepted Branch'\n"
                                      "is a sub-branch of another branch, and has diverged from the list of branches of the program,\n"
                                      "which inevitably excludes the previous steps computed.\n\n"
                                      "When using machines with stacks, print outputs, and multiple tapes,\n"
                                      "the content of these features will be shown during the steps.\n",
                                 font=("Courier 12"), fg="#6F6F6F")

def next_branch():
    global branch_counter, turn_num, is_last_branch
    num_of_branches = 0

    branch_counter += 1
    turn_num = 0
    steps_btn['state'] = tk.NORMAL

    head_label.config(text=output_head_list[branch_counter][turn_num])
    label.config(text=output_gui[branch_counter][turn_num], fg="#000000")
    instructions_text.config(text=print_stack[branch_counter][turn_num], fg="#000000")

    turn_num += 1

    for item in output_gui:
        if item != []:
            num_of_branches += 1

    if branch_counter == num_of_branches - 1:
        next_branch_btn['state'] = tk.DISABLED
        accepted_branch_btn['state'] = tk.DISABLED
        is_last_branch = True

def accepted_branch():
    global branch_counter, turn_num, is_last_branch
    num_of_branches = 0
    is_last_branch = True


    branch_counter = accepted_branch_num
    turn_num = 0
    steps_btn['state'] = tk.NORMAL
    next_branch_btn['state'] = tk.DISABLED
    accepted_branch_btn['state'] = tk.DISABLED

    head_label.config(text=output_head_list[accepted_branch_num][turn_num])
    label.config(text=output_gui[accepted_branch_num][turn_num])




if __name__ == '__main__':

    window = tk.Tk()
    window.geometry("1200x1000")
    window.title("Guanzon: Abstract Machine Interpreter")


    head_label = tk.Label(window, text="", font=("Courier 22 bold"))
    head_label.pack()
    label = tk.Label(window, text="", font=("Courier 22 bold"))
    label.pack()

    sample_input = "11011101"


    input_text_label = tk.Label(text="Input", font=("Courier 13"))
    input_text = tk.Text(window, width=40, height=3, font=("Courier 13"))
    input_text.insert(tk.END, sample_input)

    machine_definition_label = tk.Label(text="Machine Definition", font=("Courier 13"))

    input_text_label.pack(padx=30)
    input_text.pack(expand=False, fill = "x",padx=30)
    machine_definition_label.pack(padx=30)


    machine_text = tk.Text(window, width=40, height=10, font=("Courier 13"))
    machine_text.pack(expand=False, fill="x", padx=30)

    instructions_text= tk.Label(text="INSTRUCTIONS\n\n"
                                      "<Compute> - Computes your designated input with the machine file you submitted\n"
                                      "<Next> - Proceeds to the next step of the current configuration branch\n"
                                      "<Next Branch> - Proceeds to the next computed branch (for nondeterministic machines only)\n"
                                      "<Accepted Branch> - Skips to the accepted branch (for nondeterministic machines only)\n"
                                      "<Reset> - Resets the program (Must be pressed first before computing for another machine and/or input)\n\n\n"
                                      "NOTE: Due to the nondeterministic nature of the machine, there may be multiple accepted branches.\n"
                                      "This program computes all the branches of the same level in the tree, simultaneously,\n"
                                      "and stops when a branch/branches in a level have reached an accepting state.\n"
                                      "It is completely possible to have multiple accepted branches, but for the purpose of this program,\n"
                                      "only the first branch that gets accepted will appear.\n\n"
                                      "It is also important to note that the 'Accepted Branch' may only contain a portion of the steps\n"
                                      "computed to get to the accepted state. This is because it is possible that the 'Accepted Branch'\n"
                                      "is a sub-branch of another branch, and has diverged from the list of branches of the program,\n"
                                      "which inevitably excludes the previous steps computed.\n\n"
                                      "When using machines with stacks, print outputs, and multiple tapes,\n"
                                      "the content of these features will be shown during the steps.\n",
                                 font=("Courier 12"), fg="#6F6F6F")

    instructions_text.pack(pady=20)

    compute_btn = tk.Button(window, text="Compute", width=20, command=display_text)
    compute_btn.pack(pady=20, padx=40, side=tk.LEFT)

    steps_btn = tk.Button(window, text="Next", width=20, command=display_steps, state= tk.DISABLED)

    steps_btn.pack(pady=20, padx=40, side= tk.LEFT)
    reset_btn = tk.Button(window, text="Reset", width=20, command=reset, state= tk.DISABLED)
    reset_btn.pack(pady=20, padx=40, side=tk.RIGHT)


    next_branch_btn = tk.Button(window, text="Next Branch", width=20, command=next_branch, state= tk.DISABLED)
    next_branch_btn.pack(pady=20, padx=40, side=tk.LEFT)
    accepted_branch_btn = tk.Button(window, text="Accepted Branch", width=20, command=accepted_branch, state=tk.DISABLED)
    accepted_branch_btn.pack(pady=20, padx=40, side=tk.LEFT)

    window.mainloop()