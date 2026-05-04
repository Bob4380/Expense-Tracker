import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

# Основные данные
expenses = []

# Функции для работы с JSON
def load_data():
    global expenses
    try:
        with open('expenses.json', 'r') as f:
            expenses = json.load(f)
    except FileNotFoundError:
        expenses = []

def save_data():
    with open('expenses.json', 'w') as f:
        json.dump(expenses, f, indent=4)

# Функция добавления расхода
def add_expense():
    try:
        amount = float(entry_amount.get())
        category = entry_category.get()
        date_str = entry_date.get()

        # Проверка суммы
        if amount <= 0:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
            return

        # Проверка даты
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты. Используйте ГГГГ-ММ-ДД.")
            return

        expense = {
            'amount': amount,
            'category': category,
            'date': date_str
        }
        expenses.append(expense)
        update_table()
        save_data()
        clear_entries()
    except ValueError:
        messagebox.showerror("Ошибка", "Проверьте правильность ввода данных.")

def clear_entries():
    entry_amount.delete(0, tk.END)
    entry_category.delete(0, tk.END)
    entry_date.delete(0, tk.END)

# Обновление таблицы
def update_table():
    for row in tree.get_children():
        tree.delete(row)
    for expense in expenses:
        tree.insert('', tk.END, values=(expense['amount'], expense['category'], expense['date']))

# Фильтрация
def filter_expenses():
    category_filter = combo_category_filter.get()
    date_filter = entry_date_filter.get()

    filtered = expenses
    if category_filter != 'Все':
        filtered = [e for e in filtered if e['category'] == category_filter]
    if date_filter:
        try:
            datetime.strptime(date_filter, '%Y-%m-%d')
            filtered = [e for e in filtered if e['date'] == date_filter]
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты для фильтра.")
            return

    for row in tree.get_children():
        tree.delete(row)
    for expense in filtered:
        tree.insert('', tk.END, values=(expense['amount'], expense['category'], expense['date']))

# Подсчёт суммы за период
def calculate_sum():
    total = 0
    for item in tree.get_children():
        values = tree.item(item, 'values')
        total += float(values[0])
    label_total.config(text=f"Общая сумма: {total:.2f}")

# Инициализация GUI
load_data()

root = tk.Tk()
root.title("Expense Tracker")

# Поля ввода
tk.Label(root, text="Сумма").grid(row=0, column=0)
entry_amount = tk.Entry(root)
entry_amount.grid(row=0, column=1)

tk.Label(root, text="Категория").grid(row=1, column=0)
entry_category = tk.Entry(root)
entry_category.grid(row=1, column=1)

tk.Label(root, text="Дата (ГГГГ-ММ-ДД)").grid(row=2, column=0)
entry_date = tk.Entry(root)
entry_date.grid(row=2, column=1)

btn_add = tk.Button(root, text="Добавить расход", command=add_expense)
btn_add.grid(row=3, column=0, columnspan=2, pady=5)

# Таблица
columns = ('Сумма', 'Категория', 'Дата')
tree = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)
tree.grid(row=4, column=0, columnspan=2)

update_table()

# Фильтрация
tk.Label(root, text="Фильтр по категории").grid(row=5, column=0)
category_options = ['Все'] + list({e['category'] for e in expenses})
combo_category_filter = ttk.Combobox(root, values=category_options)
combo_category_filter.current(0)
combo_category_filter.grid(row=5, column=1)

tk.Label(root, text="Фильтр по дате (ГГГГ-ММ-ДД)").grid(row=6, column=0)
entry_date_filter = tk.Entry(root)
entry_date_filter.grid(row=6, column=1)

btn_filter = tk.Button(root, text="Применить фильтр", command=filter_expenses)
btn_filter.grid(row=7, column=0, columnspan=2, pady=5)

# Подсчёт суммы
btn_sum = tk.Button(root, text="Подсчитать сумму", command=calculate_sum)
btn_sum.grid(row=8, column=0, columnspan=2)

label_total = tk.Label(root, text="Общая сумма: 0.00")
label_total.grid(row=9, column=0, columnspan=2)

# Запуск приложения
root.mainloop()
