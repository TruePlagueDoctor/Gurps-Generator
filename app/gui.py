import tkinter as tk
from tkinter import ttk, messagebox

from app.generator import generate_character, format_character

ARCHETYPE_CHOICES = {
    "Сбалансированный": "generalist",
    "Воин": "warrior",
    "Учёный": "scholar",
    "Переговорщик": "negotiator",
    "Разведчик": "scout",
}



class GurpsGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GURPS генератор персонажа")
        self.geometry("800x600")

        # Основной фрейм параметров
        params_frame = ttk.LabelFrame(self, text="Параметры генерации")
        params_frame.pack(fill="x", padx=10, pady=10)

        # Имя
        ttk.Label(params_frame, text="Имя персонажа:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.name_var = tk.StringVar(value="Безымянный")
        ttk.Entry(params_frame, textvariable=self.name_var, width=25).grid(
            row=0, column=1, sticky="w", padx=5, pady=5
        )

        # Очки
        ttk.Label(params_frame, text="Очки персонажа:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.points_var = tk.StringVar(value="100")
        ttk.Entry(params_frame, textvariable=self.points_var, width=10).grid(
            row=1, column=1, sticky="w", padx=5, pady=5
        )

        # TL
        ttk.Label(params_frame, text="Технический уровень (TL):").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.tl_var = tk.StringVar(value="3")
        ttk.Entry(params_frame, textvariable=self.tl_var, width=10).grid(
            row=2, column=1, sticky="w", padx=5, pady=5
        )

        # Чекбоксы
        self.allow_super_var = tk.BooleanVar(value=False)
        self.allow_supernatural_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            params_frame,
            text="Разрешить суперспособности",
            variable=self.allow_super_var,
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=2)

        ttk.Checkbutton(
            params_frame,
            text="Разрешить сверхъестественные черты/магия",
            variable=self.allow_supernatural_var,
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=2)

        # Кнопка генерации
        generate_button = ttk.Button(
            params_frame,
            text="Сгенерировать персонажа",
            command=self.on_generate,
        )
        generate_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Растягивание по сетке
        for i in range(2):
            params_frame.columnconfigure(i, weight=1)

        # Поле вывода листа персонажа
        output_frame = ttk.LabelFrame(self, text="Лист персонажа")
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.output_text = tk.Text(output_frame, wrap="word", font=("Consolas", 10))
        self.output_text.pack(fill="both", expand=True, side="left")

        # Скроллбар
        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.output_text.configure(yscrollcommand=scrollbar.set)

        ttk.Label(params_frame, text="Архетип:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.archetype_var = tk.StringVar(value="Сбалансированный")
        arch_cb = ttk.Combobox(
            params_frame,
            textvariable=self.archetype_var,
            values=list(ARCHETYPE_CHOICES.keys()),
            state="readonly",
            width=25,
        )
        arch_cb.grid(row=3, column=1, sticky="w", padx=5, pady=5)




    def on_generate(self):
        """Обработчик кнопки 'Сгенерировать персонажа'."""
        try:
            total_points = int(self.points_var.get())
            tl = int(self.tl_var.get())
        except ValueError:
            messagebox.showerror(
                "Ошибка", "Очки персонажа и TL должны быть целыми числами."
            )
            return

        if total_points <= 0:
            messagebox.showerror(
                "Ошибка", "Количество очков должно быть больше нуля."
            )
            return

        name = self.name_var.get().strip() or "Безымянный"
        allow_super = self.allow_super_var.get()
        allow_supernatural = self.allow_supernatural_var.get()

        ui_arch = self.archetype_var.get()
        archetype = ARCHETYPE_CHOICES.get(ui_arch, "generalist")

        char = generate_character(
            total_points=total_points,
            tl=tl,
            allow_super=allow_super,
            allow_supernatural=allow_supernatural,
            name=name,
            archetype=archetype,
        )


        sheet = format_character(char)

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, sheet)


if __name__ == "__main__":
    app = GurpsGeneratorApp()
    app.mainloop()
