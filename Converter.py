import tkinter as tk
from tkinter import messagebox
import requests
import json
import os
from datetime import datetime

# Глобальные переменные
history = []
history_file = "history.json"
api_url = "https://api.exchangerate-api.com/v4/latest/"

#Загрузка истории из файла
def load_history():
    global history
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    else:
        history = []

#Сохранение истории в файл
def save_history():
    global history
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except:
        pass

#Обновление отображения истории
def update_history_display(history_listbox):
    history_listbox.delete(0, tk.END)
    for entry in history:
        history_listbox.insert(tk.END, entry)

#Добавление записи в историю
def add_to_history(from_curr, to_curr, amount, result, rate, history_listbox):
    global history
    time_str = datetime.now().strftime("%H:%M:%S")
    history_entry = f"{time_str} {amount:.2f} {from_curr} → {result:.2f} {to_curr}"

    history.insert(0, history_entry)

    if len(history) > 20:
        history = history[:20]

    update_history_display(history_listbox)
    save_history()

#Конвертация валюты
def convert_currency(amount_entry, from_var, to_var, result_label, convert_btn, history_listbox):
    amount_str = amount_entry.get().strip()
    if not amount_str:
        messagebox.showwarning("Ошибка", "Введите сумму")
        return

    try:
        amount = float(amount_str)
        if amount <= 0:
            messagebox.showwarning("Ошибка", "Сумма > 0")
            return
    except ValueError:
        messagebox.showwarning("Ошибка", "Введите число")
        return

    from_curr = from_var.get()
    to_curr = to_var.get()

    if from_curr == to_curr:
        result = amount
        rate = 1.0
        result_label.config(text=f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}")
        add_to_history(from_curr, to_curr, amount, result, rate, history_listbox)
        return

    convert_btn.config(state=tk.DISABLED, text="Загрузка...")

    try:
        response = requests.get(f"{api_url}{from_curr}", timeout=10)
        response.raise_for_status()
        data = response.json()

        rate = data['rates'].get(to_curr)
        if rate is None:
            messagebox.showerror("Ошибка", f"Валюта {to_curr} не найдена")
            return

        result = amount * rate
        result_label.config(text=f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}")
        add_to_history(from_curr, to_curr, amount, result, rate, history_listbox)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось получить курс")
    finally:
        convert_btn.config(state=tk.NORMAL, text="Конвертировать")

# Удаление истории
def clear_history(history_listbox):
    global history
    if messagebox.askyesno("Подтверждение", "Очистить историю?"):
        history = []
        update_history_display(history_listbox)
        save_history()

#Загрузка истории
def load_history_from_file(history_listbox):
    global history
    if os.path.exists(history_file):
        load_history()
        update_history_display(history_listbox)
        messagebox.showinfo("Информация", f"Загружено {len(history)} записей")
    else:
        messagebox.showinfo("Информация", "Файл не найден")


# Создание окна
root = tk.Tk()
root.title("Конвертер Валют")
root.geometry("420x500")
root.resizable(False, False)

currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'RUB']
load_history()

# Блок конвертации
convert_frame = tk.Frame(root, relief=tk.GROOVE, bd=2)
convert_frame.pack(pady=10, padx=10, fill=tk.X)

tk.Label(convert_frame, text="Конвертер", font=('Arial', 10, 'bold')).pack(pady=5)

# Строка 1: Сумма
row1 = tk.Frame(convert_frame)
row1.pack(pady=5)
tk.Label(row1, text="Сумма:").pack(side=tk.LEFT, padx=5)
amount_entry = tk.Entry(row1, width=10)
amount_entry.pack(side=tk.LEFT)

# Строка 2: Из и В
row2 = tk.Frame(convert_frame)
row2.pack(pady=5)

tk.Label(row2, text="Из:").pack(side=tk.LEFT, padx=5)
from_var = tk.StringVar(value="USD")
from_menu = tk.OptionMenu(row2, from_var, *currencies)
from_menu.pack(side=tk.LEFT, padx=5)

tk.Label(row2, text="В:").pack(side=tk.LEFT, padx=5)
to_var = tk.StringVar(value="EUR")
to_menu = tk.OptionMenu(row2, to_var, *currencies)
to_menu.pack(side=tk.LEFT, padx=5)

# Результат
result_label = tk.Label(convert_frame, text="", font=('Arial', 10, 'bold'), fg="blue")
result_label.pack(pady=5)

# Кнопка конвертации
convert_btn = tk.Button(convert_frame, text="Конвертировать", width=15, bg="#4CAF50", fg="white")
convert_btn.pack(pady=5)

# Блок истории (посередине)
history_frame = tk.Frame(root, relief=tk.GROOVE, bd=2)
history_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

tk.Label(history_frame, text="История", font=('Arial', 10, 'bold')).pack(pady=5)

# Список истории
history_listbox = tk.Listbox(history_frame, width=45, height=8)
history_listbox.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

# Скроллбар
scrollbar = tk.Scrollbar(history_listbox)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
history_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=history_listbox.yview)

# Блок кнопок управления (внизу)
buttons_frame = tk.Frame(root)
buttons_frame.pack(pady=10, padx=10, fill=tk.X)

tk.Button(buttons_frame, text="Очистить", width=10, bg="#f44336", fg="white",
          command=lambda: clear_history(history_listbox)).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

tk.Button(buttons_frame, text="Сохранить", width=10, bg="#2196F3", fg="white",
          command=save_history).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

tk.Button(buttons_frame, text="Загрузить", width=10, bg="#FF9800", fg="white",
          command=lambda: load_history_from_file(history_listbox)).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

# Настройка кнопки конвертации
convert_btn.config(command=lambda: convert_currency(
    amount_entry, from_var, to_var, result_label, convert_btn, history_listbox
))

# Привязка Enter
amount_entry.bind('<Return>', lambda e: convert_currency(
    amount_entry, from_var, to_var, result_label, convert_btn, history_listbox
))

update_history_display(history_listbox)

# Запуск приложения
root.mainloop()