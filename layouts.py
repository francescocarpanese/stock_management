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
            sg.Combo(['','l','dl','cl','ml','g','mg'],
                     key='-comb_dosagem-',
                     default_value=''),
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
            sg.Button('Guarda',key='-but_save_new_drug-'),
            sg.Button('Fecha',key='-but-exit_new_drug-'),

        ],
    ]
    return layout

def get_main_layout():
    layout = [
        [
            sg.Text('Nome'),
            sg.Input('',key='-in_name-', enable_events=True),
            sg.Checkbox('Expirado',  default=True, key='-chx_expired-', enable_events=True),
            sg.Checkbox('Esgotados', default=False, key='-chx_out_stock-', enable_events=True),
            sg.Checkbox('Presente',  default=True, key='-chx_present-', enable_events=True),
        ],
        [
            sg.Table(
            values = [],
            headings= ['Nome','Dosagem','Units','Expiracao','Numero de pecas dentro 1 caixinha','Forma','Lote','Stock presente'],
            key='-list_table-',
            )
        ],
        [
            sg.Button('Nuovo movimento', key='-but_new_mov-'),
            sg.Button('Correccao farmaco', key='-but_correct_drug'),
            sg.Button('Nuovo Farmaco', key='-but_new_drug-'),
            sg.Button('Report', key='-but_report-')
        ]

    ]
    return layout

def get_new_movement_layout():
    layout = [
            [
                sg.Text('Nome:', size=10),
                sg.Text('',key='-txt_drug_name-', size=10),
                sg.Text('Dosagemn:', size=25),
                sg.Text('', key='-txt_dosagem-'), 
                sg.Text('', key='-txt_dosagem_unit-'),
            ],
            [
                sg.Text('Expiracao:', size=10),
                sg.Text(key="-txt_DATE-", visible=True, size=10),
                sg.Text('Numero pexca dentro 1 caixa:', size=25),
                sg.Text(0, key='-txt_pieces_in_box-'),
            ],
            [
                sg.Text('Forma:', size=10),
                sg.Text('', key='-txt_forma-',size=10),
                sg.Text('Lote:', size=25),
                sg.Text('', key='-txt_lote-'),
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
                sg.Input(0, key='-pieces_moved-'),
            ],
            [
                sg.Text('Entrada/Saida/Inventario'),
                sg.Combo(['Entrada','Saida','Inventario'], key='-comb_type_mov-', readonly=True)
            ],
            [
                sg.Text('Assignatura'),
                sg.Input('', key='-in_signature-')
            ],
            [
                sg.Button('Guarda', key='-but_save_mov-'),
                sg.Button('Fecha', key='-but_exit_mov-'),
            ],
            [
                sg.HorizontalSeparator(),
            ],
            [
                sg.Text('Numero dos pecas movido:'),
                sg.Text(key='-tot_pieces_moved-')
            ]
        ]

    return layout

def get_report_layout():
    layout = [
            [
                sg.CalendarButton("Data do inicio",
                    target="-in_data_start-",
                    format="%Y-%m-%d",
                    default_date_m_d_y=(1, 1, 2023)),
                    sg.Input(key="-in_data_start-",
                             visible=True,
                             disabled=True)
            ],
            [
                sg.CalendarButton("Data do fim",
                    target="-in_data_end-",
                    format="%Y-%m-%d",
                    default_date_m_d_y=(1, 1, 2023)),
                    sg.Input(key="-in_data_end-",
                             visible=True,
                             disabled=True)
            ],
            [
                sg.Button('Generate', key='-but_generate_report-'),
            ],
            [
                sg.Text('Link reports:'),
                sg.Text('', key='-txt_link_folder-', size=(20,1), enable_events=True),
            ],
    ]
    return layout
