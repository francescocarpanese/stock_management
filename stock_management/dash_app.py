"""
Modern Dash web application for hospital drug stock management
Beautiful, responsive UI with Bootstrap styling
"""

import dash
from dash import html, dcc, Input, Output, State, callback, dash_table, ALL, ctx
import dash_bootstrap_components as dbc
from datetime import date, datetime, timedelta
import sqlite3
import os
import pandas as pd

from stock_management.create_tables import create_all_tables
import stock_management.sql_utils as sql_utils
import stock_management.search_utils as search_utils
import stock_management.drug_utils as drugs_win_utils
import stock_management.movement_utils as movement_win_utils
from stock_management import report_utils

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

# Database setup
DB_PATH = "database.db"
if not os.path.exists(DB_PATH):
    create_all_tables(DB_PATH)


def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)


# Custom CSS styling
CUSTOM_STYLE = {
    'backgroundColor': '#f8f9fa',
    'fontFamily': 'Arial, sans-serif'
}

CARD_STYLE = {
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'borderRadius': '10px',
    'marginBottom': '20px'
}

BUTTON_STYLE = {
    'marginRight': '10px',
    'marginBottom': '10px',
    'fontSize': '16px',
    'fontWeight': 'bold',
    'padding': '12px 24px',
    'borderRadius': '8px'
}


def create_navbar():
    """Create navigation bar"""
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.I(className="fas fa-hospital me-2"),
                    dbc.NavbarBrand("Sistema de Gestão de Stock Hospitalar", 
                                   className="ms-2",
                                   style={'fontSize': '24px', 'fontWeight': 'bold'})
                ], width="auto"),
            ], align="center", className="g-0"),
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4",
        style={'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}
    )


def create_filters_card():
    """Create filters and search card"""
    return dbc.Card([
        dbc.CardHeader(
            html.H5([
                html.I(className="fas fa-filter me-2"),
                "Filtros e Pesquisa"
            ], className="mb-0"),
            style={'backgroundColor': '#e9ecef'}
        ),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Nome do Medicamento:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dbc.Input(
                        id='search-input',
                        type='text',
                        placeholder='Digite o nome...',
                        debounce=True,
                        style={'fontSize': '16px', 'padding': '10px'}
                    )
                ], md=6),
                dbc.Col([
                    dbc.Label("Filtros:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    html.Div([
                        dbc.Checkbox(
                            id='filter-expired',
                            label='Expirado',
                            value=True,
                            className='me-3',
                            style={'fontSize': '16px'}
                        ),
                        dbc.Checkbox(
                            id='filter-out-stock',
                            label='Esgotados',
                            value=False,
                            className='me-3',
                            style={'fontSize': '16px'}
                        ),
                        dbc.Checkbox(
                            id='filter-present',
                            label='Presente',
                            value=True,
                            style={'fontSize': '16px'}
                        ),
                    ], className='d-flex align-items-center mt-2')
                ], md=6)
            ])
        ])
    ], style=CARD_STYLE)


