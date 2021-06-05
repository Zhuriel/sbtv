#!/usr/bin/env python3
import argh

import compile

mem_list = []


@argh.arg("filename", help="The path to the input file")
@argh.arg("--debug", help="Prints additional debug information")
@argh.arg("inputs", help="Space separated bit vector inputs")
def sim(filename, debug=False, *inputs):
    "Simulate the specified file with the given inputs"
    with open(filename, 'r') as file:
        program = file.readlines()
    input_words = [[bool(int(in_bit)) for in_bit in inword] for inword in inputs]
    outputs = []
    for input in input_words:
        outputs.append(run_cycle(program, input, debug))
    print(" ".join(["".join([str(int(o)) for o in output]) for output in outputs]))


def run_cycle(program, input, debug):
    global mem_list
    line_inputs = []
    outputs = []
    for line_id, line in enumerate(program):
        if debug:
            print(f"line {line_id}:")
            print("".join([str(int(i)) for i in line_inputs]))
        line_outputs = []
        for char in line:
            if char == 'i':
                line_outputs.append([input.pop(0)])
            elif char == 'o':
                outputs += line_inputs.pop(0)
            elif char == '1':
                line_outputs.append([True])
            elif char == '0':
                line_outputs.append([False])
            elif char == 'v':
                line_outputs.append(line_inputs.pop(0) + line_inputs.pop(0))
            elif char == 'x':
                line_outputs.append(line_inputs.pop(1))
                line_outputs.append(line_inputs.pop(0))
            elif char == '<':
                val = line_inputs.pop(0)
                line_outputs.append([val[0]])
                line_outputs.append(val[1:])
            elif char == '>':
                val = line_inputs.pop(0)
                line_outputs.append(val[:-1])
                line_outputs.append([val[-1]])
            elif char == '|':
                line_outputs.append(line_inputs.pop(0))
            elif char == '-':
                line_inputs.pop(0)
            elif char == ':':
                val = line_inputs.pop(0)
                line_outputs.append(val)
                line_outputs.append(val)
            elif char == '&':
                a = line_inputs.pop(0)
                b = line_inputs.pop(0)
                res = [not (aa & bb) for aa, bb in zip(a, b)]
                line_outputs.append(res)
            elif char == 'r':
                if len(mem_list) == 0:
                    line_outputs.append([False])
                else:
                    line_outputs.append([mem_list.pop(0)])
            elif char == 'w':
                val = line_inputs.pop(0)
                for bit in val:
                    mem_list.append(bit)
            elif char == " ":
                pass
            else:
                break
        line_inputs = line_outputs
    return outputs


argh.dispatch_commands([sim, compile.compile])
