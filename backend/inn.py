import polars as pl


def filter_by_inn(file):
    filename: str = file.name
    output_filename = filename.replace('.xlsx', "_out.xlsx")
    df = pl.read_excel(filename)

    filtered = df[['ИНН', "Сумма операции"]].drop_nulls()
    aggregated_df = filtered.group_by("ИНН").agg([
        pl.len().alias("количество"),
        pl.sum("Сумма операции").alias("сумма")
    ])
    aggregated_df.write_excel(output_filename)
    return aggregated_df, output_filename
def filter_by_sample(file, sample_interval: int):
    filename: str = file.name
    output_filename = filename.replace('.xlsx', "_out.xlsx")
    df = pl.read_excel(filename).with_row_index()
    
    total_rows = df.height
    start = sum(int(digit) for digit in str(total_rows))
    df = df[start:]
    filtered = df.filter((pl.col("index") - 1) % sample_interval == start).drop('index')
    filtered.write_excel(output_filename)
    return output_filename
