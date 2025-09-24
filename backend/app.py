import os
import json
import logging
import traceback
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from database import DatabaseManager

# ============================================================
# CONFIGURAÇÕES BÁSICAS
# ============================================================

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "inventario"
}

logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


# ============================================================
# FUNÇÃO AUXILIAR PARA COMPLIANCE (NOVA - COLOQUE AQUI)
# ============================================================
def check_monthly_compliance(machine_data):
    """Verifica se a máquina rodou o agente no mês atual"""
    try:
        ultima_atualizacao = machine_data.get('ultima_atualizacao')
        if not ultima_atualizacao:
            return False
            
        if isinstance(ultima_atualizacao, str):
            ultima = datetime.fromisoformat(ultima_atualizacao.replace('Z', '+00:00'))
        else:
            ultima = ultima_atualizacao
            
        # Verificar se rodou neste mês
        agora = datetime.now()
        mesmo_mes = ultima.month == agora.month
        mesmo_ano = ultima.year == agora.year
        
        return mesmo_mes and mesmo_ano
        
    except Exception:
        return False
    
# ============================================================
# ROTAS PRINCIPAIS
# ============================================================

@app.route('/')
def index():
    """Redireciona para o dashboard"""
    return redirect('/dashboard')

@app.route('/dashboard')
def serve_dashboard():
    """Serve a página HTML do dashboard"""
    try:
        return send_from_directory('../static', 'dashboard.html')
    except:
        return """
        <h1>Sistema de Inventário</h1>
        <p>API está funcionando! Dashboard em construção.</p>
        <p><a href="/api/machines_dashboard">Ver máquinas</a></p>
        <p><a href="/health">Health Check</a></p>
        """

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Endpoint de teste"""
    return jsonify({
        "message": "API está funcionando!",
        "timestamp": datetime.now().isoformat(),
        "endpoints_available": [
            "/health",
            "/api/inventory",
            "/api/machines_dashboard", 
            "/api/machine/<id>",
            "/api/test"
        ]
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Verifica se o servidor está rodando"""
    return jsonify({"status": "ok", "message": "Server is running"}), 200

@app.route('/api/inventory', methods=['POST'])
def save_inventory():
    """Recebe dados do agente e salva no banco de dados"""
    db = DatabaseManager(**DB_CONFIG)
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Dados inválidos"}), 400

        # Processar dados do seu agente
        processed_data = process_agent_data(data)
        
        # Inserir ou atualizar máquina
        machine_id = db.save_inventory(processed_data)
        
        return jsonify({
            "success": True,
            "message": "Inventário salvo com sucesso",
            "machine_id": machine_id
        }), 200

    except Exception as e:
        logging.error("Erro ao salvar inventário:\n" + traceback.format_exc())
        return jsonify({"success": False, "message": f"Erro ao salvar inventário: {str(e)}"}), 500
    finally:
        db.disconnect()

@app.route("/api/machines_dashboard", methods=["GET"])
def machines_dashboard():
    """Rota para listar todas as máquinas com status de compliance"""
    db = DatabaseManager(**DB_CONFIG)
    try:
        machines = db.get_all_machines(table="maquinas")
        response = []
        agora = datetime.now()

        for m in machines:
            ultima_str = m.get("ultima_atualizacao")
            online = False
            if ultima_str:
                try:
                    if isinstance(ultima_str, str):
                        ultima = datetime.fromisoformat(ultima_str.replace('Z', '+00:00'))
                    else:
                        ultima = ultima_str
                    online = (agora - ultima) <= timedelta(minutes=5)
                except Exception as e:
                    logging.warning(f"Erro ao processar data: {e}")
                    online = False

            # NOVO: Verificar compliance mensal
            em_compliance = check_monthly_compliance(m)
            
            # Processar software
            software_data = m.get("software", "[]")
            try:
                if isinstance(software_data, str):
                    software_list = json.loads(software_data)
                else:
                    software_list = software_data
            except:
                software_list = []

            response.append({
                "id": m.get("id"),
                "nome_computador": m.get("nome_computador"),
                "dominio": m.get("dominio"),
                "usuario": m.get("usuario"),
                "data_coleta": str(m.get("data_coleta")),
                "ip": m.get("ip"),
                "so": m.get("so"),
                "ram": m.get("ram"),
                "armazenamento": m.get("armazenamento"),
                "software": software_list,
                "ultima_atualizacao": str(m.get("ultima_atualizacao")),
                "online": online,
                "em_compliance": em_compliance,  # NOVO CAMPO
                "mes_referencia": agora.strftime("%Y-%m")  # NOVO CAMPO
            })
        return jsonify(response), 200

    except Exception as e:
        logging.error("Erro ao listar máquinas:\n" + traceback.format_exc())
        return jsonify({"success": False, "message": f"Erro ao listar máquinas: {str(e)}"}), 500
    finally:
        db.disconnect()

