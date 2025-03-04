import shutil
import pandas as pd
import polars as pl


def filting(file, sheet_name: str, column: int, target_value: int):
    filename: str = file.name
    column_name = str(column)

    # Создаем имя для выходного файла
    out_filename = filename.replace(".xlsx", "_out.xlsx")
    # Копируем в out-файл
    shutil.copy(filename, out_filename)
    print(f"Создана копия файла: {out_filename}")

    # Читаем через polars
    df = pl.read_excel(out_filename, sheet_name=sheet_name)
    df = df.filter(df["Лицевой счет"].str.starts_with(column_name))

    df = df.with_columns(
        (pl.col("исходящий актив") + pl.col("исходящий пассив")).alias(
            "рабочий остаток"
        )
    )
    summary = df["рабочий остаток"].sum()
    target = target_value * summary * 0.01
    filtered = df.filter(pl.col("рабочий остаток") >= target)
    sample = filtered["рабочий остаток"].sum()
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
        )
        filtered.to_pandas().to_excel(
            writer,
            sheet_name=f"{sheet_name}_FILTERED_{target_value}",
            index=False,
        )
        sample_df.to_pandas().to_excel(
            writer,
            sheet_name="ВЫБОРКА",
            index=False,
        )

    print(f"Готово! Проверьте файл {out_filename}")
    return out_filename
