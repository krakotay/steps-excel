import gradio as gr
from samle import process_excel_report, calculate_initial_row_params
from comis import process_706_account_data
from inn import filter_by_inn, filter_by_inn_split
from filter import process_account_filter_report
from distribute import process_disribute, scan_disribute
import polars as pl
from datetime import datetime

# Создаем интерфейс с использованием Gradio Blocks и вкладок
with gr.Blocks() as app:
    dt_now = datetime.now()

    gr.HTML("""<h1 style="color: darkgreen;">ООО КНК</h1>""")
    bank_name = gr.Textbox(label="Название аудироемого лица", value="Авангард")
    date_value_start = gr.Textbox(
        label="Период проверки, начало",
        value=datetime(dt_now.year, 1, 1).strftime("%d-%m-%Y"),
    )
    date_value_end = gr.Textbox(
        label="Период проверки, конец", value=dt_now.strftime("%d-%m-%Y")
    )
    boss_name = gr.Textbox(
        label="Руководитель проверки", value="Ельхимова Татьяна Викторовна"
    )
    with gr.Tabs():
        with gr.TabItem("Балансовый счет"):
            gr.Markdown("## Фильтрация по балансовому счету")
            with gr.Row():
                file_input = gr.File(
                    label="Загрузите Excel файл (.xlsx)", file_types=[".xlsx"]
                )
                column_number = gr.Number(label="Цифры начала", value=706, precision=0)
                sheet_input = gr.Textbox(label="Название листа", value="Приложение_ОСВ")
                target_value = gr.Number(
                    label="Сколько процентов от суммы нужно?", value=40, precision=0
                )

            process_button = gr.Button("Запустить процесс")
            download_output = gr.File(label="Скачать обработанный файл")

            process_button.click(
                process_account_filter_report,
                inputs=[
                    file_input,
                    sheet_input,
                    column_number,
                    target_value,
                    bank_name,
                    date_value_start,
                    date_value_end,
                    boss_name,
                ],
                outputs=[download_output],
            )

        with gr.TabItem("Метод систематической выборки (по шагам)"):
            gr.Markdown("ОСВ")
            with gr.Row():
                file_input = gr.File(
                    label="Загрузите Excel файл (.xlsx)", file_types=[".xlsx"]
                )
                sheet_input = gr.Textbox(label="Название листа", value="706")
            with gr.Row():
                scan_button = gr.Button("Сканировать Excel файл")
                start_input = gr.Number(
                    label="Начать со строчки номер", value=1, precision=0
                )
                rows = gr.Textbox(label="Высота, строчек", interactive=False)
            with gr.Row():
                green_input = gr.Number(
                    label="Интервал в GREEN?", value=10, precision=0
                )
                yellow_input = gr.Number(
                    label="Интервал в YELLOW?", value=10, precision=0
                )
            process_button = gr.Button("Запустить процесс")
            download_output = gr.File(label="Скачать обработанный файл")
            output_text = gr.Textbox(label="Лог выполнения", interactive=False)

            scan_button.click(
                calculate_initial_row_params,
                inputs=[file_input, sheet_input],
                outputs=[start_input, rows],
            )
            process_button.click(
                process_excel_report,
                inputs=[
                    file_input,
                    sheet_input,
                    start_input,
                    green_input,
                    yellow_input,
                    bank_name,
                    date_value_start,
                    date_value_end,
                    boss_name,
                ],
                outputs=[output_text, download_output],
            )

        with gr.TabItem("706 по символам"):
            with gr.Row():
                file_input = gr.File(
                    label="Загрузите Excel файл (.xlsx)", file_types=[".xlsx"]
                )
                sheet_input = gr.Textbox(label="Название листа", value="Приложение_ОСВ")
            with gr.Row():
                type_value = gr.Radio(
                    ["Доход", "Расход"], label="Выберите тип", value="Расход"
                )
                timevalue = gr.Radio(
                    ["Первый", "Не первый"], label="Этап", value="Первый"
                )
                target_value = gr.Number(
                    label="Сколько процентов от суммы нужно?", value=40, precision=0
                )
            process_button = gr.Button("Запустить процесс")
            download_output = gr.File(label="Скачать обработанный файл")
            log_percentage = gr.Textbox(label="Результаты", interactive=False)

            process_button.click(
                process_706_account_data,
                inputs=[
                    file_input,
                    sheet_input,
                    type_value,
                    target_value,
                    timevalue,
                    bank_name,
                    date_value_start,
                    date_value_end,
                    boss_name,
                ],
                outputs=[download_output, log_percentage],
            )

        with gr.TabItem("фильтрация по ИНН"):
            # gr.Markdown("## Метка 3")

            with gr.Row():
                file_input = gr.File(
                    label="Загрузите Excel файл (.xlsx)", file_types=[".xlsx"]
                )
                with gr.Column():
                    sheet_input = gr.Radio(
                        label="Название листа",
                        choices=["дебет", "кредит"],
                        value="дебет",
                    )
                    main_col_name = gr.Textbox(
                        label="Название столбца", value="ИНН контрагента"
                    )
                    process_button = gr.Button("Запустить процесс")
                download_output = gr.File(label="Скачать обработанный файл")

            dataframe = gr.Dataframe(
                type="polars",
                interactive=False,
                wrap=True,  # Оборачиваем текст
            )
            inn_list_show = gr.CheckboxGroup(label="Выбранные ИНН", interactive=True)

            with gr.Row():
                download_filtered = gr.File(label="Скачать выборку")
                process_filter_button = gr.Button("Выгрузить выборку по листам")

            def update_inn_list(df: pl.DataFrame, main_col_name: str):
                if df is not None and not df.is_empty():
                    # Предполагаем, что в df есть столбец с ИНН
                    inn_values = df[main_col_name].unique(maintain_order=True).to_list()
                    return gr.CheckboxGroup(choices=inn_values, value=None)
                return gr.CheckboxGroup(choices=[])

            process_button.click(
                fn=filter_by_inn,
                inputs=[
                    file_input,
                    bank_name,
                    date_value_start,
                    date_value_end,
                    boss_name,
                    sheet_input,
                    main_col_name,
                ],
                outputs=[dataframe, download_output, inn_list_show],
            ).then(
                fn=update_inn_list,
                inputs=[dataframe, main_col_name],
                outputs=[inn_list_show],
            )

            # Фильтрация по шагам
            process_filter_button.click(
                filter_by_inn_split,
                inputs=[
                    file_input,
                    bank_name,
                    date_value_start,
                    date_value_end,
                    boss_name,
                    sheet_input,
                    main_col_name,
                    inn_list_show,
                ],
                outputs=[download_filtered],
            )
        with gr.TabItem("Раскадровка"):
            def update_accounts_list(df: pl.DataFrame):
                if df is None or df.is_empty():
                    return gr.CheckboxGroup(choices=[], value=[])
                accounts = df["счет"].unique(maintain_order=True).to_list()
                # По умолчанию — ничего не выбрано (или можно выбрать всё, если хочешь)
                return gr.CheckboxGroup(choices=accounts, value=[])

            def toggle_all(current_selected: list[str], df: pl.DataFrame):
                if df is None or df.is_empty():
                    return []
                all_accounts = df["счет"].unique(maintain_order=True).to_list()
                if set(current_selected) == set(all_accounts):
                    # Всё уже выбрано — снимаем выделение
                    return []
                else:
                    # Выделяем все
                    return all_accounts

            file_input = gr.File(
                label="Загрузите Excel файл (.xlsx)", file_types=[".xlsx"]
            )
            sheet_input = gr.Textbox(label="Название листа", value="Приложение_ОСВ")
            len_number = gr.Number(label="Сколько цифр", value=3, precision=0)


            scan_button = gr.Button("Сканировать")

            with gr.Row():
                df_output = gr.Dataframe(type="polars", label="Сколько получилось", interactive=False)
                with gr.Column():
                    accounts_list = gr.CheckboxGroup(label="Выбранные счета", choices=[], value=[])
                    toggle_button = gr.Button("Выделить всё / снять")
                    selected_count = gr.Textbox(label="Сколько выбрано", value="0", interactive=False)

            text_field = gr.Textbox(label="Всего записей", value="0", interactive=False)
            process_button = gr.Button("Обработать файл")
            download_output = gr.File(label="Скачать обработанный файл")

            # 1) Сканируем
            scan_evt = scan_button.click(
                scan_disribute,
                inputs=[file_input, sheet_input, len_number],
                outputs=[df_output, text_field],
            )

            # 2) После сканирования — заполняем чекбоксы уникальными "счет"
            scan_evt.then(
                fn=update_accounts_list,
                inputs=[df_output],
                outputs=[accounts_list],
            )

            # 3) Кнопка "Выделить всё / снять"
            def _update_selected_count(selected: list[str]):
                return str(len(selected))

            toggle_button.click(
                fn=toggle_all,
                inputs=[accounts_list, df_output],
                outputs=[accounts_list],
            ).then(
                fn=_update_selected_count,
                inputs=[accounts_list],
                outputs=[selected_count]
            )

            # Чтобы счётчик обновлялся и при ручном выборе
            accounts_list.change(
                fn=_update_selected_count,
                inputs=[accounts_list],
                outputs=[selected_count]
            )

            # 4) Обработка файла — передаём выбранные счета
            process_button.click(
                process_disribute,
                inputs=[
                    file_input,
                    sheet_input,
                    len_number,
                    bank_name,
                    date_value_start,
                    date_value_end,
                    boss_name,
                    accounts_list,  # <-- новое!
                ],
                outputs=[download_output],
            )



if __name__ == "__main__":
    app.launch(inbrowser=True)
