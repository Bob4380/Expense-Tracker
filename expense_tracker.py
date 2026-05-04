import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")
        
        self.expenses = []
        self.filename = "expenses.json"
        
        self.load_data()
        self.create_widgets()
        self.refresh_table()
    
    def create_widgets(self):
        # Фрейм для ввода данных
        input_frame = tk.LabelFrame(self.root, text="Добавить расход", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Сумма
        tk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w")
        self.amount_entry = tk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5)
        
        # Категория
        tk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky="w")
        self.category_var = tk.StringVar()
        categories = ["еда", "транспорт", "развлечения", "здоровье", "одежда", "другое"]
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, 
                                           values=categories, width=12)
        self.category_combo.grid(row=0, column=3, padx=5)
        self.category_combo.set(categories[0])
        
        # Дата
        tk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=4, sticky="w")
        self.date_entry = tk.Entry(input_frame, width=12)
        self.date_entry.grid(row=0, column=5, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        
        # Кнопка добавления
        self.add_button = tk.Button(input_frame, text="Добавить расход", 
                                    command=self.add_expense, bg="#4CAF50", fg="white")
        self.add_button.grid(row=0, column=6, padx=20)
        
        # Фрейм для фильтрации
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по категории
        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0, sticky="w")
        self.filter_category_var = tk.StringVar(value="Все")
        filter_categories = ["Все"] + ["еда", "транспорт", "развлечения", "здоровье", "одежда", "другое"]
        self.filter_category_combo = ttk.Combobox(filter_frame, 
                                                   textvariable=self.filter_category_var,
                                                   values=filter_categories, width=12)
        self.filter_category_combo.grid(row=0, column=1, padx=5)
        
        # Фильтр по дате
        tk.Label(filter_frame, text="С даты:").grid(row=0, column=2, sticky="w")
        self.date_from_entry = tk.Entry(filter_frame, width=12)
        self.date_from_entry.grid(row=0, column=3, padx=5)
        
        tk.Label(filter_frame, text="По дату:").grid(row=0, column=4, sticky="w")
        self.date_to_entry = tk.Entry(filter_frame, width=12)
        self.date_to_entry.grid(row=0, column=5, padx=5)
        
        # Кнопка фильтрации
        self.filter_button = tk.Button(filter_frame, text="Применить фильтр", 
                                       command=self.refresh_table, bg="#2196F3", fg="white")
        self.filter_button.grid(row=0, column=6, padx=20)
        
        # Кнопка сброса фильтра
        self.reset_button = tk.Button(filter_frame, text="Сбросить", 
                                      command=self.reset_filter, bg="#FF5722", fg="white")
        self.reset_button.grid(row=0, column=7, padx=5)
        
        # Таблица расходов
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("id", "amount", "category", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("id", text="№")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        
        self.tree.column("id", width=50)
        self.tree.column("amount", width=100)
        self.tree.column("category", width=150)
        self.tree.column("date", width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Фрейм для итоговой суммы
        summary_frame = tk.Frame(self.root)
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        self.summary_label = tk.Label(summary_frame, text="Итого за период: 0.00 руб.", 
                                      font=("Arial", 12, "bold"))
        self.summary_label.pack()
    
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
            return True
        except ValueError:
            return False
    
    def validate_amount(self, amount_str):
        try:
            amount = float(amount_str)
            return amount > 0
        except ValueError:
            return False
    
    def add_expense(self):
        amount = self.amount_entry.get().strip()
        category = self.category_var.get().strip()
        date = self.date_entry.get().strip()
        
        # Валидация
        if not amount or not category or not date:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return
        
        if not self.validate_amount(amount):
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
            return
        
        if category not in ["еда", "транспорт", "развлечения", "здоровье", "одежда", "другое"]:
            messagebox.showerror("Ошибка", "Выберите категорию из списка!")
            return
        
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ДД.ММ.ГГГГ!")
            return
        
        # Добавление расхода
        expense = {
            "id": len(self.expenses) + 1,
            "amount": float(amount),
            "category": category,
            "date": date
        }
        
        self.expenses.append(expense)
        self.save_data()
        self.refresh_table()
        
        # Очистка полей
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        
        messagebox.showinfo("Успех", "Расход добавлен!")
    
    def get_filtered_expenses(self):
        filtered = self.expenses.copy()
        
        # Фильтр по категории
        filter_category = self.filter_category_var.get()
        if filter_category != "Все":
            filtered = [e for e in filtered if e["category"] == filter_category]
        
        # Фильтр по дате
        date_from = self.date_from_entry.get().strip()
        date_to = self.date_to_entry.get().strip()
        
        if date_from:
            if not self.validate_date(date_from):
                messagebox.showerror("Ошибка", "Неверный формат даты 'С даты'!")
                return None
            from_date = datetime.strptime(date_from, "%d.%m.%Y")
            filtered = [e for e in filtered 
                       if datetime.strptime(e["date"], "%d.%m.%Y") >= from_date]
        
        if date_to:
            if not self.validate_date(date_to):
                messagebox.showerror("Ошибка", "Неверный формат даты 'По дату'!")
                return None
            to_date = datetime.strptime(date_to, "%d.%m.%Y")
            filtered = [e for e in filtered 
                       if datetime.strptime(e["date"], "%d.%m.%Y") <= to_date]
        
        return filtered
    
    def refresh_table(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение отфильтрованных данных
        filtered_expenses = self.get_filtered_expenses()
        if filtered_expenses is None:
            return
        
        # Заполнение таблицы
        total_sum = 0
        for i, expense in enumerate(filtered_expenses, 1):
            self.tree.insert("", "end", values=(
                i, 
                f"{expense['amount']:.2f}", 
                expense['category'], 
                expense['date']
            ))
            total_sum += expense['amount']
        
        # Обновление итоговой суммы
        self.summary_label.config(text=f"Итого за период: {total_sum:.2f} руб.")
    
    def reset_filter(self):
        self.filter_category_var.set("Все")
        self.date_from_entry.delete(0, tk.END)
        self.date_to_entry.delete(0, tk.END)
        self.refresh_table()
    
    def save_data(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
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
