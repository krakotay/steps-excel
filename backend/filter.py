import shutil
import pandas as pd
import polars as pl
from make_title import create_title_page
from config import OSV_SCHEMA
from decimal import Decimal
from make_numeric import change_numeric_format

def filting(
    file,
    sheet_name: str,
    column: int,
    target_value: int,
    bank_name: str,
    date_start: str,
    date_end: str,
    boss_name: str,
):
    filename: str = file.name
    column_name = str(column)

    # Создаем имя для выходного файла
    out_filename = filename.replace(".xlsx", "_out.xlsx")
    # Копируем в out-файл
    shutil.copy(filename, out_filename)
    print(f"Создана копия файла: {out_filename}")

    # Читаем через polars
    df = pl.read_excel(
        out_filename,
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
    filtered = df.filter(pl.col("рабочий остаток") >= Decimal(str(target)))

    sample = filtered["рабочий остаток"].sum()
    print(f"target: {target} | summary: {summary} | sample: {sample}")
    sample_df = pl.DataFrame({"сумма выборки": sample, "процент": sample / summary})

    # Запись в (уже скопированный) файл
    print("\nЗаписываем в копию файла...")

    with pd.ExcelWriter(
        out_filename, mode="a", engine="openpyxl", if_sheet_exists="overlay"
    ) as writer:
        df.to_pandas().to_excel(
            writer,
            sheet_name=f"{sheet_name}_FILTERED",
            index=False,
            float_format="%.2f",
        )
        change_numeric_format(writer.book, f"{sheet_name}_FILTERED")
        filtered.to_pandas().to_excel(
            writer,
            sheet_name=f"{sheet_name}_FILTERED_{target_value}",
            index=False,
            float_format="%.2f",

        )
        change_numeric_format(writer.book, f"{sheet_name}_FILTERED_{target_value}")

        sample_df.to_pandas().to_excel(
            writer,
            sheet_name="ВЫБОРКА",
            index=False,
            float_format="%.2f",

        )
        change_numeric_format(writer.book, "ВЫБОРКА")
        create_title_page(writer.book, bank_name, date_start, date_end, boss_name)

    # Добавляем титульный лист

    print(f"Готово! Проверьте файл {out_filename}")
    return out_filename
