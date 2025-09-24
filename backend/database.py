import mysql.connector
from mysql.connector import Error
import logging
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor(dictionary=True)
            logging.info("Conexão com o banco de dados estabelecida")
        except Error as e:
            logging.error(f"Erro ao conectar no banco: {str(e)}")
            raise

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logging.info("Conexão com o banco encerrada")

    def save_inventory(self, data):
        try:
            logging.info(f"Salvando dados no banco: {data.get('machine_name')}")

            # Extrair dados recebidos
            nome = data.get("machine_name", "Unknown")
            usuario = data.get("user", "N/A")
            dominio = data.get("dominio", "")
            ip = data.get("ip", "N/A")
            so = data.get("os", "N/A")
            ram = data.get("ram", "N/A")
            armazenamento = data.get("storage", "N/A")
            software = json.dumps(data.get("software", []))
            ultima_atualizacao = data.get("ultima_atualizacao")
            data_coleta = datetime.now()

            # Converter string para datetime se necessário
            if isinstance(ultima_atualizacao, str):
                try:
                    ultima_atualizacao = datetime.fromisoformat(ultima_atualizacao.replace('Z', '+00:00'))
                except:
                    ultima_atualizacao = datetime.now()

            # Verifica se já existe a máquina
            self.cursor.execute(
                "SELECT id FROM maquinas WHERE nome_computador = %s",
                (nome,)
            )
            result = self.cursor.fetchone()

            if result:  # Atualiza
                machine_id = result["id"]
                self.cursor.execute("""
                    UPDATE maquinas SET 
                        dominio=%s,
                        usuario=%s,
                        ip=%s,
                        so=%s,
                        ram=%s,
                        armazenamento=%s,
                        software=%s,
                        ultima_atualizacao=%s,
                        data_coleta=%s
                    WHERE id=%s
                """, (dominio, usuario, ip, so, ram, armazenamento, software, ultima_atualizacao, data_coleta, machine_id))
            else:  # Insere novo
                self.cursor.execute("""
                    INSERT INTO maquinas 
                        (nome_computador, dominio, usuario, ip, so, ram, armazenamento, software, ultima_atualizacao, data_coleta)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (nome, dominio, usuario, ip, so, ram, armazenamento, software, ultima_atualizacao, data_coleta))
                machine_id = self.cursor.lastrowid

            self.conn.commit()
            logging.info(f"Inventário salvo com sucesso: machine_id={machine_id}")
            return machine_id

        except Exception as e:
            logging.error(f"Erro ao salvar inventário: {str(e)}")
            if self.conn:
                self.conn.rollback()
            raise

    def get_all_machines(self, table="maquinas"):
        """Retorna todas as máquinas cadastradas"""
        try:
            query = f"SELECT * FROM {table} ORDER BY ultima_atualizacao DESC"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"Erro ao buscar máquinas: {str(e)}")
            return []

    def get_machine_by_id(self, machine_id):
        """Busca máquina por ID"""
        try:
            self.cursor.execute(
                "SELECT * FROM maquinas WHERE id = %s",
                (machine_id,)
            )
            return self.cursor.fetchone()
        except Exception as e:
            logging.error(f"Erro ao buscar máquina {machine_id}: {str(e)}")
            return None

    def get_days_inactive(self, machine_id):
        """Calcula quantos dias a máquina está inativa"""
        try:
            self.cursor.execute("""
                SELECT DATEDIFF(NOW(), ultima_atualizacao) as dias_inativo 
                FROM maquinas WHERE id = %s
            """, (machine_id,))
            result = self.cursor.fetchone()
            return result['dias_inativo'] if result else 0
        except Exception as e:
            logging.error(f"Erro ao calcular dias inativo: {e}")
            return 0

    def delete_machine(self, machine_id):
        """Deleta uma máquina pelo ID"""
        try:
            # Primeiro buscar o nome da máquina para log
            machine = self.get_machine_by_id(machine_id)
            machine_name = machine.get('nome_computador', 'Unknown') if machine else 'Unknown'
            
            # Deletar a máquina
            self.cursor.execute(
                "DELETE FROM maquinas WHERE id = %s",
                (machine_id,)
            )
            self.conn.commit()
            
            logging.info(f"Máquina deletada: {machine_name} (ID: {machine_id})")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao deletar máquina {machine_id}: {e}")
            self.conn.rollback()
            raise

    def get_machine_by_name(self, machine_name):
        """Busca máquina pelo nome"""
        try:
            self.cursor.execute(
                "SELECT * FROM maquinas WHERE nome_computador = %s",
                (machine_name,)
            )
            return self.cursor.fetchone()
        except Exception as e:
            logging.error(f"Erro ao buscar máquina por nome {machine_name}: {e}")
            return None