def create_action_buttons():
    """Create action buttons"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Button([
                html.I(className="fas fa-plus-circle me-2"),
                "Novo Medicamento"
            ], id='btn-new-drug', color='success', size='lg', style=BUTTON_STYLE),
            dbc.Button([
                html.I(className="fas fa-exchange-alt me-2"),
                "Novo Movimento"
            ], id='btn-new-movement', color='warning', size='lg', style=BUTTON_STYLE),
            dbc.Button([
                html.I(className="fas fa-edit me-2"),
                "Corrigir Medicamento"
            ], id='btn-correct-drug', color='info', size='lg', style=BUTTON_STYLE),
            dbc.Button([
                html.I(className="fas fa-file-alt me-2"),
                "Gerar Relatório"
            ], id='btn-report', color='primary', size='lg', style=BUTTON_STYLE),
        ])
    ], style=CARD_STYLE)


def create_drugs_table():
    """Create the drugs table"""
    return dbc.Card([
        dbc.CardHeader(
            html.H5([
                html.I(className="fas fa-pills me-2"),
                "Lista de Medicamentos"
            ], className="mb-0"),
            style={'backgroundColor': '#e9ecef'}
        ),
        dbc.CardBody([
            html.Div(id='table-container')
        ])
    ], style=CARD_STYLE)


def format_drugs_for_table(rows):
    """Format drug rows for display in table"""
    if not rows:
        return []
    
    formatted_rows = search_utils.format_table_rows(rows)
    
    data = []
    for idx, row in enumerate(formatted_rows):
        data.append({
            'id': rows[idx][0],  # Hidden ID
            'Nome': row[0],
            'Dosagem': row[1],
            'Units': row[2],
            'Expiração': row[3],
            'Peças/Caixa': row[4],
            'Forma': row[5],
            'Lote': row[6],
            'Stock': row[7]
        })
    
    return data


# Modal for New Drug
def create_new_drug_modal():
    """Create modal for adding/editing drugs"""
    today = date.today()
    
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Novo Medicamento", style={'fontSize': '20px'})),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Nome:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dbc.Input(id='drug-name', type='text', style={'fontSize': '16px'}),
                ], md=12, className='mb-3'),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Dosagem:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dbc.Input(id='drug-dose', type='text', style={'fontSize': '16px'}),
                ], md=6, className='mb-3'),
                dbc.Col([
                    dbc.Label("Unidades:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='drug-units',
                        options=[
                            {'label': '', 'value': ''},
                            {'label': 'l', 'value': 'l'},
                            {'label': 'dl', 'value': 'dl'},
                            {'label': 'cl', 'value': 'cl'},
                            {'label': 'ml', 'value': 'ml'},
                            {'label': 'g', 'value': 'g'},
                            {'label': 'mg', 'value': 'mg'},
                        ],
                        value='',
                        style={'fontSize': '16px'}
                    ),
                ], md=6, className='mb-3'),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Data de Expiração:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dcc.DatePickerSingle(
                        id='drug-expiration',
                        date=today,
                        display_format='YYYY-MM-DD',
                        style={'fontSize': '16px'}
                    ),
                ], md=6, className='mb-3'),
                dbc.Col([
                    dbc.Label("Peças por Caixa:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dbc.Input(id='drug-pieces-per-box', type='number', value=0, style={'fontSize': '16px'}),
                ], md=6, className='mb-3'),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Forma:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='drug-form',
                        options=[
                            {'label': 'Comprimidos', 'value': 'Comprimidos'},
                            {'label': 'Ampolla', 'value': 'Ampolla'},
                            {'label': 'Xerope', 'value': 'Xerope'},
                            {'label': 'Pumadas', 'value': 'Pumadas'},
                            {'label': 'Frasca', 'value': 'Frasca'},
                        ],
                        style={'fontSize': '16px'}
                    ),
                ], md=6, className='mb-3'),
                dbc.Col([
                    dbc.Label("Lote:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dbc.Input(id='drug-lote', type='text', style={'fontSize': '16px'}),
                ], md=6, className='mb-3'),
            ]),
            html.Div(id='drug-modal-alert')
        ]),
        dbc.ModalFooter([
            dbc.Button("Guardar", id='save-drug-btn', color='success', size='lg', 
                      style={'fontSize': '16px', 'fontWeight': 'bold'}),
            dbc.Button("Cancelar", id='close-drug-modal', color='danger', size='lg',
                      style={'fontSize': '16px', 'fontWeight': 'bold'}),
        ])
    ], id='drug-modal', size='lg', is_open=False)


# Modal for New Movement
def create_new_movement_modal():
    """Create modal for adding movements"""
    today = date.today()
    
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Novo Movimento", style={'fontSize': '20px'})),
        dbc.ModalBody([
            # Drug info display
            dbc.Card([
                dbc.CardHeader("Informação do Medicamento", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                dbc.CardBody(id='movement-drug-info')
            ], className='mb-3'),
            
            # Movement inputs
            dbc.Row([
                dbc.Col([
                    dbc.Label("Data do Movimento:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dcc.DatePickerSingle(
                        id='movement-date',
                        date=today,
                        display_format='YYYY-MM-DD',
                        style={'fontSize': '16px'}
                    ),
                ], md=6, className='mb-3'),
                dbc.Col([
                    dbc.Label("Origem/Destino:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dbc.Input(id='movement-origin', type='text', style={'fontSize': '16px'}),
                ], md=6, className='mb-3'),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Caixas Completas:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dbc.Input(id='movement-boxes', type='number', value=0, style={'fontSize': '16px'}),
                ], md=4, className='mb-3'),
                dbc.Col([
                    dbc.Label("Peças Fora de Caixa:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dbc.Input(id='movement-pieces', type='number', value=0, style={'fontSize': '16px'}),
                ], md=4, className='mb-3'),
                dbc.Col([
                    dbc.Label("Total de Peças:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    html.Div(id='movement-total', 
                            style={'fontSize': '20px', 'fontWeight': 'bold', 'color': '#007bff', 'marginTop': '8px'}),
                ], md=4, className='mb-3'),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Tipo de Movimento:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='movement-type',
                        options=[
                            {'label': 'Entrada', 'value': 'Entrada'},
                            {'label': 'Saída', 'value': 'Saida'},
                            {'label': 'Inventário', 'value': 'Inventario'},
                        ],
                        style={'fontSize': '16px'}
                    ),
                ], md=6, className='mb-3'),
                dbc.Col([
                    dbc.Label("Assinatura:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dbc.Input(id='movement-signature', type='text', style={'fontSize': '16px'}),
                ], md=6, className='mb-3'),
            ]),
            html.Div(id='movement-modal-alert')
        ]),
        dbc.ModalFooter([
            dbc.Button("Guardar", id='save-movement-btn', color='success', size='lg',
                      style={'fontSize': '16px', 'fontWeight': 'bold'}),
            dbc.Button("Cancelar", id='close-movement-modal', color='danger', size='lg',
                      style={'fontSize': '16px', 'fontWeight': 'bold'}),
        ])
    ], id='movement-modal', size='lg', is_open=False)


# Modal for Reports
def create_report_modal():
    """Create modal for generating reports"""
    today = date.today()
    # Calculate first day of previous month
    first_day_this_month = today.replace(day=1)
    if first_day_this_month.month == 1:
        start_date = first_day_this_month.replace(year=first_day_this_month.year - 1, month=12)
    else:
        start_date = first_day_this_month.replace(month=first_day_this_month.month - 1)
    
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Gerar Relatório", style={'fontSize': '20px'})),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Data de Início:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dcc.DatePickerSingle(
                        id='report-start-date',
                        date=start_date,
                        display_format='YYYY-MM-DD',
                        style={'fontSize': '16px'}
                    ),
                ], md=6, className='mb-3'),
                dbc.Col([
                    dbc.Label("Data de Fim:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    dcc.DatePickerSingle(
                        id='report-end-date',
                        date=today,
                        display_format='YYYY-MM-DD',
                        style={'fontSize': '16px'}
                    ),
                ], md=6, className='mb-3'),
            ]),
            html.Div(id='report-modal-alert')
        ]),
        dbc.ModalFooter([
            dbc.Button("Gerar", id='generate-report-btn', color='primary', size='lg',
                      style={'fontSize': '16px', 'fontWeight': 'bold'}),
            dbc.Button("Fechar", id='close-report-modal', color='secondary', size='lg',
                      style={'fontSize': '16px', 'fontWeight': 'bold'}),
        ])
    ], id='report-modal', size='lg', is_open=False)


# App layout
app.layout = dbc.Container([
    dcc.Store(id='selected-drug-id'),
    dcc.Store(id='current-drug-for-edit'),
    
    create_navbar(),
    
    create_filters_card(),
    create_action_buttons(),
    create_drugs_table(),
    
    # Modals
    create_new_drug_modal(),
    create_new_movement_modal(),
    create_report_modal(),
    
], fluid=True, style=CUSTOM_STYLE)


# Callbacks
@callback(
    Output('table-container', 'children'),
    [Input('search-input', 'value'),
     Input('filter-expired', 'value'),
     Input('filter-out-stock', 'value'),
     Input('filter-present', 'value'),
     Input('save-drug-btn', 'n_clicks'),
     Input('save-movement-btn', 'n_clicks')]
)
def update_table(search_text, expired, out_stock, present, drug_save, mov_save):
    """Update the drugs table based on filters"""
    conn = get_db_connection()
    
    search_text = search_text or ''
    rows = search_utils.search_drug(conn, search_text, expired, out_stock, present)
    
    conn.close()
    
    data = format_drugs_for_table(rows)
    
    if not data:
        return html.Div("Nenhum medicamento encontrado", 
                       style={'textAlign': 'center', 'padding': '20px', 'fontSize': '18px', 'color': '#666'})
    
    return dash_table.DataTable(
        id='drugs-table',
        columns=[
            {'name': 'Nome', 'id': 'Nome'},
            {'name': 'Dosagem', 'id': 'Dosagem'},
            {'name': 'Units', 'id': 'Units'},
            {'name': 'Expiração', 'id': 'Expiração'},
            {'name': 'Peças/Caixa', 'id': 'Peças/Caixa'},
            {'name': 'Forma', 'id': 'Forma'},
            {'name': 'Lote', 'id': 'Lote'},
            {'name': 'Stock', 'id': 'Stock'},
        ],
        data=data,
        row_selectable='single',
        selected_rows=[],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontSize': '15px',
            'fontFamily': 'Arial'
        },
        style_header={
            'backgroundColor': '#007bff',
            'color': 'white',
            'fontWeight': 'bold',
            'fontSize': '16px',
            'padding': '14px'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa'
            },
            {
                'if': {'state': 'selected'},
                'backgroundColor': '#cfe2ff',
                'border': '2px solid #007bff'
            }
        ],
        page_size=20,
    )


@callback(
    Output('selected-drug-id', 'data'),
    Input('drugs-table', 'selected_rows'),
    State('drugs-table', 'data')
)
def store_selected_drug(selected_rows, table_data):
    """Store the selected drug ID"""
    if selected_rows and table_data:
        return table_data[selected_rows[0]]['id']
    return None


# New Drug Modal callbacks
@callback(
    Output('drug-modal', 'is_open'),
    [Input('btn-new-drug', 'n_clicks'),
     Input('btn-correct-drug', 'n_clicks'),
     Input('close-drug-modal', 'n_clicks'),
     Input('save-drug-btn', 'n_clicks')],
    [State('drug-modal', 'is_open'),
     State('selected-drug-id', 'data')],
    prevent_initial_call=True
)
def toggle_drug_modal(n_new, n_correct, n_close, n_save, is_open, selected_id):
    """Toggle drug modal"""
    if ctx.triggered_id == 'btn-correct-drug' and not selected_id:
        return is_open
    
    if n_new or n_correct or n_close:
        return not is_open
    
    if n_save:
        # Will be handled by save callback
        return False
    
    return is_open


@callback(
    [Output('drug-name', 'value'),
     Output('drug-dose', 'value'),
     Output('drug-units', 'value'),
     Output('drug-expiration', 'date'),
     Output('drug-pieces-per-box', 'value'),
     Output('drug-form', 'value'),
     Output('drug-lote', 'value'),
     Output('current-drug-for-edit', 'data')],
    Input('btn-correct-drug', 'n_clicks'),
    State('selected-drug-id', 'data'),
    prevent_initial_call=True
)
def load_drug_for_edit(n_clicks, drug_id):
    """Load drug data when editing"""
    if not drug_id:
        return '', '', '', date.today(), 0, '', '', None
    
    conn = get_db_connection()
    row = sql_utils.get_row(conn, 'drugs', drug_id)
    drug = sql_utils.parse_drug(conn, 'drugs', row)
    conn.close()
    
    return (
        drug.get('name', ''),
        drug.get('dose', ''),
        drug.get('units', ''),
        drug.get('expiration', date.today()),
        drug.get('pieces_per_box', 0),
        drug.get('type', ''),
        drug.get('lote', ''),
        drug.get('id')
    )


@callback(
    Output('drug-modal-alert', 'children'),
    Input('save-drug-btn', 'n_clicks'),
    [State('drug-name', 'value'),
     State('drug-dose', 'value'),
     State('drug-units', 'value'),
     State('drug-expiration', 'date'),
     State('drug-pieces-per-box', 'value'),
     State('drug-form', 'value'),
     State('drug-lote', 'value'),
     State('current-drug-for-edit', 'data')],
    prevent_initial_call=True
)
def save_drug(n_clicks, name, dose, units, expiration, pieces, form, lote, drug_id):
    """Save drug to database"""
    if not n_clicks:
        return None
    
    values = {
        'in_drug_name': name or '',
        'in_dosagem': dose or '',
        'comb_dosagem': units or '',
        'in_DATE': expiration,
        'in_pieces_in_box': str(pieces or 0),
        'combo_forma': form or '',
        'in_lote': lote or '',
    }
    
    conn = get_db_connection()
    success = drugs_win_utils.save_drug(values, conn, id=drug_id)
    conn.close()
    
    if success:
        return dbc.Alert("Medicamento guardado com sucesso!", color="success", duration=3000)
    else:
        return dbc.Alert("Erro ao guardar medicamento. Verifique os campos.", color="danger", duration=3000)


# Movement Modal callbacks
@callback(
    Output('movement-modal', 'is_open'),
    [Input('btn-new-movement', 'n_clicks'),
     Input('close-movement-modal', 'n_clicks'),
     Input('save-movement-btn', 'n_clicks')],
    [State('movement-modal', 'is_open'),
     State('selected-drug-id', 'data')],
    prevent_initial_call=True
)
def toggle_movement_modal(n_new, n_close, n_save, is_open, selected_id):
    """Toggle movement modal"""
    if ctx.triggered_id == 'btn-new-movement' and not selected_id:
        return is_open
    
    if n_new or n_close:
        return not is_open
    
    if n_save:
        return False
    
    return is_open


@callback(
    Output('movement-drug-info', 'children'),
    Input('btn-new-movement', 'n_clicks'),
    State('selected-drug-id', 'data'),
    prevent_initial_call=True
)
def load_drug_info_for_movement(n_clicks, drug_id):
    """Load drug info when creating movement"""
    if not drug_id:
        return "Selecione um medicamento primeiro"
    
    conn = get_db_connection()
    row = sql_utils.get_row(conn, 'drugs', drug_id)
    drug = sql_utils.parse_drug(conn, 'drugs', row)
    conn.close()
    
    return html.Div([
        html.P([html.Strong("Nome: "), drug.get('name', '')]),
        html.P([html.Strong("Dosagem: "), f"{drug.get('dose', '')} {drug.get('units', '')}"]),
        html.P([html.Strong("Expiração: "), str(drug.get('expiration', ''))]),
        html.P([html.Strong("Peças por Caixa: "), str(drug.get('pieces_per_box', ''))]),
        html.P([html.Strong("Forma: "), drug.get('type', '')]),
        html.P([html.Strong("Lote: "), drug.get('lote', '')]),
    ], style={'fontSize': '15px'})


@callback(
    Output('movement-total', 'children'),
    [Input('movement-boxes', 'value'),
     Input('movement-pieces', 'value')],
    State('selected-drug-id', 'data')
)
def update_movement_total(boxes, pieces, drug_id):
    """Calculate total pieces for movement"""
    if not drug_id:
        return "0"
    
    conn = get_db_connection()
    row = sql_utils.get_row(conn, 'drugs', drug_id)
    drug = sql_utils.parse_drug(conn, 'drugs', row)
    conn.close()
    
    boxes = boxes or 0
    pieces = pieces or 0
    pieces_per_box = drug.get('pieces_per_box', 0)
    
    total = boxes * pieces_per_box + pieces
    return str(total)


@callback(
    Output('movement-modal-alert', 'children'),
    Input('save-movement-btn', 'n_clicks'),
    [State('movement-date', 'date'),
     State('movement-origin', 'value'),
     State('movement-boxes', 'value'),
     State('movement-pieces', 'value'),
     State('movement-type', 'value'),
     State('movement-signature', 'value'),
     State('selected-drug-id', 'data')],
    prevent_initial_call=True
)
def save_movement(n_clicks, mov_date, origin, boxes, pieces, mov_type, signature, drug_id):
    """Save movement to database"""
    if not n_clicks or not drug_id:
        return None
    
    values = {
        'in_data_movido': mov_date,
        'in_origin_destiny': origin or '',
        'boxes_moved': str(boxes or 0),
        'pieces_moved': str(pieces or 0),
        'comb_type_mov': mov_type or '',
        'in_signature': signature or '',
    }
    
    conn = get_db_connection()
    row = sql_utils.get_row(conn, 'drugs', drug_id)
    drug = sql_utils.parse_drug(conn, 'drugs', row)
    
    success = movement_win_utils.save_move(values, conn, drug, None)
    conn.close()
    
    if success:
        return dbc.Alert("Movimento guardado com sucesso!", color="success", duration=3000)
    else:
        return dbc.Alert("Erro ao guardar movimento. Verifique os campos.", color="danger", duration=3000)


# Report Modal callbacks
@callback(
    Output('report-modal', 'is_open'),
    [Input('btn-report', 'n_clicks'),
     Input('close-report-modal', 'n_clicks')],
    State('report-modal', 'is_open'),
    prevent_initial_call=True
)
def toggle_report_modal(n_report, n_close, is_open):
    """Toggle report modal"""
    if n_report or n_close:
        return not is_open
    return is_open


@callback(
    Output('report-modal-alert', 'children'),
    Input('generate-report-btn', 'n_clicks'),
    [State('report-start-date', 'date'),
     State('report-end-date', 'date')],
    prevent_initial_call=True
)
def generate_report(n_clicks, start_date, end_date):
    """Generate reports"""
    if not n_clicks:
        return None
    
    values = {
        'in_data_start': start_date,
        'in_data_end': end_date,
    }
    
    conn = get_db_connection()
    
    # Generate reports (this will create files in reports/ directory)
    try:
        # Parse dates if provided
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        
        success, error_msg, folder_path = report_utils.generate_reports(
            conn, 
            start_date=start_date_obj, 
            end_date=end_date_obj
        )
        
        conn.close()
        
        if not success:
            return dbc.Alert(error_msg, color="danger", dismissable=True)
        
        return dbc.Alert([
            "Relatórios gerados com sucesso! ",
            html.Br(),
            html.Small(f"Pasta: {folder_path}")
        ], color="success")
    except Exception as e:
        conn.close()
        return dbc.Alert(f"Erro ao gerar relatórios: {str(e)}", color="danger")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("  Sistema de Gestão de Stock Hospitalar - Web Application")
    print("="*60)
    print("\n  🌐 Acesse: http://localhost:8050")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8050)


if __name__ == '__main__':
    main()
