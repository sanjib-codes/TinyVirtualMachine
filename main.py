import tkinter as tk
from tkinter import messagebox


class TinyVirtualMachine:
    """Educational stack-based virtual machine."""

    def __init__(self):
        self.reset_state()

    def reset_state(self):
        self.stack = []
        self.variables = {}
        self.pc = 0
        self.program = []
        self.halted = False
        self.output = []
        self.temp_counter = 0

    def save_temporary(self, value):
        self.temp_counter += 1
        self.variables[f"T{self.temp_counter}"] = value

    def load_program(self, source):
        self.reset_state()
        labels = {}
        raw = []

        # Pass 1: collect labels and instructions.
        for line_no, raw_line in enumerate(source.splitlines(), 1):
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue
            if line.endswith(":"):
                label = line[:-1].strip()
                if not label.isidentifier():
                    raise ValueError(f"Invalid label on line {line_no}")
                if label in labels:
                    raise ValueError(f"Duplicate label '{label}' on line {line_no}")
                labels[label] = len(raw)
            else:
                parts = line.split()
                raw.append({"op": parts[0].upper(), "args": parts[1:], "line": line_no})

        arity = {
            "PUSH": 1, "POP": 0, "DUP": 0, "ADD": 0, "SUB": 0,
            "MUL": 0, "DIV": 0, "MOD": 0, "NEG": 0, "LOAD": 1,
            "STORE": 1, "PRINT": 0, "EQ": 0, "GT": 0, "LT": 0,
            "JMP": 1, "JZ": 1, "JNZ": 1, "HALT": 0
        }

        # Pass 2: validate and resolve jump labels.
        for ins in raw:
            op, args, line_no = ins["op"], ins["args"], ins["line"]
            if op not in arity:
                raise ValueError(f"Unknown instruction '{op}' on line {line_no}")
            if len(args) != arity[op]:
                raise ValueError(f"{op} expects {arity[op]} argument(s) on line {line_no}")
            if op == "PUSH":
                try:
                    float(args[0])
                except ValueError:
                    raise ValueError(f"PUSH needs a number on line {line_no}")
            elif op in ("LOAD", "STORE"):
                if not args[0].isidentifier():
                    raise ValueError(f"Invalid variable name on line {line_no}")
            elif op in ("JMP", "JZ", "JNZ"):
                if args[0] not in labels:
                    raise ValueError(f"Unknown label '{args[0]}' on line {line_no}")
                ins["args"] = [labels[args[0]]]
            self.program.append(ins)

    def step(self):
        if self.halted:
            return None
        if self.pc >= len(self.program):
            self.halted = True
            return None

        ins = self.program[self.pc]
        current_pc = self.pc
        self.pc += 1
        op, args, line_no = ins["op"], ins["args"], ins["line"]

        def pop_value():
            if not self.stack:
                raise ValueError(f"Stack underflow on source line {line_no}")
            return self.stack.pop()

        if op == "PUSH":
            value = float(args[0])
            if value.is_integer():
                value = int(value)
            self.stack.append(value)
            self.save_temporary(value)

        elif op == "POP":
            pop_value()

        elif op == "DUP":
            if not self.stack:
                raise ValueError(f"Stack underflow on source line {line_no}")
            value = self.stack[-1]
            self.stack.append(value)
            self.save_temporary(value)

        elif op == "NEG":
            result = -pop_value()
            self.stack.append(result)
            self.save_temporary(result)

        elif op in ("ADD", "SUB", "MUL", "DIV", "MOD", "EQ", "GT", "LT"):
            b, a = pop_value(), pop_value()
            if op == "ADD":
                result = a + b
            elif op == "SUB":
                result = a - b
            elif op == "MUL":
                result = a * b
            elif op == "DIV":
                if b == 0:
                    raise ValueError(f"Division by zero on source line {line_no}")
                result = a / b
            elif op == "MOD":
                if b == 0:
                    raise ValueError(f"Modulo by zero on source line {line_no}")
                result = a % b
            elif op == "EQ":
                result = int(a == b)
            elif op == "GT":
                result = int(a > b)
            else:
                result = int(a < b)
            self.stack.append(result)
            self.save_temporary(result)

        elif op == "STORE":
            self.variables[args[0]] = pop_value()

        elif op == "LOAD":
            name = args[0]
            if name not in self.variables:
                raise ValueError(f"Undefined variable '{name}' on source line {line_no}")
            value = self.variables[name]
            self.stack.append(value)
            self.save_temporary(value)

        elif op == "PRINT":
            if not self.stack:
                raise ValueError(f"Nothing to print: stack is empty on line {line_no}")
            self.output.append(self.stack[-1])

        elif op == "JMP":
            self.pc = args[0]

        elif op == "JZ":
            if pop_value() == 0:
                self.pc = args[0]

        elif op == "JNZ":
            if pop_value() != 0:
                self.pc = args[0]

        elif op == "HALT":
            self.halted = True

        return current_pc, op


