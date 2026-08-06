# cliente_api.py
"""
Cliente para interação com a API GraphQL.
Responsável por autenticação e consultas de dados.
"""

import os
import requests
from datetime import datetime
from config import API_URL, API_HEADERS, LOGIN_CREDENTIALS


class ClienteAPI:
    
    def __init__(self):
        self.token = None
        self.headers = API_HEADERS.copy()

    def _executar_graphql(self, payload, headers=None):
        response = requests.post(API_URL, headers=headers or self.headers, json=payload)
        response.raise_for_status()

        data = response.json()
        if "errors" in data:
            raise Exception(data["errors"])

        return data
    
    def fazer_login(self):
        login_payload = {
            "query": """mutation login($email: String!, $password: String!) {
                logIn(input: { email: $email, password: $password }) {
                    token
                    preAuthToken
                    email
                    role 
                }
            }""",
            "variables": {
                "email": LOGIN_CREDENTIALS["email"],
                "password": LOGIN_CREDENTIALS["password"]
            }
        }
        
        try:
            data = self._executar_graphql(login_payload)
            login_data = data["data"]["logIn"]

            self.token = login_data.get("token")
            pre_auth_token = login_data.get("preAuthToken")

            if not self.token and pre_auth_token:
                print("Login requer validação 2FA.")
                email_2fa = login_data.get("email") or LOGIN_CREDENTIALS["email"]
                self.token = self._validar_2fa(pre_auth_token, email_2fa)

            if not self.token:
                raise Exception("Login não retornou token nem preAuthToken.")

            print("Login realizado com sucesso!")
            print(f"Token obtido: {self.token[:20]}...{self.token[-10:] if len(self.token) > 30 else self.token}")
            return self.token
            
        except Exception as e:
            print(f"Erro ao fazer login: {e}")
            raise

    def _validar_2fa(self, pre_auth_token, email):
        codigo_2fa = input("Cole o código 2FA recebido por email: ").strip()

        if not codigo_2fa:
            raise Exception("Código 2FA não informado.")

        if not email:
            raise Exception("Email não encontrado para validar 2FA.")

        tipo_2fa = os.getenv("TWO_FACTOR_TYPE", "login").strip() or "login"

        payload_2fa = {
            "operationName": None,
            "variables": {
                "email": email,
                "preAuthToken": pre_auth_token,
                "twoFactorCode": codigo_2fa,
                "type": tipo_2fa
            },
            "query": """mutation VerifyTwoFactor($email: String!, $preAuthToken: String!, $twoFactorCode: String!, $type: String!) {
                verifyTwoFactor(input: {email: $email, preAuthToken: $preAuthToken, twoFactorCode: $twoFactorCode, type: $type}) {
                    token
                    preAuthToken
                    authenticated
                }
            }"""
        }

        try:
            data = self._executar_graphql(payload_2fa)
            resultado = data["data"]["verifyTwoFactor"]
            token = resultado.get("token") if isinstance(resultado, dict) else resultado

            if not token:
                raise Exception("Validação 2FA não retornou token.")

            print("2FA validado com sucesso!")
            return token
        except Exception as e:
            raise Exception(f"Erro ao validar 2FA: {e}") from e
    
    def buscar_dados_timesheet(self, data_inicio, data_fim):
        if not self.token:
            raise Exception("Token não encontrado. Faça login primeiro.")
        
        data_inicio_dt = datetime.strptime(data_inicio, "%d/%m/%Y")
        
        periodo = data_inicio_dt.strftime("%Y-%m")
        
        query_payload = {
            "query": """{
                records(where: { 
                    sheet: { key_regex: "timesheet" } 
                    dynamicFields: { month_regex: "%s" }
                } order: { updatedAt: DESC }) {
                    count
                    data {
                        id
                        dynamicFields
                        dynamicAssociations
                    }
                }
            }""" % periodo,
            "variables": {}
        }

        headers_auth = self.headers.copy()
        headers_auth['Authorization'] = self.token
        
        try:
            print("Enviando requisição com autenticação padrão...")
            response = requests.post(API_URL, headers=headers_auth, json=query_payload)

            if response.status_code == 200:
                data = response.json()

                if 'errors' not in data:
                    total = data['data']['records']['count']
                    print(f"Dados recuperados com sucesso! Total de registros: {total}")
                    return data['data']['records']['data']
                else:
                    print(f"Erro na consulta: {data['errors']}")
            else:
                print(f"Status {response.status_code} na resposta da API.")
                
        except requests.exceptions.HTTPError as e:
            print(f"Erro HTTP: {e}")
            raise
        except Exception as e:
            print(f"Erro geral: {e}")
            raise

        raise Exception("Erro ao buscar dados do timesheet.")
