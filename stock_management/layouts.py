"""
Layouts for the GUI
"""

import PySimpleGUI as sg

font = ("Arial", 20)


def get_new_drug_layout():
    layout = [
        [sg.Text("Nome:", font=font), sg.Input("", key="-in_drug_name-", font=font)],
        [
            sg.Text("Dosagemn", font=font),
            sg.Input("", key="-in_dosagem-", font=font),
            sg.Combo(
                ["", "l", "dl", "cl", "ml", "g", "mg"],
                key="-comb_dosagem-",
                default_value="",
                font=font,
            ),
        ],
        [
            sg.CalendarButton(
                "Data de expiracao",
                target="-in_DATE-",
                format="%Y-%m-%d",
                default_date_m_d_y=(1, 1, 2023),
                font=font,
            ),
            sg.Input(key="-in_DATE-", visible=True, disabled=True, font=font),
        ],
        [
            sg.Text("Numero pexca dentro 1 caixa", font=font),
            sg.Input(0, key="-in_pieces_in_box-", font=font),
        ],
        [
            sg.Text("Forma", font=font),
            sg.Combo(
                ["Comprimidos", "Ampolla", "Xerope", "Pumadas", "Frasca"],
                readonly=True,
                key="-combo_forma-",
                font=font,
            ),
        ],
        [sg.Text("Lote", font=font), sg.Input("", key="-in_lote-", font=font)],
        [
            sg.Button("Guarda", key="-but_save_new_drug-", font=font),
            sg.Button("Fecha", key="-but-exit_new_drug-", font=font),
        ],
    ]
    return layout


def get_main_layout():
    layout = [
        [
            sg.Text("Nome", font=font),
            sg.Input("", key="-in_name-", enable_events=True, font=font),
            sg.Checkbox(
                "Expirado",
                default=True,
                key="-chx_expired-",
                enable_events=True,
                font=font,
            ),
            sg.Checkbox(
                "Esgotados",
                default=False,
                key="-chx_out_stock-",
                enable_events=True,
                font=font,
            ),
            sg.Checkbox(
                "Presente",
                default=True,
                key="-chx_present-",
                enable_events=True,
                font=font,
            ),
        ],
        [
            sg.Table(
                values=[],
                headings=[
                    "Nome",
                    "Dosagem",
                    "Units",
                    "Expiracao",
                    "Pecas por caixa",
                    "Forma",
                    "Lote",
                    "Stock presente",
                ],
                key="-list_table-",
                font=font,
                col_widths=[20, 8, 5, 8, 12, 8, 8, 10],
                justification="left",
                auto_size_columns=False,
                num_rows=20,
                alternating_row_color=sg.theme_button_color()[1],
                selected_row_colors="red on yellow",
            )
        ],
        [
            sg.Button("Nuovo Movimento", key="-but_new_mov-", font=font),
            sg.Button("Correccao Medicamento", key="-but_correct_drug", font=font),
            sg.Button("Nuovo Medicamento", key="-but_new_drug-", font=font),
            sg.Button("Report", key="-but_report-", font=font),
            sg.Button("Test", key="-but_test-", font=font),
        ],
    ]
    return layout


def get_new_movement_layout():
    layout = [
        [
            sg.Text("Nome:", size=10, font=font),
            sg.Text("", key="-txt_drug_name-", size=10, font=font),
            sg.Text("Dosagemn:", size=25, font=font),
            sg.Text("", key="-txt_dosagem-", font=font),
            sg.Text("", key="-txt_dosagem_unit-", font=font),
        ],
        [
            sg.Text("Expiracao:", size=10, font=font),
            sg.Text(key="-txt_DATE-", visible=True, size=10, font=font),
            sg.Text("Numero pexca dentro 1 caixa:", size=25, font=font),
            sg.Text(0, key="-txt_pieces_in_box-", font=font),
        ],
        [
            sg.Text("Forma:", size=10, font=font),
            sg.Text("", key="-txt_forma-", size=10, font=font),
            sg.Text("Lote:", size=25, font=font),
            sg.Text("", key="-txt_lote-", font=font),
        ],
        [
            sg.HorizontalSeparator(),
        ],
        [
            sg.CalendarButton(
                "Data do movido",
                target="-in_data_movido-",
                format="%Y-%m-%d",
                default_date_m_d_y=(1, 1, 2023),
                font=font,
            ),
            sg.Input(key="-in_data_movido-", visible=True, disabled=True, font=font),
        ],
        [
            sg.Text("Origem/Destino", font=font),
            sg.Input("", key="-in_origin_destiny-", font=font),
        ],
        [
            sg.Text("Numero de caixinha completas", font=font),
            sg.Input(0, key="-boxes_moved-", font=font),
        ],
        [
            sg.Text("Numero de pecas fora de caixina", font=font),
            sg.Input(0, key="-pieces_moved-", font=font),
        ],
        [
            sg.Text("Entrada/Saida/Inventario", font=font),
            sg.Combo(
                ["Entrada", "Saida", "Inventario"],
                key="-comb_type_mov-",
                readonly=True,
                font=font,
            ),
        ],
        [
            sg.Text("Assignatura", font=font),
            sg.Input("", key="-in_signature-", font=font),
        ],
        [
            sg.Button("Guarda", key="-but_save_mov-", font=font),
            sg.Button("Fecha", key="-but_exit_mov-", font=font),
        ],
        [
            sg.HorizontalSeparator(),
        ],
        [
            sg.Text("Numero dos pecas movido:", font=font),
            sg.Text(key="-tot_pieces_moved-", font=font),
        ],
    ]

    return layout


def get_report_layout():
    layout = [
        [
            sg.CalendarButton(
                "Data do inicio",
                target="-in_data_start-",
                format="%Y-%m-%d",
                default_date_m_d_y=(1, 1, 2023),
                font=font,
            ),
            sg.Input(key="-in_data_start-", visible=True, disabled=True, font=font),
        ],
        [
            sg.CalendarButton(
                "Data do fim",
                target="-in_data_end-",
                format="%Y-%m-%d",
                default_date_m_d_y=(1, 1, 2023),
                font=font,
            ),
            sg.Input(key="-in_data_end-", visible=True, disabled=True, font=font),
        ],
        [
            sg.Button("Generate", key="-but_generate_report-", font=font),
        ],
        [
            sg.Text("Link reports:", font=font),
            sg.Text(
                "", key="-txt_link_folder-", size=(20, 1), enable_events=True, font=font
            ),
        ],
    ]
    return layout

def get_test_layout():
    layout = [
        [

            sg.Text('Test Window')

        ],
        [

            sg.Text('Enter something:'),
            sg.InputText()

        ],
        [

            sg.Button('Ok', key='-but_confirm_test-', font=font),
            sg.Button('Cancel', key='-but_exit_test-', font=font)

        ]
    ]
    return layout
