# agent/utils.py
# Funções auxiliares para o sistema de inventário

import json
import logging
import os
import sys
from datetime import datetime
import requests
import platform
import getpass

# ============================================================
# CONFIGURAÇÃO DE LOGGING
# ============================================================
def setup_logging(log_file='inventory_agent.log'):
    """Configura sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

# ============================================================
# BACKUP E ARQUIVOS
# ============================================================
def save_json_backup(data, filename=None):
    """Salva backup dos dados em JSON local"""
    try:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            computer_name = data.get('identificacao', {}).get('nome_computador', 'unknown')
            filename = f"inventory_backup_{computer_name}_{timestamp}.json"
        
        # Criar diretório de backup se não existir
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        filepath = os.path.join(backup_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Backup salvo em: {filepath}")
        return filepath
    
    except Exception as e:
        logging.error(f"Erro ao salvar backup: {e}")
        return None

# ============================================================
# VALIDAÇÃO DE DADOS
# ============================================================
def validate_data(data):
    """Valida estrutura dos dados coletados"""
    required_fields = [
        'identificacao',
        'sistema_operacional',
        'processador',
        'memoria',
        'rede',
        'discos'
    ]
    
    errors = []
    
    # Verificar campos obrigatórios
    for field in required_fields:
        if field not in data:
            errors.append(f"Campo obrigatório ausente: {field}")
    
    # Validar identificação
    if 'identificacao' in data:
        if not data['identificacao'].get('nome_computador'):
            errors.append("nome_computador é obrigatório")
    
    # Validar discos
    if 'discos' in data:
        if not isinstance(data['discos'], list):
            errors.append("discos deve ser uma lista")
        elif len(data['discos']) == 0:
            errors.append("Nenhum disco encontrado")
    
    # Validar softwares
    if 'softwares' in data:
        if not isinstance(data['softwares'], list):
            errors.append("softwares deve ser uma lista")
    
    return errors

# ============================================================
# UTILITÁRIOS DE SISTEMA
# ============================================================
def format_file_size(size_bytes):
    """Formata tamanho de arquivo em formato legível"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def clean_string(text):
    """Limpa string removendo caracteres especiais"""
    if not text:
        return ""
    
    # Remover caracteres de controle e espaços extras
    cleaned = ''.join(char for char in text if ord(char) >= 32)
    return cleaned.strip()

