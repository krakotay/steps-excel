from excelsior import Editor


def change_numeric_format_fast(
    editor: Editor,
    columns: list[str] = ["C:", "D:", "E:", "F:", "G:", "H:", "I:"],
) -> Editor:
    for column in columns:
        editor = editor.set_number_format(column, "#,##0.00")
    return editor
