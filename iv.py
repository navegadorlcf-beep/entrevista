
import streamlit as st
import sqlite3
from datetime import datetime

# ---------------- BANCO ----------------
conn = sqlite3.connect("pesquisa.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS respostas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    sentimento TEXT,
    categoria TEXT,
    intensidade INTEGER,
    data TEXT
)
""")
conn.commit()

# ---------------- INTERFACE ----------------
st.title("📊 Olá, bem-vindo(a) a nossa pesquisa, obrigado por participar!")

nome = st.text_input("Qual é seu primeiro nome:")

if nome:
    sentimento = st.text_area("Descreva como você está se sentindo hoje e por que:")

    categoria = st.selectbox(
        "Classifique seu humor:",
        ["Feliz", "Neutro", "Triste", "Ansioso", "Irritado"]
    )

    intensidade = st.slider("Intensidade:", 1, 5)

    if st.button("Enviar resposta"):
        if sentimento.strip() == "":
            st.warning("Descreva como você está se sentindo!")
        else:
            data = datetime.now().strftime("%d/%m/%Y %H:%M")

            cursor.execute("""
            INSERT INTO respostas (nome, sentimento, categoria, intensidade, data)
            VALUES (?, ?, ?, ?, ?)
            """, (nome, sentimento, categoria, intensidade, data))

            conn.commit()
            st.success("Resposta registrada!")

# ---------------- DADOS ----------------
st.subheader("📋 Dados coletados")

cursor.execute("SELECT id, nome, sentimento, categoria, intensidade, data FROM respostas")
dados = cursor.fetchall()

texto = ""

for d in dados:
    linha = f"""
ID: {d[0]}
Data: {d[5]}
Nome: {d[1]}
Sentimento: {d[2]}
Categoria: {d[3]}
Intensidade: {d[4]}
------------------------
"""
    st.text(linha)
    texto += linha + "\n"

# ---------------- EDIÇÃO ----------------
st.subheader("✏️ Editar resposta")

ids = [str(d[0]) for d in dados]

if ids:
    id_selecionado = st.selectbox("Selecione o ID da resposta:", ids)

    cursor.execute(
        "SELECT nome, sentimento, categoria, intensidade FROM respostas WHERE id=?",
        (id_selecionado,)
    )
    dado = cursor.fetchone()

    if dado:
        novo_nome = st.text_input("Nome", value=dado[0])
        novo_sentimento = st.text_area("Sentimento", value=dado[1])
        opcoes = ["Feliz", "Neutro", "Triste", "Ansioso", "Irritado"]

        nova_categoria = st.selectbox(
            "Categoria",
            opcoes,
            index=opcoes.index(dado[2])
        )

        nova_intensidade = st.slider("Intensidade", 1, 5, value=dado[3])

        if st.button("Atualizar"):
            if novo_sentimento.strip() == "":
                st.warning("O sentimento não pode estar vazio!")
            else:
                cursor.execute("""
                UPDATE respostas
                SET nome=?, sentimento=?, categoria=?, intensidade=?
                WHERE id=?
                """, (novo_nome, novo_sentimento, nova_categoria, nova_intensidade, id_selecionado))

                conn.commit()
                st.success("Resposta atualizada!")

# ---------------- DOWNLOAD COM SENHA ----------------
st.subheader("📥 Download dos dados")

senha_download = st.text_input("Digite a senha para baixar:", type="password", key="senha_download")

if senha_download == "1234":
    st.download_button(
        "Baixar dados",
        texto,
        file_name="dados_pesquisa.txt"
    )
elif senha_download:
    st.error("Senha incorreta!")

# ---------------- LIMPAR REGISTROS ----------------
st.subheader("🧹 Limpar todos os registros")

senha_limpar = st.text_input("Digite a senha para limpar o banco:", type="password", key="senha_limpar")

confirmar = st.checkbox("Tenho certeza que quero apagar TODOS os dados")

if st.button("Apagar tudo"):
    if senha_limpar != "admin123":
        st.error("Senha incorreta!")
    elif not confirmar:
        st.warning("Confirme que deseja apagar todos os dados!")
    else:
        cursor.execute("DELETE FROM respostas")
        conn.commit()
        st.success("Todos os registros foram apagados!")