"""Tkinter-интерфейс с переключателем золотой сетки."""
import tkinter as tk
from tkinter import filedialog

from .validator import validate_group_input, auto_suggest_from_single
from .generator import create_garden
from .visualizer import draw_garden


class GardenApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        # Настройка по умолчанию: золотая сетка выключена
        self.show_golden_grid = tk.BooleanVar(value=False)

    # ---------- ПОДНЯТЬ ОКНО ПОВЕРХ ----------
    def _popup(self, win):
        win.deiconify()
        win.lift()
        win.attributes('-topmost', True)
        win.update_idletasks()
        win.update()
        win.focus_force()
        win.grab_set()
        win.after(200, lambda: win.attributes('-topmost', False))

    # ---------- ДИАЛОГ ВВОДА ----------
    def ask_groups(self):
        win = tk.Toplevel(self.root)
        win.title("Сад Рёандзи — ввод")
        win.geometry("560x360")
        win.resizable(False, False)

        result = {"value": None}

        tk.Label(
            win,
            text="Введите количество камней в группах через пробел:",
            font=("Segoe UI", 11, "bold"),
            pady=10
        ).pack()

        tk.Label(
            win,
            text="Например: 5 2 3 2 3   (классика Рёандзи, 15 камней)\n"
                 "Или введите одно число N — предложу варианты разбиения.",
            font=("Segoe UI", 9),
            fg="#555",
            justify=tk.LEFT
        ).pack(padx=15, pady=(0, 10))

        entry = tk.Entry(win, font=("Consolas", 13), justify=tk.CENTER)
        entry.pack(fill=tk.X, padx=20, pady=5)
        entry.focus_set()
        entry.insert(0, "5 2 3 2 3")
        entry.select_range(0, tk.END)

        error_label = tk.Label(win, text="", fg="red", font=("Segoe UI", 9))
        error_label.pack()

        # ---- Переключатель золотой сетки ----
        options_frame = tk.Frame(win, pady=10)
        options_frame.pack()
        tk.Checkbutton(
            options_frame,
            text="📐 Показать золотую сетку (для архитекторов)",
            variable=self.show_golden_grid,
            font=("Segoe UI", 10)
        ).pack(anchor='w')

        def on_ok(event=None):
            text = entry.get().strip()
            if not text:
                result["value"] = None
                win.destroy()
                return
            text = text.replace(',', ' ').replace(';', ' ')
            try:
                nums = [int(x) for x in text.split() if x.strip()]
            except ValueError:
                error_label.config(text="❌ Только целые числа через пробел")
                return
            result["value"] = nums
            win.destroy()

        def on_cancel(event=None):
            result["value"] = None
            win.destroy()

        btn_frame = tk.Frame(win, pady=10)
        btn_frame.pack()
        tk.Button(btn_frame, text="Далее →", width=14,
                  font=("Segoe UI", 10, "bold"),
                  command=on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", width=14,
                  font=("Segoe UI", 10),
                  command=on_cancel).pack(side=tk.LEFT, padx=5)

        win.bind("<Return>", on_ok)
        win.bind("<Escape>", on_cancel)
        win.protocol("WM_DELETE_WINDOW", on_cancel)

        self._popup(win)
        self.root.wait_window(win)
        return result["value"]

    # ---------- ДИАЛОГ ВЫБОРА ВАРИАНТА ----------
    def ask_variant(self, n, variants):
        win = tk.Toplevel(self.root)
        win.title(f"Варианты для {n} камней")
        win.geometry("540x400")
        win.resizable(False, False)

        result = {"groups": None}

        tk.Label(
            win,
            text=f"💡 Варианты распределения {n} камней:",
            font=("Segoe UI", 11, "bold"),
            pady=10
        ).pack()

        listbox = tk.Listbox(win, font=("Consolas", 11), height=10,
                             activestyle='none', selectmode=tk.SINGLE)
        for name, groups in variants:
            listbox.insert(tk.END,
                           f"  {name}:  {groups}  (сумма = {sum(groups)})")
        listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        listbox.selection_set(0)
        listbox.activate(0)
        listbox.focus_set()

        def on_ok(event=None):
            sel = listbox.curselection()
            if not sel:
                return
            result["groups"] = variants[sel[0]][1]
            win.destroy()

        def on_cancel(event=None):
            result["groups"] = None
            win.destroy()

        btn_frame = tk.Frame(win, pady=10)
        btn_frame.pack()
        tk.Button(btn_frame, text="Выбрать", width=14,
                  font=("Segoe UI", 10, "bold"),
                  command=on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Назад", width=14,
                  font=("Segoe UI", 10),
                  command=on_cancel).pack(side=tk.LEFT, padx=5)

        listbox.bind("<Double-Button-1>", on_ok)
        win.bind("<Return>", on_ok)
        win.bind("<Escape>", on_cancel)
        win.protocol("WM_DELETE_WINDOW", on_cancel)

        self._popup(win)
        self.root.wait_window(win)
        return result["groups"]

    # ---------- ДИАЛОГ АНАЛИЗА ----------
    def show_analysis(self, groups, status, message, suggestions):
        win = tk.Toplevel(self.root)
        win.title("Анализ распределения")
        win.geometry("600x480")
        win.resizable(False, False)

        colors = {
            'ok': '#2e7d32',
            'warning': '#ef6c00',
            'suggestion': '#1565c0',
            'error': '#c62828',
        }
        icons = {
            'ok': '✅',
            'warning': '⚠️',
            'suggestion': '💡',
            'error': '❌',
        }
        titles = {
            'ok': 'ГАРМОНИЧНО',
            'warning': 'ПРЕДУПРЕЖДЕНИЕ',
            'suggestion': 'ЕСТЬ ИДЕЯ',
            'error': 'ОШИБКА',
        }

        # Заголовок с цветом статуса
        header = tk.Frame(win, bg=colors[status], height=55)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(
            header,
            text=f"{icons[status]}  {titles[status]}",
            font=("Segoe UI", 14, "bold"),
            fg="white", bg=colors[status]
        ).pack(pady=14)

        # Тело
        text_frame = tk.Frame(win)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        tk.Label(
            text_frame,
            text=f"Распределение: {groups}\nВсего камней: {sum(groups)}",
            font=("Segoe UI", 10, "bold"),
            justify=tk.LEFT
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            text_frame,
            text=message,
            font=("Segoe UI", 10),
            justify=tk.LEFT,
            wraplength=560
        ).pack(anchor='w', pady=(0, 10))

        if suggestions:
            tk.Label(
                text_frame,
                text="💡 Предложения:",
                font=("Segoe UI", 10, "bold"),
                justify=tk.LEFT
            ).pack(anchor='w', pady=(0, 4))
            for s in suggestions:
                tk.Label(
                    text_frame,
                    text=f"  • {s}",
                    font=("Segoe UI", 9),
                    justify=tk.LEFT,
                    wraplength=560
                ).pack(anchor='w')

        # Результат
        result = {"ok": status != 'error'}

        def on_ok():
            result["ok"] = True
            win.destroy()

        def on_cancel():
            result["ok"] = False
            win.destroy()

        btn_frame = tk.Frame(win, pady=12)
        btn_frame.pack(side=tk.BOTTOM)

        if status == 'error':
            tk.Button(btn_frame, text="Понятно",
                      width=14, font=("Segoe UI", 10, "bold"),
                      command=on_cancel).pack(side=tk.LEFT, padx=5)
        elif status in ('warning', 'suggestion'):
            tk.Button(btn_frame, text="Продолжить",
                      width=14, font=("Segoe UI", 10, "bold"),
                      bg="#4caf50", fg="white",
                      command=on_ok).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Изменить",
                      width=14, font=("Segoe UI", 10),
                      command=on_cancel).pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(btn_frame, text="Далее →",
                      width=14, font=("Segoe UI", 10, "bold"),
                      bg="#4caf50", fg="white",
                      command=on_ok).pack(side=tk.LEFT, padx=5)

        win.bind("<Return>", lambda e: on_ok())
        win.bind("<Escape>", lambda e: on_cancel())
        win.protocol("WM_DELETE_WINDOW", on_cancel)

        self._popup(win)
        self.root.wait_window(win)
        return result["ok"]

    # ---------- ДИАЛОГ СОХРАНЕНИЯ ----------
    def ask_save_path(self):
        self.root.lift()
        self.root.focus_force()
        path = filedialog.asksaveasfilename(
            title="Сохранить сад как PNG",
            defaultextension=".png",
            filetypes=[("PNG-изображение", "*.png"),
                       ("Все файлы", "*.*")],
            initialfile="ryoanji_garden.png",
            parent=self.root
        )
        return path if path else None

    # ---------- ОКНО «ЕЩЁ САД?» ----------
    def ask_again(self):
        win = tk.Toplevel(self.root)
        win.title("Готово!")
        win.geometry("420x200")
        win.resizable(False, False)

        result = {"again": False}

        tk.Label(
            win,
            text="🌸 Сад создан!\nСоздать ещё один?",
            font=("Segoe UI", 12, "bold"),
            pady=20
        ).pack()

        def yes():
            result["again"] = True
            win.destroy()

        def no():
            result["again"] = False
            win.destroy()

        btn_frame = tk.Frame(win, pady=10)
        btn_frame.pack()
        tk.Button(btn_frame, text="Да", width=12,
                  font=("Segoe UI", 10, "bold"),
                  bg="#4caf50", fg="white",
                  command=yes).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Выход", width=12,
                  font=("Segoe UI", 10),
                  command=no).pack(side=tk.LEFT, padx=5)

        win.bind("<Return>", lambda e: yes())
        win.bind("<Escape>", lambda e: no())
        win.protocol("WM_DELETE_WINDOW", no)

        self._popup(win)
        self.root.wait_window(win)
        return result["again"]

    # ---------- ПРОСТОЕ ОКНО ОШИБКИ ----------
    def _simple_error(self, text):
        win = tk.Toplevel(self.root)
        win.title("Ошибка")
        win.geometry("460x180")
        win.resizable(False, False)

        tk.Label(
            win, text="❌ " + text,
            font=("Segoe UI", 11),
            wraplength=420, pady=25
        ).pack()

        def close():
            win.destroy()

        tk.Button(win, text="OK", width=12,
                  font=("Segoe UI", 10, "bold"),
                  command=close).pack(pady=10)

        win.bind("<Return>", lambda e: close())
        win.bind("<Escape>", lambda e: close())
        win.protocol("WM_DELETE_WINDOW", close)

        self._popup(win)
        self.root.wait_window(win)

    # ---------- ГЛАВНЫЙ ЦИКЛ ----------
    def run(self):
        try:
            while True:
                groups = self.ask_groups()
                if groups is None:
                    break

                if not groups:
                    continue

                if any(n < 0 for n in groups):
                    self._simple_error("Числа должны быть положительными.")
                    continue

                # Одиночное число → предложить варианты
                if len(groups) == 1:
                    n = groups[0]
                    if n <= 0:
                        self._simple_error("Число должно быть > 0.")
                        continue
                    variants = auto_suggest_from_single(n)
                    if not variants:
                        self._simple_error(
                            f"Не могу предложить разбиение для {n} камней."
                        )
                        continue
                    chosen = self.ask_variant(n, variants)
                    if chosen is None:
                        continue
                    groups = chosen

                # Валидация
                status, message, suggestions = validate_group_input(groups)
                if not self.show_analysis(groups, status, message, suggestions):
                    continue

                # Сохранение
                save_path = self.ask_save_path()

                # Генерация + отрисовка
                stones, w, h = create_garden(groups)
                title_extra = f"Группы: {groups} | Всего: {sum(groups)}"
                draw_garden(
                    stones, w, h,
                    title_extra=title_extra,
                    save_path=save_path,
                    show_golden_grid=self.show_golden_grid.get()
                )

                if not self.ask_again():
                    break
        except Exception as e:
            import traceback
            traceback.print_exc()
            try:
                self._simple_error(f"{type(e).__name__}: {e}")
            except Exception:
                pass
        finally:
            try:
                self.root.destroy()
            except Exception:
                pass