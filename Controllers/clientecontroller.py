from typing import List
import services.supabase as db;
import models.Cliente as cliente;

def Incluir(cliente):
    try:
        # Consulta SQL
        query = """
            INSERT INTO Chamados (
                chamados_sh, 
                chamados_px, 
                titulo, 
                data_abertura, 
                pendencia_retorno, 
                usuario_resp, 
                status, 
                observacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Parâmetros da consulta
        params = (
            str(cliente.chsh), 
            str(cliente.chpx), 
            str(cliente.titulo), 
            cliente.data.strftime('%Y-%m-%d %H:%M:%S'),  # Converte data para string
            str(cliente.pend),  # Converte bool para int (0 ou 1)
            str(cliente.usr), 
            str(cliente.status), 
            str(cliente.obs)
        )

        # Executa a consulta
        db.cursor.execute(query, params)
        
        # Confirma a transação
        db.cnxn.commit()
        
        print("Chamado inserido com sucesso!")
    except Exception as e:
        print("Erro ao inserir chamado:", e)

def selecionarchamados():
    # Executa a consulta SQL
    db.cursor.execute("SELECT * FROM Chamados")
    rows = db.cursor.fetchall()
    
    # Cria uma lista de objetos Cliente
    constumerList = []
    for row in rows:
        constumerList.append(cliente.Cliente(
            id=row[0],  # ID
            chsh=row[1],  # Chamado Fácil
            chpx=row[2],  # Chamado Nordeste
            titulo=row[3],  # Título
            data=row[4],  # Data
            pend=row[5],  # Pendência
            usr=row[6],  # Usuário responsável
            status=row[7],  # Status
            obs=row[8]  # Observação
        ))
    
    return constumerList
