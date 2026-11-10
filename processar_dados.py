# processar_dados.py
"""
Processador de dados para conversão dos dados da API 
para o formato necessário para geração da fatura.
"""

import pandas as pd
from datetime import datetime
import re
import unicodedata
from config import TAGS_INTERESSE


class ProcessarDados:
    
    def __init__(self):
        self.tags_interesse = TAGS_INTERESSE
    
    def processar_dados_api(self, dados_api, data_inicio, data_fim):
        _, resultados = self.processar_dados_com_linhas(dados_api, data_inicio, data_fim)
        return resultados

    def processar_dados_com_linhas(self, dados_api, data_inicio, data_fim):
        linhas = self.extrair_linhas_api(dados_api, data_inicio, data_fim)
        resultados = self._agrupar_por_tag(linhas, data_inicio, data_fim)
        return linhas, resultados

    def extrair_linhas_api(self, dados_api, data_inicio, data_fim):
        data_inicio_dt = datetime.strptime(data_inicio, "%d/%m/%Y")
        data_fim_dt = datetime.strptime(data_fim, "%d/%m/%Y")
        
        registros_processados = []
        
        for registro in dados_api:
            dynamic_fields = registro.get('dynamicFields', {})
            
            start_date_str = dynamic_fields.get('start_date', '')
            description = dynamic_fields.get('description', '')
            duration_str = dynamic_fields.get('duration', '0')
            tag = dynamic_fields.get('tag', 'development')
            task = dynamic_fields.get('task', '')
            start_time = self._obter_horario(dynamic_fields, 'comeco')
            stop_time = self._obter_horario(dynamic_fields, 'parada')

            if not start_time and isinstance(start_date_str, str) and 'T' in start_date_str:
                start_time = start_date_str.split('T', 1)[1]
            
            if not description and task:
                description = task
            elif not description and not task:
                description = 'Sem descrição'
            
            if start_date_str:
                try:
                    start_date_dt = self._processar_data(start_date_str)
                    
                    if not (data_inicio_dt <= start_date_dt <= data_fim_dt):
                        continue
                        
                except Exception as e:
                    print(f"Erro ao processar data {start_date_str}: {e}")
                    continue
            else:
                continue
            
            try:
                duration = float(str(duration_str).replace(',', '.'))
            except (ValueError, TypeError):
                duration = 0.0
            
            registros_processados.append({
                'id': registro.get('id', ''),
                'start_date': start_date_dt,
                'start_time': start_time,
                'stop_time': stop_time,
                'description': description,
                'duration': duration,
                'tag': tag,
                'task': task
            })
        
        return registros_processados

    def _obter_horario(self, dynamic_fields, tipo):
        aliases = {
            'comeco': (
                'start_time', 'start', 'started_at', 'start_datetime',
                'time_start', 'begin', 'begin_time', 'time_begin',
                'starttime', 'startedat', 'clock_in', 'check_in', 'time_in',
                'hora_inicio', 'hora_entrada', 'inicio', 'entrada', 'comeco'
            ),
            'parada': (
                'stop_time', 'stop', 'stopped_at', 'stop_datetime',
                'end_time', 'end', 'ended_at', 'end_datetime', 'end_date',
                'stop_date', 'finish_date', 'ending_at', 'time_stop',
                'time_end', 'finish', 'finish_time', 'stoptime', 'clock_out',
                'check_out', 'time_out',
                'stoppedat', 'enddate', 'endedat', 'hora_parada',
                'hora_fim', 'hora_saida', 'parada', 'saida', 'fim'
            )
        }
        campos = {
            self._normalizar_nome_campo(chave): valor
            for chave, valor in dynamic_fields.items()
        }
        for alias in aliases[tipo]:
            valor = campos.get(self._normalizar_nome_campo(alias))
            if valor not in (None, ''):
                return valor
        return ''

    @staticmethod
    def _normalizar_nome_campo(chave):
        chave = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', str(chave))
        chave = unicodedata.normalize('NFKD', chave)
        chave = ''.join(char for char in chave if not unicodedata.combining(char))
        return re.sub(r'[^a-zA-Z0-9]+', '_', chave).strip('_').lower()
    
    def _processar_data(self, start_date_str):
        if 'T' in start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
        else:
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:
                try:
                    start_date = datetime.strptime(start_date_str[:10], fmt).date()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"Formato de data não reconhecido: {start_date_str}")
        
        return datetime.combine(start_date, datetime.min.time())
    
    def _agrupar_por_tag(self, registros_processados, data_inicio, data_fim):
        df = pd.DataFrame(registros_processados)
        
        if df.empty:
            print(f"Nenhum registro encontrado entre {data_inicio} e {data_fim}")
            return {}
        
        resultados = {}
        
        for tag in self.tags_interesse:
            tag_df = df[df['tag'] == tag]
            
            if tag_df.empty:
                print(f"Nenhum registro encontrado para a tag '{tag}'")
                continue
            
            agrupado = tag_df.groupby('description')['duration'].sum()\
                            .reset_index()\
                            .sort_values('duration', ascending=False)
            
            resultados[tag] = agrupado
        
        return resultados
