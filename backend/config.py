import polars as pl

OSV_SCHEMA = pl.Schema(
    {
        "Лицевой счет": pl.String,
        "Наименование счета": pl.String,
        "Входящий руб.(Д)": pl.Decimal(scale=2),
        "Входящий руб.(К)": pl.Decimal(scale=2),
        "Оборот руб.(Д)": pl.Decimal(scale=2),
        "Оборот руб.(К)": pl.Decimal(scale=2),
        "Исходящий руб.(Д)": pl.Decimal(scale=2),
        "Исходящий руб.(К)": pl.Decimal(scale=2),
    }
)


if __name__ == "__main__":
    # df = pl.DataFrame(
    #     {
    #         "Лицевой счет": "123",
    #         "Наименование счета": "123",
    #         "Входящий руб.(Д)": 1,
    #         "Входящий руб.(К)": "1.0",
    #         "Оборот руб.(Д)": "1.0",
    #         "Исходящий руб.(Д)": 0.1,
    #         "Исходящий руб.(К)": 0.2,
    #     },
    #     schema=OSV_SCHEMA,
    # )

    df = pl.read_excel(
        "test.xlsx",
        read_options={"header_row": 3, "use_columns": "D:K"},
        schema_overrides=OSV_SCHEMA,
    )
    print(df)
