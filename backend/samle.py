import shutil
import pandas as pd
import polars as pl
from make_title import create_title_page
from make_numeric import change_numeric_format

# Функция обработки Excel файла, аналогичная твоей консольной реализации
def sample_process(
    file,
    sheet_name: str,
    start: int,
    green_const: int,
    yellow_const: int,
    bank_name: str,
    date_start: str,
    date_end: str,
    boss_name: str,
):
    # Gradio передаёт загруженный файл как объект с атрибутом .name
    filename: str = file.name
    out_filename = filename.replace(".xlsx", "_out.xlsx")
    shutil.copy(filename, out_filename)
    print(f"Создана копия файла: {out_filename}")
    yield f"Создана копия файла: {out_filename}", None
    # Читаем исходный лист через polars
    print("Читаем исходный лист...")
    df = pl.read_excel(
        out_filename,
        sheet_name=sheet_name,
    )[start:]
    if "index" in df.columns:
        df = df.drop("index")
    df = df.with_row_index()
    total_rows = df.height
    print(f"Всего строк: {total_rows}")

    # Берем строки, начиная с указанной
    # df = df.slice(start - 1)  # Начинаем с start-1 (например, с 18-й строки для start=19)
    print("df после slice:", df)

    # Делаем систематическую выборку для yellow
    yellow_df = df.filter(pl.col("index") % yellow_const == 0)
    print("yellow_df:", yellow_df)
    filtered = (
        df.filter(~pl.col("index").is_in(yellow_df["index"]))
        .drop("index")
        .with_row_index()
    )
    print("filtered:", filtered)
    green_df = filtered.filter(pl.col("index") % green_const == 0)
    print("green_df:", green_df)
    print(f"Строк в YELLOW: {yellow_df.height}")
    print(f"Строк в GREEN: {green_df.height}")
    # print("yellow_df:", yellow_df)
    # print("green_df:", green_df)
    # Записываем данные в новый лист в скопированном файле
    print("Записываем данные в новый лист в скопированном файле")
    yield "Записываем данные в новый лист в скопированном файле", None
    with pd.ExcelWriter(
        out_filename, mode="a", engine="openpyxl", if_sheet_exists="overlay"
    ) as writer:
        yellow_df.drop("index").to_pandas().to_excel(
            writer,
            sheet_name=f"{sheet_name}_YELLOW_{len(yellow_df)}_{yellow_df.height}",
            index=False,
            float_format="%.2f",
        )
        change_numeric_format(writer.book, f"{sheet_name}_YELLOW_{len(yellow_df)}_{yellow_df.height}")
        green_df.drop("index").to_pandas().to_excel(
            writer,
            sheet_name=f"{sheet_name}_GREEN_{len(green_df)}_{green_df.height}",
            index=False,
            float_format="%.2f",
        )
        change_numeric_format(writer.book, f"{sheet_name}_GREEN_{len(green_df)}_{green_df.height}")
        print("Добавляем титульный лист")
        yield "Добавляем титульный лист", None

        create_title_page(writer.book, bank_name, date_start, date_end, boss_name)

    print(f"Готово! Проверьте файл {out_filename}")
    yield f"Готово! Проверьте файл {out_filename}", out_filename


def scan_excel(file, sheet_name):
    filename = file.name
    df = pl.read_excel(filename, sheet_name=sheet_name)
    total_rows = df.height
    start = sum(int(digit) for digit in str(total_rows))
    return start, total_rows
