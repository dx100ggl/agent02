# repl.py

from brain.build import build_brain
from brain.c1.state import State
from brain.c5.trace_pretty import print_trace

def main():
    brain = build_brain(use_lmstudio=True)  # or False if LM Studio not running

    print("Brain-24 REPL. Type 'exit' to quit.\n")

    while True:
        user_input = input(">>> ")

        if user_input.strip().lower() in ("exit", "quit"):
            break

        state = State(user_input)
        result = brain.run(state)

        print("\n--- RESULT ---")
        print(result)

        print("\n--- TRACE ---")
        print_trace(state)

        print("\n")

if __name__ == "__main__":
    main()
