import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x500")
        self.root.minsize(700, 450)

        self.data_file = "expenses.json"
        self.expenses = []

        self.load_data()
        self.create_widgets()

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="Новый расход", padding=10)
        input_frame.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=12)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var,
                                           values=["Еда", "Транспорт", "Развлечения"],
                                           state="readonly", width=15)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.category_combo.current(0)

        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(input_frame, textvariable=self.date_var, width=12)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        self.add_btn = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)

        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_category_var = tk.StringVar(value="Все")
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var,
                                         values=["Все", "Еда", "Транспорт", "Развлечения"],
                                         state="readonly", width=15)
        self.filter_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(filter_frame, text="Дата с:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.start_date_var = tk.StringVar()
        self.start_date_entry = ttk.Entry(filter_frame, textvariable=self.start_date_var, width=12)
        self.start_date_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(filter_frame, text="по:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.end_date_var = tk.StringVar()
        self.end_date_entry = ttk.Entry(filter_frame, textvariable=self.end_date_var, width=12)
        self.end_date_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        self.apply_filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.apply_filter_btn.grid(row=0, column=6, padx=5, pady=5)

        self.clear_filter_btn = ttk.Button(filter_frame, text="Сбросить", command=self.clear_filter)
        self.clear_filter_btn.grid(row=0, column=7, padx=5, pady=5)

        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("amount", "category", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        self.tree.column("amount", width=120, anchor="center")
        self.tree.column("category", width=150, anchor="center")
        self.tree.column("date", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        sum_frame = ttk.Frame(self.root)
        sum_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.sum_label = ttk.Label(sum_frame, text="Сумма за период: 0.00 руб.", font=("Arial", 11, "bold"))
        self.sum_label.pack(anchor="w")

        self.update_table()

    def validate_input(self, amount_str, date_str):
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом.")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом.")
            return False

        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ДД.ММ.ГГГГ (например, 01.01.2024).")
            return False

        return True

    def add_expense(self):
        amount_str = self.amount_var.get().strip()
        category = self.category_var.get().strip()
        date_str = self.date_var.get().strip()

        if not amount_str or not category or not date_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")
            return

        if not self.validate_input(amount_str, date_str):
            return

        expense = {
            "amount": float(amount_str),
            "category": category,
            "date": date_str
        }
        self.expenses.append(expense)

        self.amount_var.set("")
        self.category_combo.current(0)
        self.date_var.set("")

        self.save_data()
        self.update_table()

    def apply_filter(self):
        self.update_table()

    def clear_filter(self):
        self.filter_category_var.set("Все")
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.update_table()

    def get_filtered_expenses(self):
        filtered = self.expenses.copy()

        cat = self.filter_category_var.get()
        if cat and cat != "Все":
            filtered = [e for e in filtered if e["category"] == cat]

        start_str = self.start_date_var.get().strip()
        end_str = self.end_date_var.get().strip()

        if start_str:
            try:
                start_dt = datetime.strptime(start_str, "%d.%m.%Y")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%d.%m.%Y") >= start_dt]
            except ValueError:
                pass

        if end_str:
            try:
                end_dt = datetime.strptime(end_str, "%d.%m.%Y")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%d.%m.%Y") <= end_dt]
            except ValueError:
                pass

        return filtered

    def update_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtered = self.get_filtered_expenses()
        total = 0.0
        for e in filtered:
            self.tree.insert("", "end", values=(f"{e['amount']:.2f}", e["category"], e["date"]))
            total += e["amount"]

        self.sum_label.config(text=f"Сумма за период: {total:.2f} руб.")

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.expenses = []

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
