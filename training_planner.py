import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "trainings.json"

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x500")
        self.root.resizable(True, True)

        # Данные
        self.trainings = []
        self.load_data()

        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_table()
        self.create_button_frame()

        # Обновление таблицы
        self.refresh_table()

    def create_input_frame(self):
        """Форма для добавления тренировки"""
        frame = tk.LabelFrame(self.root, text="Добавить тренировку", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Дата
        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = tk.Entry(frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Тип тренировки
        tk.Label(frame, text="Тип тренировки:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(frame, textvariable=self.type_var, width=15)
        self.type_combo['values'] = ('Бег', 'Велосипед', 'Плавание', 'Силовая', 'Йога')
        self.type_combo.grid(row=0, column=3, padx=5, pady=5)
        self.type_combo.current(0)

        # Длительность
        tk.Label(frame, text="Длительность (мин):").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.duration_entry = tk.Entry(frame, width=10)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)

        # Кнопка добавления
        self.add_btn = tk.Button(frame, text="Добавить тренировку", command=self.add_training, bg="lightgreen")
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)

    def create_filter_frame(self):
        """Фильтры"""
        frame = tk.LabelFrame(self.root, text="Фильтры", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по типу
        tk.Label(frame, text="Тип тренировки:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.filter_type_var = tk.StringVar(value="Все")
        self.filter_type_combo = ttk.Combobox(frame, textvariable=self.filter_type_var, width=15)
        self.filter_type_combo['values'] = ('Все', 'Бег', 'Велосипед', 'Плавание', 'Силовая', 'Йога')
        self.filter_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_table())

        # Фильтр по дате
        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.filter_date_entry = tk.Entry(frame, width=15)
        self.filter_date_entry.grid(row=0, column=3, padx=5, pady=5)
        self.filter_date_entry.bind('<KeyRelease>', lambda e: self.refresh_table())

        # Кнопка сброса фильтров
        self.reset_btn = tk.Button(frame, text="Сбросить фильтры", command=self.reset_filters)
        self.reset_btn.grid(row=0, column=4, padx=10, pady=5)

    def create_table(self):
        """Таблица с тренировками"""
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Скроллбар
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        # Treeview
        columns = ("ID", "Дата", "Тип тренировки", "Длительность (мин)")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)

        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Тип тренировки", text="Тип тренировки")
        self.tree.heading("Длительность (мин)", text="Длительность (мин)")

        self.tree.column("ID", width=30)
        self.tree.column("Дата", width=100)
        self.tree.column("Тип тренировки", width=120)
        self.tree.column("Длительность (мин)", width=100)

        self.tree.pack(fill="both", expand=True)

        # Контекстное меню для удаления
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Удалить тренировку", command=self.delete_training)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def create_button_frame(self):
        """Кнопки сохранения/загрузки"""
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=5)

        self.save_btn = tk.Button(frame, text="Сохранить в JSON", command=self.save_to_json, bg="lightblue")
        self.save_btn.pack(side="left", padx=5)

        self.load_btn = tk.Button(frame, text="Загрузить из JSON", command=self.load_from_json, bg="lightyellow")
        self.load_btn.pack(side="left", padx=5)

        self.status_label = tk.Label(frame, text="Готово", fg="green")
        self.status_label.pack(side="right", padx=5)

    def add_training(self):
        """Добавление тренировки с проверкой"""
        date = self.date_entry.get().strip()
        training_type = self.type_var.get()
        duration = self.duration_entry.get().strip()

        # Валидация
        if not date or not training_type or not duration:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        # Проверка формата даты
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return

        # Проверка длительности
        try:
            duration_val = float(duration)
            if duration_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return

        # Добавление
        new_id = max([t["id"] for t in self.trainings], default=0) + 1
        self.trainings.append({
            "id": new_id,
            "date": date,
            "type": training_type,
            "duration": duration_val
        })

        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.duration_entry.delete(0, tk.END)

        self.refresh_table()
        self.status_label.config(text=f"Добавлена тренировка #{new_id}", fg="green")
        self.root.after(2000, lambda: self.status_label.config(text="Готово"))

    def delete_training(self):
        """Удаление выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления!")
            return

        item = self.tree.item(selected[0])
        training_id = item['values'][0]

        self.trainings = [t for t in self.trainings if t["id"] != training_id]
        self.refresh_table()
        self.status_label.config(text=f"Удалена тренировка #{training_id}", fg="orange")

    def refresh_table(self):
        """Обновление таблицы с учетом фильтров"""
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Фильтрация
        filtered = self.trainings.copy()

        # Фильтр по типу
        filter_type = self.filter_type_var.get()
        if filter_type != "Все":
            filtered = [t for t in filtered if t["type"] == filter_type]

        # Фильтр по дате
        filter_date = self.filter_date_entry.get().strip()
        if filter_date:
            filtered = [t for t in filtered if t["date"] == filter_date]

        # Отображение
        for training in filtered:
            self.tree.insert("", "end", values=(
                training["id"],
                training["date"],
                training["type"],
                training["duration"]
            ))

        self.status_label.config(text=f"Показано {len(filtered)} из {len(self.trainings)} тренировок", fg="blue")

    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_type_var.set("Все")
        self.filter_date_entry.delete(0, tk.END)
        self.refresh_table()

    def show_context_menu(self, event):
        """Показ контекстного меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def save_to_json(self):
        """Сохранение в JSON"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=2)
            self.status_label.config(text=f"Сохранено в {DATA_FILE}", fg="green")
            messagebox.showinfo("Успех", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_from_json(self):
        """Загрузка из JSON"""
        if not os.path.exists(DATA_FILE):
            messagebox.showwarning("Предупреждение", f"Файл {DATA_FILE} не найден!")
            return

        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                self.trainings = json.load(f)
            self.refresh_table()
            self.status_label.config(text=f"Загружено из {DATA_FILE}", fg="green")
            messagebox.showinfo("Успех", f"Загружено {len(self.trainings)} тренировок")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

    def load_data(self):
        """Автозагрузка при старте"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.trainings = json.load(f)
            except:
                self.trainings = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
