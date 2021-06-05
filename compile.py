import os
import argh


def gen_signal_name(line_idx, sig_idx):
    return f"sig_{line_idx:04x}_{sig_idx:04x}"


def gen_input_name(idx):
    return f"input_{idx:04x}_int"


def gen_output_name(idx):
    return f"output_{idx:04x}_int"


def gen_mem_name(idx):
    return f"mem_{idx:04x}"


@argh.arg("filename", help="The path to the input file")
@argh.arg(
    "--outfile",
    default=None,
    help="The path to the output file."
    + "Generated from the module name by default"
)
@argh.arg(
    "--module_name",
    default=None,
    help="The name of the generated VHDL entity."
    + "Generated from the input file name by default"
)
@argh.arg("--debug", help="Prints additional debug information")
def compile(filename, outfile=None, module_name=None, debug=False):
    "Compile the specified file to VHDL"
    with open(filename, 'r') as file:
        program = file.read()

    input_idx = 0
    output_idx = 0

    signals = {}
    assignments = []

    mem_counter = 0
    mem_idx = 0
    mem_list = []
    registers = []

    for line_idx, line in enumerate(program.splitlines()):
        if debug:
            print(signals)

        line_in_idx = 0
        line_out_idx = 0

        for char_idx, char in enumerate(line):
            if char == "i":
                signals[gen_signal_name(line_idx, line_out_idx)] = 1
                assignments.append((
                    gen_signal_name(line_idx, line_out_idx),
                    gen_input_name(input_idx)
                ))
                line_out_idx += 1
                input_idx += 1
            elif char == "o":
                assignments.append((
                    gen_output_name(output_idx),
                    gen_signal_name(line_idx - 1, line_in_idx)
                ))
                line_in_idx += 1
                output_idx += 1
            elif char == "1":
                signals[gen_signal_name(line_idx, line_out_idx)] = 1
                assignments.append((
                    gen_signal_name(line_idx, line_out_idx),
                    "\"1\""
                ))
                line_out_idx += 1
            elif char == "0":
                signals[gen_signal_name(line_idx, line_out_idx)] = 1
                assignments.append((
                    gen_signal_name(line_idx, line_out_idx),
                    "\"0\""
                ))
                line_out_idx += 1

            elif char == "|":
                src_sig = gen_signal_name(line_idx - 1, line_in_idx)
                tgt_sig = gen_signal_name(line_idx, line_out_idx)
                signals[tgt_sig] = signals[src_sig]
                assignments.append((tgt_sig, src_sig))
                line_in_idx += 1
                line_out_idx += 1
            elif char == "v":
                src_sig_1 = gen_signal_name(line_idx - 1, line_in_idx)
                src_sig_2 = gen_signal_name(line_idx - 1, line_in_idx + 1)
                tgt_sig = gen_signal_name(line_idx, line_out_idx)
                signals[tgt_sig] = signals[src_sig_1] + signals[src_sig_2]
                assignments.append((tgt_sig, f"{src_sig_1} & {src_sig_2}"))
                line_in_idx += 2
                line_out_idx += 1
            elif char == "x":
                src_sig_1 = gen_signal_name(line_idx - 1, line_in_idx)
                src_sig_2 = gen_signal_name(line_idx - 1, line_in_idx + 1)
                tgt_sig_1 = gen_signal_name(line_idx, line_out_idx)
                tgt_sig_2 = gen_signal_name(line_idx, line_out_idx + 1)
                signals[tgt_sig_1] = signals[src_sig_2]
                signals[tgt_sig_2] = signals[src_sig_1]
                assignments.append((tgt_sig_1, src_sig_2))
                assignments.append((tgt_sig_2, src_sig_1))
                line_in_idx += 2
                line_out_idx += 2
            elif char == "<":
                src_sig = gen_signal_name(line_idx - 1, line_in_idx)
                tgt_sig_1 = gen_signal_name(line_idx, line_out_idx)
                tgt_sig_2 = gen_signal_name(line_idx, line_out_idx + 1)
                sig_len = signals[src_sig]
                signals[tgt_sig_1] = 1
                signals[tgt_sig_2] = sig_len - 1
                assignments.append((
                    tgt_sig_1,
                    f"{src_sig}({sig_len - 1} downto {sig_len - 1})"
                ))
                assignments.append((
                    tgt_sig_2,
                    f"{src_sig}({sig_len - 2} downto 0)"
                ))
                line_in_idx += 1
                line_out_idx += 2
            elif char == ">":
                src_sig = gen_signal_name(line_idx - 1, line_in_idx)
                tgt_sig_1 = gen_signal_name(line_idx, line_out_idx)
                tgt_sig_2 = gen_signal_name(line_idx, line_out_idx + 1)
                sig_len = signals[src_sig]
                signals[tgt_sig_1] = sig_len - 1
                signals[tgt_sig_2] = 1
                assignments.append((
                    tgt_sig_1,
                    f"{src_sig}({sig_len - 1} downto 1)"
                ))
                assignments.append((
                    tgt_sig_2,
                    f"{src_sig}(0 downto 0)"
                ))
                line_in_idx += 1
                line_out_idx += 2
            elif char == "-":
                line_in_idx += 1
            elif char == ":":
                src_sig = gen_signal_name(line_idx - 1, line_in_idx)
                tgt_sig_1 = gen_signal_name(line_idx, line_out_idx)
                tgt_sig_2 = gen_signal_name(line_idx, line_out_idx + 1)
                sig_len = signals[src_sig]
                signals[tgt_sig_1] = sig_len
                signals[tgt_sig_2] = sig_len
                assignments.append((tgt_sig_1, src_sig))
                assignments.append((tgt_sig_2, src_sig))
                line_in_idx += 1
                line_out_idx += 2

            elif char == "&":
                src_sig_1 = gen_signal_name(line_idx - 1, line_in_idx)
                src_sig_2 = gen_signal_name(line_idx - 1, line_in_idx + 1)
                tgt_sig = gen_signal_name(line_idx, line_out_idx)
                sig_len = signals[src_sig_1]
                if sig_len != signals[src_sig_2]:
                    print("Signal width mismatch:")
                    print(f"    line {line_idx}, char {char_idx}")
                    exit(1)
                signals[tgt_sig] = sig_len
                assignments.append((
                    tgt_sig,
                    f"not ({src_sig_1} and {src_sig_2})"
                ))
                line_in_idx += 2
                line_out_idx += 1

            elif char == "r":
                mem_name = gen_mem_name(mem_idx - mem_counter)
                tgt_sig = gen_signal_name(line_idx, line_out_idx)
                signals[tgt_sig] = 1
                signals[mem_name] = 1
                assignments.append((tgt_sig, mem_name))
                line_out_idx += 1
                if mem_counter == 0:
                    mem_list.append(mem_name)
                else:
                    mem_counter -= 1
            elif char == "w":
                src_sig = gen_signal_name(line_idx - 1, line_in_idx)
                line_in_idx += 1
                sig_len = signals[src_sig]
                for i in range(sig_len):
                    mem_name = gen_mem_name(mem_idx)
                    index = sig_len - i - 1
                    mem_idx += 1
                    if len(mem_list) == 0:
                        mem_counter += 1
                        assignments.append((
                            mem_name,
                            f"{src_sig}({index} downto {index})"
                        ))
                    else:
                        mem_name = mem_list.pop(0)
                        registers.append((
                            mem_name,
                            f"{src_sig}({index} downto {index})"
                        ))
            elif char == " ":
                pass
            else:
                break

    if module_name is None:
        module_name = os.path.splitext(os.path.basename(filename))[0]

    write_out(
        outfile,
        module_name,
        input_idx,
        output_idx,
        signals,
        assignments,
        registers
    )


