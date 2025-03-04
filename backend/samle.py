import shutil
import pandas as pd
import polars as pl

# Функция обработки Excel файла, аналогичная твоей консольной реализации
def sample_process(file, sheet_name: str, start: int, green_const: int, yellow_const: int):
    # Gradio передаёт загруженный файл как объект с атрибутом .name
    filename: str = file.name
    out_filename = filename.replace(".xlsx", "_out.xlsx")
    shutil.copy(filename, out_filename)
    print(f"Создана копия файла: {out_filename}")

    # Читаем исходный лист через polars
    print("Читаем исходный лист...")
    df = pl.read_excel(out_filename, sheet_name=sheet_name)
    total_rows = df.height
    print(f"Всего строк: {total_rows}")

    # Берем строки, начиная с указанной
    df = df[start:].with_row_index()
    total_rows = df.height

    # Вычисляем шаги для фильтрации
    step_yellow = max(1, total_rows // yellow_const)
    step_green = max(1, (total_rows - total_rows // step_yellow) // green_const)

    # Определяем маски для выборки
    yellow_mask = pl.col("index") % step_yellow == 0
    green_mask = (~yellow_mask) & (pl.col("index") % step_green == 0)

    # Фильтрация данных
    yellow_df = df.filter(yellow_mask).drop("index")
    green_df = df.filter(green_mask).drop("index")

    print(f"Строк в YELLOW: {len(yellow_df)}")
    print(f"Строк в GREEN: {len(green_df)}")

    # Записываем данные в новый лист в скопированном файле
    with pd.ExcelWriter(
        out_filename, mode="a", engine="openpyxl", if_sheet_exists="overlay"
    ) as writer:
        yellow_df.to_pandas().to_excel(
            writer,
            sheet_name=f"{sheet_name}_YELLOW_{len(yellow_df)}_{step_yellow}",
            index=False,
        )
        green_df.to_pandas().to_excel(
            writer,
            sheet_name=f"{sheet_name}_GREEN_{len(green_df)}_{step_green}",
            index=False,
        )

    print(f"Готово! Проверьте файл {out_filename}")
    return out_filename
def scan_excel(file, sheet_name):
    filename = file.name
    df = pl.read_excel(filename, sheet_name=sheet_name)
    total_rows = df.height
    start = sum(int(digit) for digit in str(total_rows))
    return start, total_rows

# Обёртка для Gradio, чтобы возвращать путь к файлу и лог
def process_file(file, sheet_name, start, green_const, yellow_const):
    try:
        out_path = sample_process(
            file, sheet_name, int(start), int(green_const), int(yellow_const)
        )
        log = f"Обработка завершена. Файл сохранён по пути: {out_path}"
    except Exception as e:
        out_path = None
        log = f"Ошибка: {e}"
    return out_path, log
