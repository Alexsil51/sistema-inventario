CREATE DATABASE inventario;
USE inventario;

-- Tabela principal de máquinas
CREATE TABLE IF NOT EXISTS maquinas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_computador VARCHAR(255) NOT NULL,
    dominio VARCHAR(255),
    usuario_logado VARCHAR(255),
    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    INDEX idx_nome (nome_computador),
    INDEX idx_data (data_coleta)
);

-- Tabela de sistema operacional
CREATE TABLE IF NOT EXISTS sistema_operacional (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    nome VARCHAR(255),
    versao VARCHAR(100),
    service_pack VARCHAR(100),
    serial VARCHAR(255),
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

-- Tabela de processadores
CREATE TABLE IF NOT EXISTS processadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    modelo VARCHAR(255),
    velocidade_mhz INT,
    quantidade INT,
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

-- Tabela de memória RAM
CREATE TABLE IF NOT EXISTS memoria_ram (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    capacidade_total_gb DECIMAL(10,2),
    slots_utilizados INT,
    velocidade_mhz INT,
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

-- Tabela de placas de rede
CREATE TABLE IF NOT EXISTS placas_rede (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    descricao VARCHAR(255),
    mac_address VARCHAR(17),
    ip_address VARCHAR(45),
    mascara VARCHAR(45),
    gateway VARCHAR(45),
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

-- Tabela de discos
CREATE TABLE IF NOT EXISTS discos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    unidade VARCHAR(10),
    tipo VARCHAR(50),
    tamanho_gb DECIMAL(12,2),
    espaco_livre_gb DECIMAL(12,2),
    sistema_arquivos VARCHAR(20),
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

-- Tabela de softwares instalados
CREATE TABLE IF NOT EXISTS softwares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    nome VARCHAR(255),
    versao VARCHAR(100),
    fabricante VARCHAR(255),
    data_instalacao DATE,
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE,
    INDEX idx_nome_software (nome)
);

-- Tabela de BIOS
CREATE TABLE IF NOT EXISTS bios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    versao VARCHAR(100),
    fabricante VARCHAR(255),
    data_release DATE,
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

-- Tabela de último logon
CREATE TABLE IF NOT EXISTS ultimo_logon (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    usuario VARCHAR(255),
    data_hora DATETIME,
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

-- Tabela de controladores
CREATE TABLE IF NOT EXISTS controladores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    tipo VARCHAR(50), -- IDE, USB, Floppy
    nome VARCHAR(255),
    descricao TEXT,
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

-- Tabela de periféricos de entrada
CREATE TABLE IF NOT EXISTS perifericos_entrada (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    tipo VARCHAR(20), -- Mouse, Teclado
    nome VARCHAR(255),
    descricao TEXT,
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

-- Tabela de monitores
CREATE TABLE IF NOT EXISTS monitores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    fabricante VARCHAR(255),
    tipo VARCHAR(100),
    descricao TEXT,
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

-- Tabela de impressoras
CREATE TABLE IF NOT EXISTS impressoras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    nome VARCHAR(255),
    porta VARCHAR(100),
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

-- Tabelas vazias para estrutura futura (conforme solicitado)
CREATE TABLE IF NOT EXISTS modems (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    placeholder VARCHAR(255),
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS ports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    placeholder VARCHAR(255),
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS registry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    placeholder VARCHAR(255),
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS slots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    placeholder VARCHAR(255),
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sounds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    placeholder VARCHAR(255),
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS storages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    placeholder VARCHAR(255),
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT,
    placeholder VARCHAR(255),
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

CREATE INDEX idx_maquinas_nome ON maquinas(nome_computador);
CREATE INDEX idx_softwares_maquina ON softwares(maquina_id);
CREATE INDEX idx_discos_maquina ON discos(maquina_id);
CREATE INDEX idx_placas_rede_maquina ON placas_rede(maquina_id);

USE inventario;
SELECT * FROM maquinas;
SHOW TABLES;
DESCRIBE maquinas;
SHOW TABLES;
DROP TABLE maquinas

CREATE TABLE maquinas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_computador VARCHAR(255) NOT NULL,
    dominio VARCHAR(255),
    usuario VARCHAR(255),
    ip VARCHAR(45),
    so VARCHAR(255),
    ram VARCHAR(100),
    armazenamento VARCHAR(100),
    software TEXT,
    ultima_atualizacao DATETIME,
    data_coleta DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_machine (nome_computador)
);


ALTER TABLE maquinas
ADD COLUMN usuario VARCHAR(255),
ADD COLUMN so VARCHAR(255),
ADD COLUMN ram VARCHAR(50),
ADD COLUMN armazenamento VARCHAR(50),
ADD COLUMN software JSON,
ADD COLUMN ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

DESCRIBE maquinas;

DROP TABLE IF EXISTS bios;
DROP TABLE IF EXISTS controladores;
DROP TABLE IF EXISTS discos;
DROP TABLE IF EXISTS impressoras;
DROP TABLE IF EXISTS memoria_ram;
DROP TABLE IF EXISTS modems;
DROP TABLE IF EXISTS monitores;
DROP TABLE IF EXISTS perifericos_entrada;
DROP TABLE IF EXISTS placas_rede;
DROP TABLE IF EXISTS ports;
DROP TABLE IF EXISTS processadores;
DROP TABLE IF EXISTS registry;
DROP TABLE IF EXISTS sistema_operacional;
DROP TABLE IF EXISTS slots;
DROP TABLE IF EXISTS softwares;
DROP TABLE IF EXISTS sounds;
DROP TABLE IF EXISTS storages;
DROP TABLE IF EXISTS ultimo_logon;
DROP TABLE IF EXISTS videos;

CREATE TABLE IF NOT EXISTS maquinas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_computador VARCHAR(255) NOT NULL,
    usuario VARCHAR(255),              -- usuário logado
    ip VARCHAR(45),                    -- endereço IP
    so VARCHAR(255),                   -- sistema operacional
    ram VARCHAR(50),                   -- memória RAM
    armazenamento VARCHAR(50),         -- armazenamento total
    software JSON,                     -- lista de softwares
    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        ON UPDATE CURRENT_TIMESTAMP
);

ALTER TABLE maquinas 
    CHANGE COLUMN usuario_logado usuario VARCHAR(255);

ALTER TABLE maquinas 
    CHANGE COLUMN ip_address ip VARCHAR(45);
    
CREATE INDEX idx_maquinas_nome ON maquinas (nome_computador);
CREATE INDEX idx_maquinas_usuario ON maquinas (usuario);

DESCRIBE maquinas;

INSERT INTO maquinas (
    nome_computador,
    dominio,
    usuario,
    ip,
    so,
    ram,
    armazenamento,
    software,
    ultima_atualizacao,
    data_coleta
) VALUES (
    'PC001',
    'DOMINIO_LOCAL',
    'alex.gama',
    '192.168.0.101',
    'Windows 11 Pro',
    '16GB',
    '512GB SSD',
    'Chrome, VSCode, Office',
    '2025-07-25 10:30:00', -- ultima_atualizacao (data simulada de meses anteriores)
    '2025-07-25 10:35:00'  -- data_coleta (data simulada de meses anteriores)
);

INSERT INTO maquinas (
    nome_computador,
    dominio,
    usuario,
    ip,
    so,
    ram,
    armazenamento,
    software,
    ultima_atualizacao,
    data_coleta
) VALUES (
    'PC002',
    'DOMINIO_LOCAL',
    'alex.Silva Sauro',
    '192.168.0.201',
    'Linux Ubunto',
    '32GB',
    '512GB SSD',
    'Chrome, VSCode, Libre Office',
    '2025-07-25 11:30:00', -- ultima_atualizacao (data simulada de meses anteriores)
    '2025-07-25 11:35:00'  -- data_coleta (data simulada de meses anteriores)
);


INSERT INTO maquinas (
    nome_computador,
    dominio,
    usuario,
    ip,
    so,
    ram,
    armazenamento,
    software,
    ultima_atualizacao,
    data_coleta
) VALUES (
    'PC003',
    'DOMINIO_LOCAL',
    'alex.Sauro',
    '192.168.0.10',
    'IOS Secoia',
    '8GB',
    '512GB SSD',
    'Chrome, VSCode, Galeria',
    '2025-07-05 10:30:00', -- ultima_atualizacao (data simulada de meses anteriores)
    '2025-07-05 10:35:00'  -- data_coleta (data simulada de meses anteriores)
);