import tkinter as tk

def press(key):
    current = entry.get()
    if key == "C":
        entry.delete(0, tk.END)
    elif key == "=":
        try:
            result = eval(current)
            entry.delete(0, tk.END)
            entry.insert(tk.END, str(result))
        except:
            entry.delete(0, tk.END)
            entry.insert(tk.END, "Ошибка")
    else:
        entry.insert(tk.END, key)

root = tk.Tk()
root.title("Калькулятор")

entry = tk.Entry(root, width=20, font=("Arial", 16), justify="right")
entry.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

buttons = [
    "7", "8", "9", "/",
    "4", "5", "6", "*",
    "1", "2", "3", "-",
    "C", "0", "=", "+"
]

row, col = 1, 0
for btn in buttons:
    tk.Button(root, text=btn, width=5, height=2, font=("Arial", 14),
              command=lambda b=btn: press(b)).grid(row=row, column=col, padx=2, pady=2)
    col += 1
    if col > 3:
        col = 0
        row += 1

root.mainloop()
