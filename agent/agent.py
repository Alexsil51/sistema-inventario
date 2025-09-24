import json
import requests
import time
import sys
import os
from datetime import datetime
import socket
import logging

# Importar módulos locais
from collector import WindowsDataCollector
from utils import (
    setup_logging, save_json_backup, validate_data, 
    print_summary, get_config_from_file, check_administrator_rights,
    get_system_info, format_json_pretty, check_network_availability
)

# ============================================================
# CONFIGURAÇÕES CORPORATIVAS
# ============================================================
SILENT_MODE = "--silent" in sys.argv
CORPORATE_TIMEOUT = 120  # 2 minutos máximo por coleta

# ============================================================
# FUNÇÃO DE ENVIO DE DADOS PARA O SERVIDOR
# ============================================================
def send_to_api(data, config):
    """Envia dados para a API via POST - Modo corporativo"""
    if not check_network_availability(config['server_url']):
        if not SILENT_MODE:
            print("Servidor indisponível - dados salvos localmente")
        return False
    
    url = f"{config['server_url']}{config['api_endpoint']}"
    headers = {'Content-Type': 'application/json'}
    
    if not SILENT_MODE:
        print(f"Enviando dados para: {url}")
    
    for attempt in range(config['retry_attempts']):
        try:
            if not SILENT_MODE:
                print(f"Tentativa {attempt + 1}/{config['retry_attempts']}")
            
            response = requests.post(
                url, 
                json=data, 
                headers=headers, 
                timeout=config['timeout']
            )
            
            if response.status_code == 200:
                if not SILENT_MODE:
                    print("✓ Dados enviados com sucesso!")
                return True
            else:
                if not SILENT_MODE:
                    print(f"✗ Erro HTTP {response.status_code}")
                
        except requests.exceptions.RequestException:
            if not SILENT_MODE:
                print(f"✗ Erro de conexão na tentativa {attempt + 1}")
        except Exception as e:
            if not SILENT_MODE:
                print(f"✗ Erro inesperado: {e}")
        
        if attempt < config['retry_attempts'] - 1:
            wait_time = (attempt + 1) * 5
            time.sleep(wait_time)
    
    if not SILENT_MODE:
        print("✗ Falha ao enviar dados após todas as tentativas")
    return False

# ============================================================
# FUNÇÃO PRINCIPAL DO AGENTE (Modo Corporativo)
# ============================================================
def main():
    if not SILENT_MODE:
        print("=" * 60)
        print("SISTEMA DE INVENTÁRIO - AGENTE DE COLETA")
        print("=" * 60)
        print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Configurar logging
    log_file = 'inventory_silent.log' if SILENT_MODE else 'inventory_agent.log'
    setup_logging(log_file)
    
    if not SILENT_MODE:
        if not check_administrator_rights():
            print("⚠️  AVISO: Executando sem privilégios de administrador")
        else:
            print("✓ Privilégios de administrador confirmados")

    # Carregar configurações
    config = get_config_from_file()
    
    if not SILENT_MODE:
        print("\n1. Testando conectividade com servidor...")
    
    # Verificar se servidor está acessível
    if not check_network_availability(config['server_url']):
        if not SILENT_MODE:
            print("⚠️  Servidor indisponível - coleta será salva localmente")
        config['backup_enabled'] = True

    if not SILENT_MODE:
        print("\n2. Inicializando coletor de dados...")
    
    collector = WindowsDataCollector()
    start_time = time.time()

    try:
        # Coletar dados com timeout
        data = collector.collect_all_data()
        
        collection_time = time.time() - start_time
        if not SILENT_MODE:
            print(f"✓ Coleta concluída em {collection_time:.2f} segundos")

        # Validar dados
        errors = validate_data(data)
        if errors and not SILENT_MODE:
            print("⚠️  Alertas de validação:")
            for error in errors:
                print(f"   - {error}")

        if not SILENT_MODE:
            print_summary(data)

        # Preparar payload para API
        payload = {
            "identificacao": data.get("identificacao", {}),
            "sistema_operacional": data.get("sistema_operacional", {}),
            "processador": data.get("processador", {}),
            "memoria": data.get("memoria", {}),
            "rede": data.get("rede", {}),
            "discos": data.get("discos", []),
            "softwares": data.get("softwares", []),
            "timestamp_coleta": datetime.now().isoformat()
        }

        # Enviar para servidor
        if not SILENT_MODE:
            print("\n3. Enviando dados para servidor central...")
        
        success = send_to_api(payload, config)
        
        # Backup local se necessário
        if config.get('backup_enabled', True) and not success:
            backup_file = save_json_backup(data)
            if backup_file and not SILENT_MODE:
                print(f"✓ Backup salvo: {backup_file}")

        if success and not SILENT_MODE:
            print("✓ Inventário enviado com sucesso!")

    except Exception as e:
        logging.error(f"Erro durante execução: {e}")
        if not SILENT_MODE:
            print(f"✗ Erro: {e}")
        return 1

    if not SILENT_MODE:
        print("\n" + "=" * 60)
        print("INVENTÁRIO CONCLUÍDO")
        print("=" * 60)
    
    return 0

# ============================================================
# NOVAS FUNÇÕES PARA MODO CORPORATIVO
# ============================================================
def check_network_availability(server_url):
    """Verifica se servidor está acessível"""
    try:
        health_url = f"{server_url}/health"
        response = requests.get(health_url, timeout=10)
        return response.status_code == 200
    except:
        return False

# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================
if __name__ == "__main__":
    # Modo silencioso para GPO
    if SILENT_MODE:
        # Redirecionar prints para logging apenas
        import sys
        class LoggerWriter:
            def __init__(self, level):
                self.level = level
            def write(self, message):
                if message.strip():
                    self.level(message.strip())
            def flush(self):
                pass
        
        sys.stdout = LoggerWriter(logging.info)
        sys.stderr = LoggerWriter(logging.error)
    
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        if not SILENT_MODE:
            print("\nPrograma interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Erro fatal: {e}")
        sys.exit(1)