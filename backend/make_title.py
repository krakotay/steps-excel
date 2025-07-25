from excelsior import Editor, AlignSpec, HorizAlignment, VertAlignment



def create_title_page_fast(
    editor: Editor, bank_name: str, date_start: str, date_end: str, boss_name: str
):
    editor.set_border("B4:D12", "thin")

    editor.set_column_width("A", 5).set_column_width("B", 15).set_column_width(
        "C", 40
    ).set_column_width("D", 15).set_column_width("E", 5)

    editor.set_cell("B4", "РАБОЧИЕ ДОКУМЕНТЫ АУДИТОРА")
    editor.merge_cells("B4:D4")
    editor.set_font(
        "B4",
        "Times New Roman",
        16,
        True,
        False,
        AlignSpec(HorizAlignment.Center, VertAlignment.Center),
    )

    editor.set_cell("B6", f"по аудиту {bank_name}")
    editor.merge_cells("B6:D6")
    editor.set_font(
        "B6",
        "Times New Roman",
        14,
        False,
        False,
        AlignSpec(HorizAlignment.Center, VertAlignment.Center),
    )

    editor.set_cell("B8", f"за период с {date_start} по {date_end}")
    editor.merge_cells("B8:D8")
    editor.set_font(
        "B8",
        "Times New Roman",
        12,
        False,
        False,
        AlignSpec(HorizAlignment.Center, VertAlignment.Center),
    )

    editor.set_cell("B12", boss_name)
    editor.merge_cells("B12:D12")
    editor.set_font(
        "B12",
        "Times New Roman",
        12,
        False,
        False,
        AlignSpec(HorizAlignment.Center, VertAlignment.Center),
    )

    editor.set_cell("B11", "Руководитель проверки:")
    editor.set_font(
        "B11",
        "Times New Roman",
        12,
        False,
        False,
        AlignSpec(HorizAlignment.Left, VertAlignment.Center),
    )

    return editor
