import PySimpleGUI as sg


def get_new_drug_layout():

    layout = [
        [
            sg.Text('Nome:'),
            sg.Input('',key='-in_drug_name-')
        ],
        [
            sg.Text('Dosagemn'),
            sg.Input('', key='-in_dosagem-'), 
            sg.Combo([''], key='-comb_dosagem-'),
        ],
        [
            sg.Text('Expiracao'),
            sg.CalendarButton("Choose Date", target="-in_DATE-", format="%Y-%m-%d", default_date_m_d_y=(1, 1, 2023)), 
            sg.Input(key="-in_DATE-", visible=True, disabled=True)
        ],
        [
            sg.Text('Numero pexca dentro 1 caixa'),
            sg.Input(0, key='-in_pieces_in_box-'),
        ],
        [
            sg.Text('Forma'),
            sg.Combo(['Comprimidos','Ampolla','Xerope','Pumadas','Frasca'], readonly=True, key='-combo_forma-')
        ],
        [
            sg.Text('Lote'),
            sg.Input('', key='-in_lote-')
        ],
        [
            sg.Button('Guarda',key='-but_save_new_drug'),
            sg.Button('Fecha',key='-but-exit_new_drug'),

        ],
    ]
    return layout

def get_main_layout():
    layout = [
        [
            sg.Text('Nome'),
            sg.Input('',key='-in_nome-'),
        ],
        [
            sg.Table(
            values = [],
            headings= ['Nome','Dosagem','Expiracao','Numero de pecas dentro 1 caixinha','Forma','Lote','Stock presente'],
            key='-list_table-',
            )
        ],
        [
            sg.Button('Nuovo movimento', key='-but_new_mov'),
            sg.Button('Correccao farmaco', key='-but_correct_drug'),
            sg.Button('Nuovo Farmaco', key='-but_new_drug-'),
        ]

    ]
    return layout

def get_new_movement_layout():
    layout = [
            [
                sg.Text(f'Nome:')
            ],
            [
                sg.Text(f'Expiracao:')
            ],
            [
                sg.Text(f'Lote:')
            ],
            [
                sg.HorizontalSeparator(),
            ],
            [
                sg.CalendarButton("Data do movido",
                    target="-in_data_movido-",
                    format="%Y-%m-%d",
                    default_date_m_d_y=(1, 1, 2023)),
                    sg.Input(key="-in_data_movido-",
                             visible=True,
                             disabled=True)
            ],
            [
                sg.Text('Origem/Destino'),
                sg.Input('',key='-in_origin_destiny-')
            ],
            [
                sg.Text('Numero de caixinha completas'),
                sg.Input(0,key= '-boxes_moved-'),
            ],
            [
                sg.Text('Numero de pecas fora de caixina'),
                sg.Input(0, key='-pieces_moved'),
            ],
            [
                sg.Text('Entrada/Saida/Inventario'),
                sg.Combo(['Entrada','Saida','Inventario'], key='-comb_type_mov', readonly=True)
            ],
            [
                sg.Text('Assignatura'),
                sg.Input('', key='-in_signature-')
            ],
            [
                sg.Button('Guarda'),
                sg.Button('Fecha'),
            ]
        ]

    return layout
