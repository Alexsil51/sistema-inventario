# agent/collector.py
# Funções de coleta WMI e registro do Windows

import wmi
import psutil
import winreg
import socket
import platform
from datetime import datetime
import logging
import subprocess
import os

logging.basicConfig(level=logging.INFO)

class WindowsDataCollector:
    def __init__(self):
        try:
            self.wmi_conn = wmi.WMI()
        except Exception as e:
            logging.error(f"Erro ao conectar WMI: {e}")
            self.wmi_conn = None
    
    def get_computer_identification(self):
        """Coleta identificação da máquina"""
        try:
            data = {
                'nome_computador': platform.node(),
                'dominio': None,
                'usuario_logado': None
            }
            
            if self.wmi_conn:
                for system in self.wmi_conn.Win32_ComputerSystem():
                    data['nome_computador'] = system.Name or platform.node()
                    data['dominio'] = system.Domain
                    data['usuario_logado'] = system.UserName
                    break
            
            # Fallback para obter usuário logado
            if not data['usuario_logado']:
                try:
                    data['usuario_logado'] = os.getlogin()
                except:
                    data['usuario_logado'] = os.environ.get('USERNAME')
            
            return data
        except Exception as e:
            logging.error(f"Erro ao coletar identificação: {e}")
            return {
                'nome_computador': platform.node(),
                'dominio': None,
                'usuario_logado': os.environ.get('USERNAME')
            }
    
    def get_installed_software(self):
        """Coleta softwares instalados do registro"""
        software_list = []
        
        # Caminhos do registro para softwares instalados
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        
        for hkey, subkey_path in registry_paths:
            try:
                with winreg.OpenKey(hkey, subkey_path) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                software_info = {}
                                
                                # Tentar obter informações do software
                                try:
                                    software_info['nome'] = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                except:
                                    software_info['nome'] = subkey_name
                                
                                try:
                                    software_info['versao'] = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                except:
                                    software_info['versao'] = "N/A"
                                
                                try:
                                    software_info['fabricante'] = winreg.QueryValueEx(subkey, "Publisher")[0]
                                except:
                                    software_info['fabricante'] = "N/A"
                                
                                try:
                                    install_date = winreg.QueryValueEx(subkey, "InstallDate")[0]
                                    # Formato YYYYMMDD para YYYY-MM-DD
                                    if len(install_date) == 8 and install_date.isdigit():
                                        software_info['data_instalacao'] = f"{install_date[:4]}-{install_date[4:6]}-{install_date[6:8]}"
                                    else:
                                        software_info['data_instalacao'] = None
                                except:
                                    software_info['data_instalacao'] = None
                                
                                # Filtrar entradas válidas (com nome não vazio)
                                if software_info['nome'] and len(software_info['nome'].strip()) > 0:
                                    software_list.append(software_info)
                            
                            i += 1
                        except OSError:
                            break
                        except Exception as e:
                            logging.warning(f"Erro ao ler software {i}: {e}")
                            i += 1
                            
            except Exception as e:
                logging.error(f"Erro ao acessar registro {subkey_path}: {e}")
        
        return software_list
    
    def get_operating_system(self):
        """Coleta informações do sistema operacional"""
        try:
            data = {
                'nome': platform.system() + " " + platform.release(),
                'versao': platform.version(),
                'service_pack': None,
                'serial': None
            }
            
            if self.wmi_conn:
                for os_info in self.wmi_conn.Win32_OperatingSystem():
                    data['nome'] = os_info.Caption
                    data['versao'] = os_info.Version
                    data['service_pack'] = os_info.ServicePackMajorVersion
                    data['serial'] = os_info.SerialNumber
                    break
            
            return data
        except Exception as e:
            logging.error(f"Erro ao coletar SO: {e}")
            return {
                'nome': platform.system() + " " + platform.release(),
                'versao': platform.version(),
                'service_pack': None,
                'serial': None
            }
    
    def get_processor_info(self):
        """Coleta informações do processador"""
        try:
            data = {
                'modelo': platform.processor(),
                'velocidade_mhz': 0,
                'quantidade': psutil.cpu_count(logical=False)
            }
            
            if self.wmi_conn:
                for proc in self.wmi_conn.Win32_Processor():
                    data['modelo'] = proc.Name
                    data['velocidade_mhz'] = proc.MaxClockSpeed
                    break
            
            return data
        except Exception as e:
            logging.error(f"Erro ao coletar processador: {e}")
            return {
                'modelo': platform.processor(),
                'velocidade_mhz': 0,
                'quantidade': psutil.cpu_count(logical=False) or 1
            }
    
    def get_memory_info(self):
        """Coleta informações de memória RAM"""
        try:
            # Usar psutil para informações básicas
            memory = psutil.virtual_memory()
            data = {
                'capacidade_total_gb': round(memory.total / (1024**3), 2),
                'slots_utilizados': 0,
                'velocidade_mhz': 0
            }
            
            if self.wmi_conn:
                slots = 0
                total_capacity = 0
                speed = 0
                
                for mem in self.wmi_conn.Win32_PhysicalMemory():
                    if mem.Capacity:
                        slots += 1
                        total_capacity += int(mem.Capacity)
                        if mem.Speed and speed == 0:
                            speed = mem.Speed
                
                if slots > 0:
                    data['slots_utilizados'] = slots
                    data['capacidade_total_gb'] = round(total_capacity / (1024**3), 2)
                    data['velocidade_mhz'] = speed
            
            return data
        except Exception as e:
            logging.error(f"Erro ao coletar memória: {e}")
            memory = psutil.virtual_memory()
            return {
                'capacidade_total_gb': round(memory.total / (1024**3), 2),
                'slots_utilizados': 1,
                'velocidade_mhz': 0
            }
    
    def get_network_info(self):
        """Coleta informações de rede"""
        try:
            data = {
                'ip_address': self._get_local_ip(),
                'placas': []
            }
            
            if self.wmi_conn:
                for adapter in self.wmi_conn.Win32_NetworkAdapterConfiguration():
                    if adapter.IPEnabled and adapter.IPAddress:
                        placa_info = {
                            'descricao': adapter.Description,
                            'mac_address': adapter.MACAddress,
                            'ip_address': adapter.IPAddress[0] if adapter.IPAddress else None,
                            'mascara': adapter.IPSubnet[0] if adapter.IPSubnet else None,
                            'gateway': adapter.DefaultIPGateway[0] if adapter.DefaultIPGateway else None
                        }
                        data['placas'].append(placa_info)
            
            return data
        except Exception as e:
            logging.error(f"Erro ao coletar rede: {e}")
            return {
                'ip_address': self._get_local_ip(),
                'placas': []
            }
    
    def _get_local_ip(self):
        """Obtém IP local da máquina"""
        try:
            # Conectar a um servidor externo para obter o IP local usado
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def get_disk_info(self):
        """Coleta informações de discos"""
        disk_list = []
        
        try:
            # Usar psutil para informações de disco
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info = {
                        'unidade': partition.device,
                        'tipo': partition.fstype,
                        'tamanho_gb': round(usage.total / (1024**3), 2),
                        'espaco_livre_gb': round(usage.free / (1024**3), 2),
                        'sistema_arquivos': partition.fstype
                    }
                    disk_list.append(disk_info)
                except Exception as e:
                    logging.warning(f"Erro ao obter info do disco {partition.device}: {e}")
            
            # Complementar com informações WMI se disponível
            if self.wmi_conn:
                try:
                    for disk in self.wmi_conn.Win32_LogicalDisk():
                        # Atualizar informações existentes ou adicionar novas
                        found = False
                        for existing_disk in disk_list:
                            if existing_disk['unidade'] == disk.DeviceID:
                                existing_disk['tipo'] = self._get_disk_type(disk.DriveType)
                                found = True
                                break
                        
                        if not found and disk.Size:
                            disk_info = {
                                'unidade': disk.DeviceID,
                                'tipo': self._get_disk_type(disk.DriveType),
                                'tamanho_gb': round(int(disk.Size) / (1024**3), 2) if disk.Size else 0,
                                'espaco_livre_gb': round(int(disk.FreeSpace) / (1024**3), 2) if disk.FreeSpace else 0,
                                'sistema_arquivos': disk.FileSystem or 'N/A'
                            }
                            disk_list.append(disk_info)
                except Exception as e:
                    logging.warning(f"Erro ao obter discos via WMI: {e}")
        
        except Exception as e:
            logging.error(f"Erro ao coletar discos: {e}")
        
        return disk_list
    
    def _get_disk_type(self, drive_type):
        """Converte código do tipo de drive para texto"""
        types = {
            0: "Desconhecido",
            1: "Sem raiz",
            2: "Removível",
            3: "Disco Fixo",
            4: "Rede",
            5: "CD-ROM",
            6: "RAM Disk"
        }
        return types.get(drive_type, "Desconhecido")
    
    def get_last_logon(self):
        """Coleta informações do último logon"""
        try:
            data = {
                'usuario': os.environ.get('USERNAME'),
                'data_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Tentar obter informações mais precisas via WMI
            if self.wmi_conn:
                try:
                    for logon in self.wmi_conn.Win32_NetworkLoginProfile():
                        if logon.Name and logon.LastLogon:
                            data['usuario'] = logon.Name
                            # Converter tempo WMI para formato legível
                            wmi_time = logon.LastLogon
                            if wmi_time:
                                # Formato: YYYYMMDDHHMMSS.ffffff+offset
                                time_str = wmi_time.split('.')[0]
                                dt = datetime.strptime(time_str, '%Y%m%d%H%M%S')
                                data['data_hora'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                            break
                except:
                    pass
            
            return data
        except Exception as e:
            logging.error(f"Erro ao coletar último logon: {e}")
            return {
                'usuario': os.environ.get('USERNAME', 'N/A'),
                'data_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def get_bios_info(self):
        """Coleta informações da BIOS"""
        try:
            data = {
                'versao': 'N/A',
                'fabricante': 'N/A',
                'data_release': None
            }
            
            if self.wmi_conn:
                for bios in self.wmi_conn.Win32_BIOS():
                    data['versao'] = bios.SMBIOSBIOSVersion or bios.Version
                    data['fabricante'] = bios.Manufacturer
                    
                    # Converter data de release
                    if bios.ReleaseDate:
                        try:
                            # Formato WMI: YYYYMMDDHHMMSS.ffffff+offset
                            date_str = bios.ReleaseDate.split('.')[0][:8]
                            dt = datetime.strptime(date_str, '%Y%m%d')
                            data['data_release'] = dt.strftime('%Y-%m-%d')
                        except:
                            pass
                    break
            
            return data
        except Exception as e:
            logging.error(f"Erro ao coletar BIOS: {e}")
            return {
                'versao': 'N/A',
                'fabricante': 'N/A',
                'data_release': None
            }
    
    def get_controllers(self):
        """Coleta informações de controladores"""
        controllers = []
        
        try:
            if self.wmi_conn:
                # Controladores IDE
                for controller in self.wmi_conn.Win32_IDEController():
                    controllers.append({
                        'tipo': 'IDE',
                        'nome': controller.Name,
                        'descricao': controller.Description
                    })
                
                # Controladores USB
                for controller in self.wmi_conn.Win32_USBController():
                    controllers.append({
                        'tipo': 'USB',
                        'nome': controller.Name,
                        'descricao': controller.Description
                    })
                
                # Controladores de Floppy (se existirem)
                for controller in self.wmi_conn.Win32_FloppyController():
                    controllers.append({
                        'tipo': 'Floppy',
                        'nome': controller.Name,
                        'descricao': controller.Description
                    })
        
        except Exception as e:
            logging.error(f"Erro ao coletar controladores: {e}")
        
        return controllers
    
    def get_input_devices(self):
        """Coleta periféricos de entrada"""
        devices = []
        
        try:
            if self.wmi_conn:
                # Teclados
                for keyboard in self.wmi_conn.Win32_Keyboard():
                    devices.append({
                        'tipo': 'Teclado',
                        'nome': keyboard.Name,
                        'descricao': keyboard.Description
                    })
                
                # Mouses
                for mouse in self.wmi_conn.Win32_PointingDevice():
                    devices.append({
                        'tipo': 'Mouse',
                        'nome': mouse.Name,
                        'descricao': mouse.Description
                    })
        
        except Exception as e:
            logging.error(f"Erro ao coletar dispositivos de entrada: {e}")
        
        return devices
    
    def get_monitors(self):
        """Coleta informações de monitores"""
        monitors = []
        
        try:
            if self.wmi_conn:
                for monitor in self.wmi_conn.Win32_DesktopMonitor():
                    monitors.append({
                        'fabricante': monitor.MonitorManufacturer or 'N/A',
                        'tipo': monitor.MonitorType or 'N/A',
                        'descricao': monitor.Description or monitor.Name
                    })
        
        except Exception as e:
            logging.error(f"Erro ao coletar monitores: {e}")
        
        return monitors
    
    def get_printers(self):
        """Coleta informações de impressoras"""
        printers = []
        
        try:
            if self.wmi_conn:
                for printer in self.wmi_conn.Win32_Printer():
                    printers.append({
                        'nome': printer.Name,
                        'porta': printer.PortName
                    })
        
        except Exception as e:
            logging.error(f"Erro ao coletar impressoras: {e}")
        
        return printers
    
    def collect_all_data(self):
        """Coleta todos os dados da máquina"""
        logging.info("Iniciando coleta completa de dados...")
        
        data = {
            'identificacao': self.get_computer_identification(),
            'softwares': self.get_installed_software(),
            'sistema_operacional': self.get_operating_system(),
            'processador': self.get_processor_info(),
            'memoria': self.get_memory_info(),
            'rede': self.get_network_info(),
            'discos': self.get_disk_info(),
            'ultimo_logon': self.get_last_logon(),
            'bios': self.get_bios_info(),
            'controladores': self.get_controllers(),
            'perifericos_entrada': self.get_input_devices(),
            'monitores': self.get_monitors(),
            'impressoras': self.get_printers(),
            'timestamp_coleta': datetime.now().isoformat()
        }
        
        logging.info("Coleta de dados concluída")
        return data