class VirtualMachineGUI:
    SAMPLE = """# Calculate (10 + 20) * 5
PUSH 10
PUSH 20
ADD
PUSH 5
MUL
PRINT
HALT
"""

    def __init__(self, root):
        self.root = root
        self.root.title("Tiny Virtual Machine - Compiler Design PBL")
        self.root.geometry("1050x720")
        self.root.minsize(850, 600)
        self.root.configure(bg="#172033")
        self.vm = TinyVirtualMachine()
        self.create_interface()
        self.editor.insert("1.0", self.SAMPLE)
        self.load_program()

    def create_interface(self):
        tk.Label(self.root, text="TINY VIRTUAL MACHINE",
                 font=("Arial", 22, "bold"), bg="#172033",
                 fg="#38BDF8").pack(pady=(14, 4))
        tk.Label(self.root,
                 text="Intermediate Code Execution | Compiler Design PBL",
                 font=("Arial", 11), bg="#172033",
                 fg="white").pack(pady=(0, 12))

        main = tk.Frame(self.root, bg="#172033")
        main.pack(fill="both", expand=True, padx=16, pady=8)
        left = tk.Frame(main, bg="#243047")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right = tk.Frame(main, bg="#243047")
        right.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(left, text="BYTECODE EDITOR", font=("Arial", 13, "bold"),
                 bg="#243047", fg="#38BDF8").pack(pady=10)
        self.editor = tk.Text(left, height=22, width=42,
                              font=("Consolas", 12), bg="#101827",
                              fg="#E2E8F0", insertbackground="white",
                              undo=True, wrap="none")
        self.editor.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        buttons = tk.Frame(left, bg="#243047")
        buttons.pack(pady=(0, 12))
        self.make_button(buttons, "LOAD", self.load_program)
        self.make_button(buttons, "STEP", self.execute_step)
        self.make_button(buttons, "RUN ALL", self.run_all)
        self.make_button(buttons, "RESET", self.reset)

        tk.Label(right, text="RUNTIME STACK (bottom to top)",
                 font=("Arial", 13, "bold"), bg="#243047",
                 fg="#4ADE80").pack(pady=(10, 6))
        self.stack_view = tk.Listbox(right, height=8, font=("Consolas", 12),
                                     bg="#101827", fg="#4ADE80")
        self.stack_view.pack(fill="x", padx=12)

        tk.Label(right, text="VARIABLE MEMORY",
                 font=("Arial", 13, "bold"), bg="#243047",
                 fg="#FACC15").pack(pady=(12, 6))
        self.variable_view = tk.Listbox(right, height=7,
                                        font=("Consolas", 12),
                                        bg="#101827", fg="#FACC15")
        self.variable_view.pack(fill="x", padx=12)

        tk.Label(right, text="EXECUTION OUTPUT",
                 font=("Arial", 13, "bold"), bg="#243047",
                 fg="#38BDF8").pack(pady=(12, 6))
        self.output_view = tk.Text(right, height=7, font=("Consolas", 11),
                                   bg="#101827", fg="white",
                                   state="disabled")
        self.output_view.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.status = tk.Label(self.root, text="STATUS: READY",
                               font=("Arial", 11, "bold"),
                               bg="#0F172A", fg="#4ADE80",
                               anchor="w", padx=14, pady=8)
        self.status.pack(fill="x", side="bottom")

    def make_button(self, parent, text, command):
        tk.Button(parent, text=text, command=command,
                  font=("Arial", 10, "bold"), bg="#0284C7",
                  fg="white", activebackground="#0369A1",
                  activeforeground="white", width=9,
                  relief="flat", cursor="hand2").pack(side="left", padx=4)

    def load_program(self):
        try:
            self.vm = TinyVirtualMachine()
            self.vm.load_program(self.editor.get("1.0", "end-1c"))
            self.clear_views()
            self.update_views()
            self.status.config(text=f"STATUS: {len(self.vm.program)} INSTRUCTIONS LOADED",
                               fg="#4ADE80")
        except Exception as error:
            messagebox.showerror("Bytecode Error", str(error))
            self.status.config(text="STATUS: LOAD ERROR", fg="#F87171")

    def execute_step(self):
        try:
            if self.vm.halted:
                self.status.config(text="STATUS: EXECUTION COMPLETED", fg="#4ADE80")
                return
            result = self.vm.step()
            self.update_views()
            if result is None:
                self.status.config(text="STATUS: EXECUTION COMPLETED", fg="#4ADE80")
            else:
                pc, operation = result
                self.status.config(text=f"EXECUTED PC {pc}: {operation}",
                                   fg="#38BDF8")
                if self.vm.halted:
                    self.status.config(text="STATUS: EXECUTION COMPLETED",
                                       fg="#4ADE80")
        except Exception as error:
            self.status.config(text="STATUS: EXECUTION ERROR", fg="#F87171")
            messagebox.showerror("Execution Error", str(error))

    def run_all(self):
        try:
            while not self.vm.halted:
                if self.vm.step() is None:
                    break
            self.update_views()
            self.status.config(text="STATUS: EXECUTION COMPLETED", fg="#4ADE80")
        except Exception as error:
            self.update_views()
            self.status.config(text="STATUS: EXECUTION ERROR", fg="#F87171")
            messagebox.showerror("Execution Error", str(error))

    def reset(self):
        self.load_program()

    def clear_views(self):
        self.stack_view.delete(0, tk.END)
        self.variable_view.delete(0, tk.END)
        self.output_view.config(state="normal")
        self.output_view.delete("1.0", tk.END)
        self.output_view.config(state="disabled")

    def update_views(self):
        self.stack_view.delete(0, tk.END)
        for index, value in enumerate(self.vm.stack, start=1):
            self.stack_view.insert(tk.END, f"{index}.  {value}")

        self.variable_view.delete(0, tk.END)
        if not self.vm.variables:
            self.variable_view.insert(tk.END, "(empty)")
        else:
            for name, value in self.vm.variables.items():
                self.variable_view.insert(tk.END, f"{name} = {value}")

        self.output_view.config(state="normal")
        self.output_view.delete("1.0", tk.END)
        for value in self.vm.output:
            self.output_view.insert(tk.END, f"OUTPUT: {value}\n")
        self.output_view.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualMachineGUI(root)
    root.mainloop()