def write_entity(file, num_in, num_out):
    file.write("entity sbtv_module is\n")
    file.write("port map (\n")
    file.write("\tclk : in std_logic;\n")
    file.write("\trstn : in std_logic;\n")
    file.write(f"\tinputs : in std_logic_vector({num_in - 1} downto 0);\n")
    file.write(f"\toutputs : out std_logic_vector({num_out - 1} downto 0));\n")


def write_decl(file, signal, width):
    file.write(f"\tsignal {signal} : std_logic_vector({width - 1} downto 0);\n")


def write_assignment(file, assignment, indent=1):
    file.write("\t" * indent + f"{assignment[0]} <= {assignment[1]};\n")


def write_regs(file, registers):
    file.write("\n\tprocess (clk, rstn) is\n\tbegin\n")
    file.write("\t\tif rstn = '0' then\n")
    for reg, _ in registers:
        write_assignment(file, (reg, "0"), 3)
    file.write("\t\telsif clk'event and clk = '1' then\n")
    for reg, src in registers:
        write_assignment(file, (reg, src), 3)
    file.write("\t\tend if;\n")
    file.write("\tend process;\n")


def write_out(
        filename, module_name,
        in_count, out_count,
        signals, assignments, registers):

    if filename is None:
        filename = module_name + ".vhd"

    with open(filename, 'w') as file:
        write_entity(file, in_count, out_count)
        file.write("\narchitecture sbtv of {module_name} is\n")
        for sig, width in signals.items():
            write_decl(file, sig, width)
        file.write("begin\n")

        for in_idx in range(in_count):
            id = in_count - in_idx - 1
            write_assignment(file, (
                gen_input_name(in_idx),
                f"inputs({id} downto {id})"
            ))
        file.write("\n")

        for assignment in assignments:
            write_assignment(file, assignment)
        if len(registers) > 0:
            write_regs(file, registers)
        file.write("\n")

        for out_idx in range(out_count):
            id = out_count - out_idx - 1
            write_assignment(file, (
                f"outputs({id} downto {id})",
                gen_output_name(out_idx)
            ))
        file.write("end architecture sbtv;")
