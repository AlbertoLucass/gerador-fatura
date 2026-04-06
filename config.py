# config.py
"""
Arquivo de configuração para o gerador de faturas.
Configure aqui suas informações pessoais e parâmetros.
"""

import os
from datetime import date
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://digitalize.oxean.com.br/graphql"
API_HEADERS = {
    'Content-Type': 'application/json'
}

LOGIN_CREDENTIALS = {
    "email": os.getenv("EMAIL"),
    "password": os.getenv("PASSWORD")
}

INFO_FATURA = {
    "razao_social": os.getenv("RAZAO_SOCIAL"),
    "cnpj": os.getenv("CNPJ"),
    "endereco": os.getenv("ENDERECO"),
    "pix": os.getenv("PIX"),
    "cliente_nome": os.getenv("CLIENTE_NOME"),
    "cliente_cnpj": os.getenv("CLIENTE_CNPJ"),
    "cliente_endereco": os.getenv("CLIENTE_ENDERECO")
}

NUMERO_FATURA = os.getenv("NUMERO_FATURA")
if not NUMERO_FATURA:
    # Auto-generate invoice number based on existing directories
    def get_next_invoice_number(year=None):
        """Get next invoice number by scanning existing year directories.
        
        If current year has no directories, checks previous years to continue
        the sequential numbering (e.g., 2027 continues from 2026's last number).
        """
        if year is None:
            year = date.today().year
        
        base_path = os.path.join(os.path.dirname(__file__), "faturas")
        
        # Try current year, then go backwards if empty
        while year >= 2025:  # Year you started invoicing
            faturas_dir = os.path.join(base_path, str(year))
            
            if os.path.exists(faturas_dir):
                max_number = 0
                for entry in os.listdir(faturas_dir):
                    # Extract number from directory name (e.g., "10-janeiro" -> 10)
                    if "-" in entry:
                        try:
                            num = int(entry.split("-")[0].strip())
                            max_number = max(max_number, num)
                        except ValueError:
                            continue
                
                if max_number > 0:
                    return max_number + 1
            
            year -= 1  # Check previous year
        
        return 1  # Fallback if no directories found at all
    
    NUMERO_FATURA = str(get_next_invoice_number())
TAXA_HORA = float(os.getenv("TAXA_HORA", "1.0"))
MES_COMPLETO = os.getenv("MES_COMPLETO") or (date.today() - relativedelta(months=1)).strftime("%m/%Y")

PDF_CONFIG = {
    "pagesize": "A4",
    "margins": {
        "right": 72,
        "left": 72,
        "top": 72,
        "bottom": 72
    }
}

TAGS_INTERESSE = os.getenv("TAGS_INTERESSE", "development,meeting").split(",")
