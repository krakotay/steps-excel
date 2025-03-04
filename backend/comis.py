import shutil
from typing import Literal
import pandas as pd
import polars as pl
import itertools
from tqdm import tqdm
import numpy as np
from make_title import create_title_page

INCOME = []
with open("../income.txt", "r") as inc:
    INCOME = [i[:-1] for i in inc.readlines()]
EXPENSE = []
with open("../expense.txt", "r") as inc:
    EXPENSE = [i[:-1] for i in inc.readlines()]


def best_subset(values: np.ndarray, target: float):
    n = len(values)
    best_sum = None
    best_diff = np.inf
    best_subset_indices = None

    # Перебираем все подмножества по их размеру (от 1 до n)
    for r in tqdm(range(1, n + 1), desc="Перебор комбинаций"):
        # Получаем все комбинации индексов размера r
        comb_indices = np.array(list(itertools.combinations(range(n), r)))
        # Если комбинаций нет — пропускаем (хотя здесь всегда будет, если r>=1)
        if comb_indices.size == 0:
            continue

        # Вычисляем сумму для каждой комбинации через numpy (массово, без цикла)
        subset_sums = np.sum(values[comb_indices], axis=1)
        # Вычисляем абсолютную разницу между суммой подмножества и целевым значением
        diffs = np.abs(target - subset_sums)

        # Находим индекс минимальной разницы в этом батче
        min_idx = np.argmin(diffs)
        if diffs[min_idx] < best_diff:
            best_diff = diffs[min_idx]
            best_sum = subset_sums[min_idx]
            best_subset_indices = comb_indices[min_idx]
            # Если решение достаточно близкое (ошибка <= 5%), выходим сразу
            if (diffs[min_idx] / target) <= 0.05:
                return values[list(best_subset_indices)], best_sum

    return values[list(best_subset_indices)], best_sum


type Abbr = Literal[
    "входящий актив",
    "входящий пассив",
    "исходящий актив",
    "исходящий пассив",
]  # актив - доход, пассив - расход


def filter_by_target_percent(
    df: pl.DataFrame, writer: pd.ExcelWriter, value: int, column: str
):
    COLUMN = column
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
        largest_df.to_pandas().to_excel(
            writer,
            sheet_name=f"LARGEST_{value}_PERCENT",
            index=False,
        )
        df = df.join(largest_df, on=COLUMN, how="anti")
        target = df[COLUMN].sum() * value * 0.01
        sample += largest_df[COLUMN].sum()
        print(f"Пересчитанная цель: {target}")

    df_values = df[COLUMN].filter(df[COLUMN] > 0).to_numpy()
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
    filtered.to_pandas().to_excel(
        writer,
        sheet_name=f"FILTERED_BY_{value}_PERCENT",
        index=False,
    )
    sample_df = pl.DataFrame(
        {"сумма выборки": sample, "процент": sample / original_sum}
    )
    sample_df.to_pandas().to_excel(
        writer,
        sheet_name="ВЫБОРКА",
        index=False,
    )

    print("С большим количеством элементов готово!")
    return log_output


def comiss(
    file,
    sheet_name: str,
    type_value: Literal["Доход", "Расход"],
    target_value: int,
    timevalue: Literal["Первый", "Не первый"],
    bank_name: str,
    date_start: str,
    date_end: str,
    boss_name: str,
):
    filename: str = file.name
    # Создаем имя для выходного файла
    out_filename = filename.replace(".xlsx", "_out.xlsx")
    # Копируем в out-файл
    shutil.copy(filename, out_filename)
    print(f"Создана копия файла: {out_filename}")

    # Читаем через polars
    df = pl.read_excel(out_filename, sheet_name=sheet_name)
    value = ""
    match type_value:
        case "Доход":
            value = INCOME
        case "Расход":
            value = EXPENSE
    print(f"values = {value}")
    df = df.filter(df["Лицевой счет"].str.starts_with("706"))
    filtered = df.filter(df["Лицевой счет"].str.contains_any(value))
    if timevalue == "Не первый":
        COLUMN = "рабочий остаток"
        if type_value == "Доход":
            INP: Abbr = "входящий пассив"
            OUT: Abbr = "исходящий пассив"
        else:
            INP: Abbr = "входящий актив"
            OUT: Abbr = "исходящий актив"
        filtered = filtered.with_columns((filtered[OUT] - filtered[INP]).alias(COLUMN))
    else:
        if type_value == "Доход":
            COLUMN: Abbr = "исходящий пассив"
        else:
            COLUMN: Abbr = "исходящий актив"

    print("Отфильтрованный: ", filtered)

    # Запись в (уже скопированный) файл
    print("\nЗаписываем в копию файла...")

    # Открываем writer один раз и пишем оба листа
    with pd.ExcelWriter(
        out_filename, mode="a", engine="openpyxl", if_sheet_exists="overlay"
    ) as writer:
        filtered.to_pandas().to_excel(
            writer,
            sheet_name=f"{sheet_name}_FILTERED",
            index=False,
        )
        log_output = filter_by_target_percent(
            filtered, writer, target_value, COLUMN
        )

    # Добавляем титульный лист
    create_title_page(out_filename, bank_name, date_start, date_end, boss_name)

    print(f"Готово! Проверьте файл {out_filename}")
    return out_filename, log_output
