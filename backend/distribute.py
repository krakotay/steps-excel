import polars as pl
from make_title import create_title_page_fast
from make_numeric import apply_numeric_format_to_columns
from excelsior import Scanner
from config import OSV_SCHEMA
def process_disribute(
    filename: str,
    sheet_name: str,
    len_number: int,
    bank_name: str,
    date_start: str,
    date_end: str,
    boss_name: str,
):
    # Создаем имя для выходного файла
    out_filename = filename.replace(".xlsx", "_out.xlsx")

    # Читаем через polars
    df: pl.DataFrame = pl.read_excel(
        filename,
        sheet_name=sheet_name,
        read_options={"header_row": 3, "use_columns": "D:K"},
        schema_overrides=OSV_SCHEMA,
    )
    df = df.with_columns(
        pl.nth(0).str.slice(0, length=int(len_number)).alias('short')
    )
    index_list: list[str] = sorted(df['short'].unique().to_list())
    scanner = Scanner(filename)
    editor = scanner.open_editor(sheet_name)
    for index in index_list:
        print('ws_' + index)
        editor.add_worksheet(index).with_polars(df.filter(pl.col('short') == index).drop('short'))
        editor = apply_numeric_format_to_columns(editor, columns = ["C:", "D:", "E:", "F:", "G:", "H:"])
    if "Титульник" not in scanner.get_sheets():
        editor.add_worksheet_at("Титульник", 0)
    else:
        editor.with_worksheet("Титульник")
    editor = create_title_page_fast(editor, bank_name, date_start, date_end, boss_name)
    editor.save(out_filename)
    return out_filename



