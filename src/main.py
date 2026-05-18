import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        from .cli import menu
        menu(0)
    else:
        from .gui import InterfazMundial
        import tkinter as tk
        root = tk.Tk()
        app = InterfazMundial(root)
        root.mainloop()


if __name__ == "__main__":
    main()