def check_administrator_rights():
    """Verifica se o script está rodando com privilégios de administrador"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_system_info():
    """Retorna informações básicas do sistema para debugging"""
    try:
        info = {
            'python_version': sys.version,
            'platform': platform.platform(),
            'architecture': platform.architecture(),
            'processor': platform.processor(),
            'is_admin': check_administrator_rights(),
            'current_user': getpass.getuser()
        }
        
        return info
    except Exception as e:
        logging.error(f"Erro ao obter informações do sistema: {e}")
        return {}

# ============================================================
# CONFIGURAÇÃO
# ============================================================
def get_config_from_file(config_file='config.json'):
    """Carrega configurações de arquivo JSON"""
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        else:
            # Criar arquivo de configuração padrão
            default_config = {
                'server_url': 'http://localhost:5000',
                'api_endpoint': '/api/inventory',
                'timeout': 30,
                'retry_attempts': 3,
                'backup_enabled': True,
                'log_level': 'INFO'
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
            
            logging.info(f"Arquivo de configuração criado: {config_file}")
            return default_config
    
    except Exception as e:
        logging.error(f"Erro ao carregar configuração: {e}")
        return {
            'server_url': 'http://localhost:5000',
            'api_endpoint': '/api/inventory',
            'timeout': 30,
            'retry_attempts': 3,
            'backup_enabled': True,
            'log_level': 'INFO'
        }

# ============================================================
# REDE E CONECTIVIDADE
# ============================================================
def check_network_availability(server_url):
    """Verifica se servidor está acessível"""
    try:
        health_url = f"{server_url}/health"
        response = requests.get(health_url, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
    except Exception as e:
        logging.warning(f"Erro ao verificar conectividade: {e}")
        return False

# ============================================================
# RELATÓRIOS E VISUALIZAÇÃO
# ============================================================
def print_summary(data):
    """Imprime resumo dos dados coletados"""
    print("\n" + "="*60)
    print("RESUMO DOS DADOS COLETADOS")
    print("="*60)
    
    # Identificação
    ident = data.get('identificacao', {})
    print(f"Máquina: {ident.get('nome_computador', 'N/A')}")
    print(f"Domínio: {ident.get('dominio', 'N/A')}")
    print(f"Usuário: {ident.get('usuario_logado', 'N/A')}")
    
    # Sistema Operacional
    so = data.get('sistema_operacional', {})
    print(f"SO: {so.get('nome', 'N/A')} {so.get('versao', '')}")
    
    # Processador
    proc = data.get('processador', {})
    print(f"CPU: {proc.get('modelo', 'N/A')}")
    print(f"Velocidade: {proc.get('velocidade_mhz', 0)} MHz")
    print(f"Núcleos: {proc.get('quantidade', 1)}")
    
    # Memória
    mem = data.get('memoria', {})
    print(f"RAM: {mem.get('capacidade_total_gb', 0)} GB")
    print(f"Slots: {mem.get('slots_utilizados', 1)}")
    
    # Discos
    discos = data.get('discos', [])
    print(f"Discos: {len(discos)}")
    for disco in discos[:3]:  # Mostra apenas os 3 primeiros
        print(f"  - {disco.get('unidade', '')}: {disco.get('tamanho_gb', 0)} GB ({disco.get('sistema_arquivos', 'N/A')})")
    if len(discos) > 3:
        print(f"  - ... e mais {len(discos) - 3} discos")
    
    # Rede
    rede = data.get('rede', {})
    placas = rede.get('placas', [])
    print(f"Placas de rede: {len(placas)}")
    print(f"IP principal: {rede.get('ip_address', 'N/A')}")
    
    # Softwares
    softwares = data.get('softwares', [])
    print(f"Softwares instalados: {len(softwares)}")
    
    # Outros componentes
    print(f"Controladores: {len(data.get('controladores', []))}")
    print(f"Monitores: {len(data.get('monitores', []))}")
    print(f"Impressoras: {len(data.get('impressoras', []))}")
    
    print("="*60)

def create_csv_report(data, filename=None):
    """Cria relatório CSV básico dos dados"""
    try:
        import csv
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            computer_name = data.get('identificacao', {}).get('nome_computador', 'unknown')
            filename = f"inventory_report_{computer_name}_{timestamp}.csv"
        
        # Criar diretório de relatórios se não existir
        report_dir = 'reports'
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        
        filepath = os.path.join(report_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Cabeçalhos
            writer.writerow(['Categoria', 'Item', 'Valor', 'Detalhes'])
            
            # Identificação
            ident = data.get('identificacao', {})
            writer.writerow(['Identificação', 'Nome do Computador', ident.get('nome_computador', ''), ''])
            writer.writerow(['Identificação', 'Domínio', ident.get('dominio', ''), ''])
            writer.writerow(['Identificação', 'Usuário Logado', ident.get('usuario_logado', ''), ''])
            
            # Sistema Operacional
            so = data.get('sistema_operacional', {})
            writer.writerow(['Sistema Operacional', 'Nome', so.get('nome', ''), ''])
            writer.writerow(['Sistema Operacional', 'Versão', so.get('versao', ''), ''])
            writer.writerow(['Sistema Operacional', 'Serial', so.get('serial', ''), ''])
            
            # Hardware básico
            proc = data.get('processador', {})
            writer.writerow(['Hardware', 'Processador', proc.get('modelo', ''), f"{proc.get('velocidade_mhz', 0)} MHz"])
            
            mem = data.get('memoria', {})
            writer.writerow(['Hardware', 'Memória RAM', f"{mem.get('capacidade_total_gb', 0)} GB", f"{mem.get('slots_utilizados', 0)} slots"])
            
            # Discos
            for i, disco in enumerate(data.get('discos', [])):
                writer.writerow(['Armazenamento', f'Disco {i+1}', disco.get('unidade', ''), 
                               f"{disco.get('tamanho_gb', 0)} GB - {disco.get('sistema_arquivos', '')}"])
            
            # Top 10 softwares (por tamanho do nome, como proxy de importância)
            softwares = sorted(data.get('softwares', []), key=lambda x: len(x.get('nome', '')), reverse=True)[:10]
            for software in softwares:
                writer.writerow(['Software', software.get('nome', ''), software.get('versao', ''), 
                               software.get('fabricante', '')])
        
        logging.info(f"Relatório CSV criado: {filepath}")
        return filepath
    
    except Exception as e:
        logging.error(f"Erro ao criar relatório CSV: {e}")
        return None

# ============================================================
# FORMATAÇÃO
# ============================================================
def format_json_pretty(data):
    """Formata JSON de forma legível"""
    try:
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        logging.error(f"Erro ao formatar JSON: {e}")
        return str(data)

# ============================================================
# FUNÇÕES DE TEMPO
# ============================================================
def is_office_hours():
    """Verifica se está em horário comercial"""
    now = datetime.now()
    return now.weekday() < 5 and 9 <= now.hour < 18

def should_run_quietly():
    """Decide se deve executar em modo silencioso"""
    return not is_office_hours()

# ============================================================
# VALIDAÇÃO DE REDE CORPORATIVA
# ============================================================
def is_domain_environment():
    """Verifica se a máquina está em ambiente de domínio"""
    try:
        import socket
        hostname = socket.gethostname()
        fqdn = socket.getfqdn()
        
        # Se o FQDN contém pontos além do nome da máquina, está em domínio
        return fqdn != hostname and '.' in fqdn
    except:
        return False

def get_domain_name():
    """Obtém o nome do domínio"""
    try:
        import socket
        fqdn = socket.getfqdn()
        if '.' in fqdn:
            return fqdn.split('.', 1)[1]
        return None
    except:
        return None

# ============================================================
# LOGGING AVANÇADO
# ============================================================
def log_performance(operation_name, start_time):
    """Registra tempo de execução de operações"""
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    if duration > 5:  # Log apenas se demorar mais de 5 segundos
        logging.warning(f"Operação '{operation_name}' demorou {duration:.2f} segundos")
    else:
        logging.info(f"Operação '{operation_name}' concluída em {duration:.2f} segundos")
    
    return duration