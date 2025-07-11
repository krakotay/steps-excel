import shutil
import polars as pl
import pandas as pd
from make_title import create_title_page
from make_numeric import change_numeric_format


def filter_by_inn(file, bank_name: str, date_start: str, date_end: str, boss_name: str):
    filename: str = file.name
    output_filename = filename.replace('.xlsx', "_out.xlsx")
    shutil.copy(filename, output_filename)
    df = pl.read_excel(output_filename)

    filtered = df[['ИНН', "Сумма операции"]].drop_nulls()
    aggregated_df = filtered.group_by("ИНН").agg([
        pl.len().alias("количество"),
        pl.sum("Сумма операции").alias("сумма"),
    ])
    
    total_sum = aggregated_df["сумма"].sum()
    aggregated_df = aggregated_df.with_columns([
        (pl.col("сумма") * 100 / total_sum).round(2).alias("процент")
    ]).sort(by="сумма", descending=True)
    with pd.ExcelWriter(
        output_filename, mode="a", engine="openpyxl", if_sheet_exists="overlay"
    ) as writer:
        aggregated_df.to_pandas().to_excel(
            writer,
            sheet_name="ИНН агрегированные",
            index=False,
            float_format="%.2f",
        )
        change_numeric_format(writer.book, "ИНН агрегированные")

        create_title_page(writer.book, bank_name, date_start, date_end, boss_name)
    inns = aggregated_df["ИНН"].to_list()
    print("inns", inns)
    return aggregated_df, output_filename, inns

def filter_by_inn_split(file, bank_name: str, date_start: str, date_end: str, boss_name: str, inns_list: list[str]):
    filename: str = file.name
    output_filename = filename.replace('.xlsx', "_out.xlsx")
    df = pl.read_excel(output_filename, sheet_id=2).with_row_index()
    with pd.ExcelWriter(
        output_filename, mode="a", engine="openpyxl", if_sheet_exists="overlay"
    ) as writer:
        for inn in inns_list:
            df_filtered = df.filter(pl.col("ИНН") == inn)
            df_filtered.drop("index").to_pandas().to_excel(
                writer,
                sheet_name=inn.strip(),
                index=False,
                float_format="%.2f",
            )
            change_numeric_format(writer.book, inn.strip())

        create_title_page(writer.book, bank_name, date_start, date_end, boss_name)

    
    # Добавляем титульный лист
    
    return output_filename
