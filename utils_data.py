# utils_data.py
"""
Utilitários para manipulação de datas e períodos.
"""

from datetime import datetime
from calendar import monthrange
import os


class UtilsData:
    
    @staticmethod
    def calcular_periodo(mes_completo):
        try:
            mes, ano = mes_completo.split('/')
            mes = int(mes)
            ano = int(ano)

            data_inicio = f"01/{mes:02d}/{ano}"

            ultimo_dia = monthrange(ano, mes)[1]
            data_fim = f"{ultimo_dia:02d}/{mes:02d}/{ano}"

            return data_inicio, data_fim

        except ValueError:
            raise ValueError("Formato de mês inválido. Use MM/YYYY (ex: 05/2025)")
    
    @staticmethod
    def formatar_nome_arquivo(numero_fatura, data_inicio, data_fim):
        NOMES_MESES = {
            1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
            5: "maio", 6: "junho", 7: "julho", 8: "agosto",
            9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
        }

        # Extrair mês e ano de data_inicio (formato DD/MM/YYYY)
        partes = data_inicio.split('/')
        mes = int(partes[1])
        ano = partes[2]

        nome_mes = NOMES_MESES[mes]
        pasta_mes = f"{numero_fatura}-{nome_mes}"

        destino = os.path.join("faturas", ano, pasta_mes)
        os.makedirs(destino, exist_ok=True)

        data_inicio_fmt = data_inicio.replace('/', '-')
        data_fim_fmt = data_fim.replace('/', '-')
        filename = f"Fatura_{numero_fatura}_{data_inicio_fmt}_a_{data_fim_fmt}.pdf"

        return os.path.join(destino, filename)
    
    @staticmethod
    def validar_formato_data(data_str, formato="%d/%m/%Y"):
        try:
            datetime.strptime(data_str, formato)
            return True
        except ValueError:
            return False
