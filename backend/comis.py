from typing import Literal
import polars as pl
import numpy as np
from make_title import create_title_page_fast
import os
from make_numeric import apply_numeric_format_to_columns
from excelsior import Scanner, Editor
base_dir = os.path.dirname(__file__)
income_path = os.path.join(base_dir, "../income.txt")
expense_path = os.path.join(base_dir, "../expense.txt")

INCOME = []
with open(income_path, "r") as inc:
    INCOME = [i[:-1] for i in inc.readlines()]
EXPENSE = []
with open(expense_path, "r") as inc:
    EXPENSE = [i[:-1] for i in inc.readlines()]


def best_subset(values_arr: np.ndarray, target: float):
    """
    Берет элементы из 'values' последовательно, пока их сумма
    не станет больше или равна 'target'.
    """
    # Если цель не положительная, ничего не берем
    if target <= 0:
        return [], target

    # Если список пуст, ничего не возвращаем
    if values_arr.size == 0:
        return [], target

    # Вычисляем нарастающую сумму
    cumsum = np.cumsum(values_arr)

    # Находим индекс, где нарастающая сумма впервые достигает или превышает цель.
    # np.searchsorted эффективно находит этот индекс в отсортированном массиве (cumsum отсортирован).
    k = np.searchsorted(cumsum, target)

    # Если k выходит за пределы массива, это означает, что сумма всех значений
    # меньше цели. В этом случае мы берем все значения.
    if k >= len(values_arr):
        subset = values_arr
    else:
        # В противном случае мы берем срез до найденного индекса включительно.
        subset = values_arr[: k + 1]

    # Вычисляем остаток от цели
    remaining_target = target - subset.sum()

    return subset, remaining_target


type Abbr = Literal[
    "Входящий руб.(К)",
    "Входящий руб.(Д)",
    "Исходящий руб.(К)",
    "Исходящий руб.(Д)",
]


def filter_by_target_percent(
    df: pl.DataFrame, editor: Editor, value: int, column: str
) -> tuple[str, Editor]:
    COLUMN = column
    df = df.with_columns(pl.col(COLUMN).cast(pl.Float64).round(2))
    df = df.sort(by=COLUMN)
    target = df[COLUMN].sum()
    original_sum = target
    sample = 0
    print(f"Сумма: {target}")
    target = value * target * 0.01
    print(f"Цель: {target}")
    largest_df = df.filter(df[COLUMN] >= target)
    if not largest_df.is_empty():
        print("выношу в отдельный лист")
        editor.add_worksheet(f"LARGEST_{value}_PERCENT").with_polars(largest_df)

        editor = apply_numeric_format_to_columns(editor)

        df = df.join(largest_df, on=COLUMN, how="anti")
        target = float(df[COLUMN].sum()) * value * 0.01
        sample += float(largest_df[COLUMN].sum())
        print(f"Пересчитанная цель: {target}")

    df_values = (
        df[COLUMN].filter(df[COLUMN] > 0).sort(descending=True).to_numpy()
    )
    column_summ = df[COLUMN].sum()
    if column_summ > target:
        best_sub, summary = best_subset(df_values, target)
        print(best_sub, summary)
        filtered = df.filter(df[COLUMN] > 0)
        filtered = filtered.filter(filtered[COLUMN].is_in(best_sub))
    else:
        filtered = df.filter(df[COLUMN] > 0)
    print(filtered)
    sample += filtered[COLUMN].sum()
    # print("Сумма что получилась: ", filtered[COLUMN].sum())
    log_output = (
        f"Цель была: {target}, получилось {filtered[COLUMN].sum()}, или {100 * filtered[COLUMN].sum() / target}% от ожидаемого"
        if target != 0.0
        else "Там ноль"
    )
    editor.add_worksheet(f"FILTERED_BY_{value}_PERCENT").with_polars(filtered)
    editor = apply_numeric_format_to_columns(editor)
    sample_df = pl.DataFrame(
        {"сумма выборки": sample, "процент": sample / original_sum}
    )
    editor.add_worksheet("ВЫБОРКА").with_polars(sample_df)
    editor = apply_numeric_format_to_columns(editor)

    print("С большим количеством элементов готово!")
    return log_output, editor


def process_706_account_data(
    filename: str,
    sheet_name: str,
    type_value: Literal["Доход", "Расход"],
    target_value: int,
    timevalue: Literal["Первый", "Не первый"],
    bank_name: str,
    date_start: str,
    date_end: str,
    boss_name: str,
):
    # Создаем имя для выходного файла
    out_filename = filename.replace(".xlsx", "_out.xlsx")

    # Читаем через polars
    df = pl.read_excel(
        filename,
        sheet_name=sheet_name,
        read_options={"header_row": 3, "use_columns": "D:K"},
    )
    value = ""
    match type_value:
        case "Доход":
            value = INCOME
        case "Расход":
            value = EXPENSE
    print(f"values = {value}")
    df = df.filter(df["Лицевой счет"].str.starts_with("706"))
    print(df)
    filtered = df.filter(df["Лицевой счет"].str.contains_any(value))

    if timevalue == "Не первый":
        COLUMN = "рабочий остаток"
        if type_value == "Доход":
            INP: Abbr = "Входящий руб.(К)"
            OUT: Abbr = "Исходящий руб.(К)"
        else:
            INP: Abbr = "Входящий руб.(Д)"
            OUT: Abbr = "Исходящий руб.(Д)"
        filtered = filtered.with_columns((filtered[OUT] + filtered[INP]).alias(COLUMN))
    else:
        if type_value == "Доход":
            COLUMN: Abbr = "Исходящий руб.(К)"
        else:
            COLUMN: Abbr = "Исходящий руб.(Д)"

    print("Отфильтрованный: ", filtered)
    if filtered[COLUMN].sum() == 0:
        return None, "Внимание! Деление на ноль!"
    # Запись в (уже скопированный) файл
    print("\nЗаписываем в копию файла...")
    scanner = Scanner(filename)
    editor = scanner.open_editor(sheet_name)
    editor.add_worksheet(f"{sheet_name}_FILTERED").with_polars(filtered)
    editor = apply_numeric_format_to_columns(editor)
    log_output, editor = filter_by_target_percent(filtered, editor, target_value, COLUMN)
    if "Титульник" not in scanner.get_sheets():
        editor.add_worksheet_at("Титульник", 0)
    else:
        editor.with_worksheet("Титульник")

    editor = create_title_page_fast(editor, bank_name, date_start, date_end, boss_name)
    editor.save(out_filename)
    print(f"Готово! Проверьте файл {out_filename}")
    return out_filename, log_output
