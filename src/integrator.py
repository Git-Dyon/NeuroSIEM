#!/usr/bin/env python3
import sys
import json
import requests # Usaremos requests para falar com a API local do Ollama

# --- CONFIGURAÇÃO ---
# 'host.docker.internal' é o endereço mágico que permite o Docker falar com o seu PC (Host)
OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
MODELO = "llama3.2" # Ou "llama3", "mistral", dependendo do que você baixou

def get_ai_analysis(log_content):
    # Prompt otimizado para modelos locais (Llama 3 é muito bom em seguir instruções)
    prompt = f"""
    Você é um Analista de SOC Sênior (Security Operations Center).
    Sua tarefa é analisar o seguinte log de segurança.
    
    LOG:
    {log_content}

    Responda EXCLUSIVAMENTE em formato JSON com a seguinte estrutura (sem texto antes ou depois):
    {{
        "risco": "Alto, Médio ou Baixo",
        "tipo_ataque": "Nome técnico do ataque",
        "explicacao_curta": "Resumo de 1 frase do que aconteceu",
        "mitigacao": "Ação recomendada imediata"
    }}
    """
    
    payload = {
        "model": MODELO,
        "prompt": prompt,
        "format": "json", # Força resposta em JSON nativo (recurso novo do Ollama)
        "stream": False
    }

    try:
        # Envia para o servidor local
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        # O Ollama devolve a resposta dentro de 'response'
        resultado_texto = response.json()['response']
        return json.loads(resultado_texto)
        
    except requests.exceptions.RequestException as e:
        return {"erro": f"Falha na conexão com Ollama: {str(e)}"}
    except json.JSONDecodeError:
        return {"erro": "IA respondeu, mas não foi um JSON válido."}
    except Exception as e:
        return {"erro": f"Erro inesperado: {str(e)}"}

def main():
    try:
        # O Wazuh envia o caminho do arquivo de alerta como argumento
        alert_file_path = sys.argv[1]
        
        with open(alert_file_path) as f:
            alert_json = json.load(f)

        # Extrai o log para análise
        log_para_analise = json.dumps(alert_json)

        # Chama a IA Local
        analise = get_ai_analysis(log_para_analise)

        # Grava no log de integrações
        with open('/var/ossec/logs/integrations.log', 'a') as log_file:
            log_file.write(f"\n--- [LOCAL AI] NOVO ALERTA PROCESSADO ---\n")
            log_file.write(json.dumps(analise, indent=4, ensure_ascii=False))
            log_file.write(f"\n-----------------------------------------\n")

    except Exception as e:
        with open('/var/ossec/logs/integrations.log', 'a') as log_file:
            log_file.write(f"Erro no script local: {str(e)}\n")

if __name__ == "__main__":
    main()
    