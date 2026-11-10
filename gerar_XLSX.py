"""Exporta as linhas individuais do timesheet para uma planilha XLSX."""

import os
from datetime import datetime

import pandas as pd
from openpyxl.styles import Font, PatternFill


def exportar_linhas_xlsx(linhas, nome_arquivo_pdf=None, data_inicio=None):
    """Gera uma linha por registro processado, sem agrupá-los por descrição."""
    if nome_arquivo_pdf:
        nome_arquivo = os.path.splitext(nome_arquivo_pdf)[0] + "_linhas.xlsx"
    elif data_inicio:
        periodo = datetime.strptime(data_inicio, '%d/%m/%Y')
        diretorio = os.path.join('faturas', str(periodo.year), 'timesheet')
        os.makedirs(diretorio, exist_ok=True)
        nome_arquivo = os.path.join(
            diretorio, f'Timesheet_{periodo.month:02d}-{periodo.year}.xlsx'
        )
    else:
        raise ValueError('Informe o arquivo PDF ou a data de início do período.')

    colunas = {
        'id': 'ID',
        'start_date': 'Data',
        'start_time': 'Começo',
        'stop_time': 'Parada',
        'description': 'Descrição',
        'duration': 'Duração (horas)',
        'tag': 'Tag',
        'task': 'Tarefa'
    }
    tabela = pd.DataFrame(linhas, columns=list(colunas)).rename(columns=colunas)

    with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
        tabela.to_excel(writer, index=False, sheet_name='Timesheet')
        planilha = writer.sheets['Timesheet']
        planilha.freeze_panes = 'A2'
        planilha.auto_filter.ref = planilha.dimensions

        for celula in planilha[1]:
            celula.font = Font(bold=True, color='FFFFFF')
            celula.fill = PatternFill(fill_type='solid', fgColor='366092')

        larguras = {
            'A': 24, 'B': 14, 'C': 18, 'D': 18,
            'E': 55, 'F': 20, 'G': 20, 'H': 40
        }
        for coluna, largura in larguras.items():
            planilha.column_dimensions[coluna].width = largura

        for celula in planilha['B'][1:]:
            celula.number_format = 'dd/mm/yyyy'
        for celula in planilha['F'][1:]:
            celula.number_format = '0.00'

    return nome_arquivo