@app.route("/api/machine/<int:machine_id>", methods=["GET"])
def get_machine(machine_id):
    """Rota para buscar uma máquina específica"""
    db = DatabaseManager(**DB_CONFIG)
    try:
        machine = db.get_machine_by_id(machine_id)
        if machine:
            # Processar software
            software_data = machine.get("software", "[]")
            try:
                if isinstance(software_data, str):
                    software_list = json.loads(software_data)
                else:
                    software_list = software_data
            except:
                software_list = []
            
            machine["software"] = software_list
            return jsonify(machine), 200
        else:
            return jsonify({"success": False, "message": "Máquina não encontrada"}), 404
    except Exception as e:
        logging.error(f"Erro ao buscar máquina {machine_id}:\n" + traceback.format_exc())
        return jsonify({"success": False, "message": f"Erro ao buscar máquina: {str(e)}"}), 500
    finally:
        db.disconnect()

# ============================================================
# ROTA PARA DELETAR MÁQUINA (NOVA - COLOQUE AQUI)
# ============================================================
@app.route('/api/machine/<int:machine_id>', methods=['DELETE'])
def delete_machine(machine_id):
    """Deleta uma máquina do banco de dados (APENAS MANUAL)"""
    db = DatabaseManager(**DB_CONFIG)
    try:
        # Verificar se a máquina existe
        machine = db.get_machine_by_id(machine_id)
        if not machine:
            return jsonify({"success": False, "message": "Máquina não encontrada"}), 404
        
         # Calcular dias inativo (MANUALMENTE - sem depender da função)
        last_update = machine.get('ultima_atualizacao')
        days_inactive = 0
        if last_update:
            if isinstance(last_update, str):
                last_date = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
            else:
                last_date = last_update
            days_inactive = (datetime.now() - last_date).days
        
        machine_name = machine.get('nome_computador', 'Desconhecida')

        # Confirmar com dados da máquina
        #machine_name = machine.get('nome_computador', 'Desconhecida')
        #last_update = machine.get('ultima_atualizacao', 'N/A')
        #days_inactive = db.get_days_inactive(machine_id)
        
        # Deletar a máquina
        db.delete_machine(machine_id)
        
        logging.info(f"Máquina deletada manualmente: {machine_name} (ID: {machine_id})")
        return jsonify({
            "success": True, 
            "message": f"Máquina '{machine_name}' deletada com sucesso",
            "deleted_machine": {
                "id": machine_id,
                "nome": machine_name,
                "ultima_atualizacao": last_update,
                "dias_inativo": days_inactive
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao deletar máquina {machine_id}:\n" + traceback.format_exc())
        return jsonify({"success": False, "message": f"Erro ao deletar máquina: {str(e)}"}), 500
    finally:
        db.disconnect()

# ============================================================
# NOVA ROTA PARA DEPLOY (ADICIONE AQUI)
# ============================================================
@app.route('/deploy.ps1')
def serve_deploy_script():
    """Serve o script de deploy via HTTP"""
    return send_from_directory('../deploy', 'deploy.ps1')


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def process_agent_data(data):
    """Processa os dados do agente para o formato do banco"""
    identificacao = data.get('identificacao', {})
    sistema_operacional = data.get('sistema_operacional', {})
    processador = data.get('processador', {})
    memoria = data.get('memoria', {})
    rede = data.get('rede', {})
    discos = data.get('discos', [])
    softwares = data.get('softwares', [])
    
    # Calcular armazenamento total
    total_storage = sum(disco.get('tamanho_gb', 0) for disco in discos)
    
    # Obter IP principal
    ip_principal = rede.get('ip_address', 'N/A')
    if rede.get('placas'):
        for placa in rede['placas']:
            if placa.get('ip_address'):
                ip_principal = placa['ip_address']
                break
    
    return {
        "machine_name": identificacao.get('nome_computador', 'Unknown'),
        "user": identificacao.get('usuario_logado', 'N/A'),
        "dominio": identificacao.get('dominio', 'N/A'),
        "ip": ip_principal,
        "os": f"{sistema_operacional.get('nome', 'N/A')} {sistema_operacional.get('versao', '')}",
        "ram": f"{memoria.get('capacidade_total_gb', 0)} GB",
        "storage": f"{total_storage} GB",
        "software": softwares,
        "ultima_atualizacao": data.get('timestamp_coleta', datetime.now().isoformat())
    }

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("Iniciando servidor de inventário...")
    print(f"Dashboard disponível em: http://10.65.0.16:5000")
    print(f"API disponível em: http://10.65.0.16:5000/api/")
    app.run(host="0.0.0.0", port=5000, debug=True)