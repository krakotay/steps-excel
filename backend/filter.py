import polars as pl

from config import OSV_SCHEMA

from excelsior import Scanner

from make_title import create_title_page_fast
from make_numeric import change_numeric_format_fast


def filting(
    filename: str,
    sheet_name: str,
    column: int,
    target_value: int,
    bank_name: str,
    date_start: str,
    date_end: str,
    boss_name: str,
):
    column_name = str(column)

    # Создаем имя для выходного файла
    out_filename = filename.replace(".xlsx", "_out.xlsx")

    # Читаем через polars
    df: pl.DataFrame = pl.read_excel(
        filename,
        sheet_name=sheet_name,
        read_options={"header_row": 3, "use_columns": "D:K"},
        schema_overrides=OSV_SCHEMA,
    )
    df = df.filter(df["Лицевой счет"].str.starts_with(column_name))

    df = df.with_columns(
        (pl.col("Исходящий руб.(Д)") + pl.col("Исходящий руб.(К)")).alias(
            "рабочий остаток"
        )
    )
    print(df)
    summary = df["рабочий остаток"].sum()
    target = target_value * float(summary) * 0.01
    filtered = df.filter(pl.col("рабочий остаток") >= target)

    sample = filtered["рабочий остаток"].sum()
    print(f"target: {target} | summary: {summary} | sample: {sample}")
    sample_df = pl.DataFrame({"сумма выборки": sample, "процент": sample / summary})

    # Запись в (уже скопированный) файл
    print("\nЗаписываем в копию файла...")

    # добавляем df / f"{sheet_name}_FILTERED"
    scanner = Scanner(filename)
    editor = scanner.open_editor(sheet_name)
    editor.add_worksheet(f"{sheet_name}_FILTERED").with_polars(df)
    editor = change_numeric_format_fast(editor).set_columns_width(["C", "D", "E", "F", "G", "H", "I"], 15)

    # добавляем filtered / f"{sheet_name}_FILTERED_{target_value}"
    editor.add_worksheet(f"{sheet_name}_FILTERED_{target_value}").with_polars(filtered)
    editor.add_worksheet("ВЫБОРКА").with_polars(sample_df)
    editor = change_numeric_format_fast(editor).set_columns_width(["C", "D", "E", "F", "G", "H", "I"], 15)

    if "Титульник" not in scanner.get_sheets():
        editor.add_worksheet_at("Титульник", 0)
    else:
        editor.with_worksheet("Титульник")
    editor = create_title_page_fast(editor, bank_name, date_start, date_end, boss_name)

    editor.save(out_filename)
    print(
        f"new_worksheets == {Scanner(out_filename).get_sheets()}"
    )

    print(f"Готово! Проверьте файл {out_filename}")
    return out_filename
