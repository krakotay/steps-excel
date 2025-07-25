import polars as pl
from make_title import create_title_page_fast
from make_numeric import apply_numeric_format_to_columns
from excelsior import Scanner
# Функция обработки Excel файла, аналогичная твоей консольной реализации
def process_excel_report(
    filename: str,
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
    out_filename = filename.replace(".xlsx", "_out.xlsx")
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
    print("Записываем данные в новый лист в скопированном файле")
    yield "Записываем данные в новый лист в скопированном файле", None
    scanner = Scanner(filename)
    editor = scanner.open_editor(sheet_name)
    editor.add_worksheet(f"{sheet_name}_YELLOW_{len(yellow_df)}_{yellow_df.height}").with_polars(yellow_df.drop("index"))
    editor = apply_numeric_format_to_columns(editor)

    editor.add_worksheet(f"{sheet_name}_GREEN_{len(green_df)}_{green_df.height}").with_polars(green_df.drop("index"))
    editor = apply_numeric_format_to_columns(editor)
    if "Титульник" not in scanner.get_sheets():
        editor.add_worksheet_at("Титульник", 0)
    else:
        editor.with_worksheet("Титульник")
    editor = create_title_page_fast(editor, bank_name, date_start, date_end, boss_name)

    editor.save(out_filename)


    print(f"Готово! Проверьте файл {out_filename}")
    yield f"Готово! Проверьте файл {out_filename}", out_filename


def calculate_initial_row_params(filename: str, sheet_name):
    df = pl.read_excel(filename, sheet_name=sheet_name)
    total_rows = df.height
    start = sum(int(digit) for digit in str(total_rows))
    return start, total_rows
