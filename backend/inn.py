import polars as pl
from make_title import create_title_page_fast
from make_numeric import apply_numeric_format_to_columns
from excelsior import Scanner

def filter_by_inn(
    filename: str,
    bank_name: str,
    date_start: str,
    date_end: str,
    boss_name: str,
    sheet_input: str,
    main_col_name: str,
):
    output_filename: str = filename.replace(".xlsx", "_out.xlsx")
    df = pl.read_excel(filename, sheet_name=sheet_input)

    filtered = (
        df.select(main_col_name, "Сумма")
        .drop_nulls()
        .with_columns(pl.col(main_col_name).str.strip_chars().replace("", "БЕЗ_ИНН"))
    )
    aggregated_df = filtered.group_by(main_col_name).agg(
        [
            pl.len().alias("количество"),
            pl.sum("Сумма").round(2).alias("сумма"),
        ]
    )

    total_sum = aggregated_df["сумма"].sum()
    aggregated_df = aggregated_df.with_columns(
        [(pl.col("сумма") * 100 / total_sum).round(2).alias("процент")]
    ).sort(by="сумма", descending=True)
    scanner = Scanner(filename)
    editor = scanner.open_editor(sheet_input)
    editor.add_worksheet(f'ИНН агрегированные {sheet_input}').with_polars(aggregated_df)
    editor = apply_numeric_format_to_columns(editor, columns=['C:', 'D:'])
    if "Титульник" not in scanner.get_sheets():
        editor.add_worksheet_at("Титульник", 0)
    else:
        editor.with_worksheet("Титульник")
    editor = create_title_page_fast(editor, bank_name, date_start, date_end, boss_name)

    inns = aggregated_df[main_col_name].to_list()
    print("inns", inns)
    editor.save(output_filename)
    return aggregated_df, output_filename, inns


def filter_by_inn_split(
    filename: str,
    bank_name: str,
    date_start: str,
    date_end: str,
    boss_name: str,
    sheet_input: str,
    main_col_name: str,
    inns_list: list[str],
):
    output_filename: str = filename.replace(".xlsx", "_out.xlsx")
    df = pl.read_excel(output_filename, sheet_name=sheet_input).with_row_index()
    scanner = Scanner(filename)
    editor = scanner.open_editor(sheet_input)
    for inn in inns_list:
        df_filtered = df.filter(
            pl.col(main_col_name).str.strip_chars().replace("", "БЕЗ_ИНН") == inn
        ).drop("index")
        editor = editor.add_worksheet(inn.strip()).with_polars(df_filtered)
        editor = apply_numeric_format_to_columns(editor, columns=['F:', 'G:'])

    if "Титульник" not in scanner.get_sheets():
        editor.add_worksheet_at("Титульник", 0)
    else:
        editor.with_worksheet("Титульник")
    editor = create_title_page_fast(editor, bank_name, date_start, date_end, boss_name)
    editor.save(output_filename)

    # # Добавляем титульный лист

    return output_filename
