import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)

        self.data_file = "expenses.json"
        self.expenses = []

        self.load_data()
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        input_frame = ttk.LabelFrame(main_frame, text="Добавление расхода", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=15)
        self.amount_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 20))

        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(input_frame, textvariable=self.category_var, width=15)
        self.category_combobox['values'] = ('Еда', 'Транспорт', 'Развлечения', 'Здоровье',
                                           'Образование', 'Одежда', 'Коммунальные услуги', 'Другое')
        self.category_combobox.grid(row=0, column=3, sticky=tk.W, pady=5, padx=(5, 20))

        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=4, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(input_frame, textvariable=self.date_var, width=15)
        self.date_entry.grid(row=0, column=5, sticky=tk.W, pady=5, padx=(5, 20))

        self.add_button = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        self.add_button.grid(row=0, column=6, sticky=tk.W, pady=5)

        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.filter_category_var = tk.StringVar()
        self.filter_category_combobox = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, width=15)
        self.filter_category_combobox['values'] = ('Все', 'Еда', 'Транспорт', 'Развлечения', 'Здоровье',
                                                   'Образование', 'Одежда', 'Коммунальные услуги', 'Другое')
        self.filter_category_combobox.set('Все')
        self.filter_category_combobox.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 20))

        ttk.Label(filter_frame, text="Дата с:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.start_date_var = tk.StringVar()
        self.start_date_entry = ttk.Entry(filter_frame, textvariable=self.start_date_var, width=15)
        self.start_date_entry.grid(row=0, column=3, sticky=tk.W, pady=5, padx=(5, 5))

        ttk.Label(filter_frame, text="по:").grid(row=0, column=4, sticky=tk.W, pady=5)
        self.end_date_var = tk.StringVar()
        self.end_date_entry = ttk.Entry(filter_frame, textvariable=self.end_date_var, width=15)
        self.end_date_entry.grid(row=0, column=5, sticky=tk.W, pady=5, padx=(5, 20))

        self.apply_filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.apply_filter_button.grid(row=0, column=6, sticky=tk.W, pady=5)

        self.clear_filter_button = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.clear_filter)
        self.clear_filter_button.grid(row=0, column=7, sticky=tk.W, pady=5, padx=(10, 0))

        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        columns = ('amount', 'category', 'date')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        self.tree.heading('amount', text='Сумма')
        self.tree.heading('category', text='Категория')
        self.tree.heading('date', text='Дата')

        self.tree.column('amount', width=150)
        self.tree.column('category', width=200)
        self.tree.column('date', width=150)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.delete_button = ttk.Button(main_frame, text="Удалить выбранный расход", command=self.delete_expense)
        self.delete_button.grid(row=3, column=0, sticky=tk.W, pady=10)

        sum_frame = ttk.LabelFrame(main_frame, text="Итого", padding="10")
        sum_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.total_label = ttk.Label(sum_frame, text="Общая сумма: 0.00 руб.", font=('Arial', 12, 'bold'))
        self.total_label.grid(row=0, column=0, sticky=tk.W)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.update_table()

    def validate_input(self, amount_str, date_str):
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом!")
            return False

        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ДД.ММ.ГГГГ (например, 01.01.2024)!")
            return False

        return True

    def add_expense(self):
        amount_str = self.amount_var.get().strip()
        category = self.category_var.get().strip()
        date_str = self.date_var.get().strip()

        if not amount_str or not category or not date_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        if not self.validate_input(amount_str, date_str):
            return

        amount = float(amount_str)

        expense = {
            'amount': amount,
            'category': category,
            'date': date_str
        }

        self.expenses.append(expense)

        self.amount_var.set("")
        self.category_var.set("")
        self.date_var.set("")

        self.save_data()
        self.update_table()

        messagebox.showinfo("Успех", "Расход добавлен!")

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите расход для удаления!")
            return

        index = self.tree.index(selected_item[0])

        if 0 <= index < len(self.expenses):
            del self.expenses[index]
            self.save_data()
            self.update_table()
            messagebox.showinfo("Успех", "Расход удален!")

    def apply_filter(self):
        self.update_table()

    def clear_filter(self):
        self.filter_category_var.set("Все")
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.update_table()

    def get_filtered_expenses(self):
        filtered = self.expenses.copy()

        category_filter = self.filter_category_var.get()
        if category_filter and category_filter != "Все":
            filtered = [exp for exp in filtered if exp['category'] == category_filter]

        start_date_str = self.start_date_var.get().strip()
        end_date_str = self.end_date_var.get().strip()

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%d.%m.%Y")
                filtered = [exp for exp in filtered if datetime.strptime(exp['date'], "%d.%m.%Y") >= start_date]
            except ValueError:
                pass

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%d.%m.%Y")
                filtered = [exp for exp in filtered if datetime.strptime(exp['date'], "%d.%m.%Y") <= end_date]
            except ValueError:
                pass

        return filtered

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtered_expenses = self.get_filtered_expenses()

        total_sum = 0
        for expense in filtered_expenses:
            self.tree.insert('', tk.END, values=(
                f"{expense['amount']:.2f}",
                expense['category'],
                expense['date']
            ))
            total_sum += expense['amount']

        self.total_label.config(text=f"Общая сумма: {total_sum:.2f} руб.")

    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.expenses = []

def main():
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
