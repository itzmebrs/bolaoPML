from flask import Flask, request, render_template
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

app = Flask(__name__)

def conectar_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

@app.route('/')
def home():
    conn = conectar_db()
    cur = conn.cursor()

    # Buscar jogos
    cur.execute("SELECT id_jogo, time_1, time_2, data_jogo FROM jogos ORDER BY data_jogo")
    jogos = cur.fetchall()

    # Buscar usuários
    cur.execute("SELECT id_usuario, nome FROM usuarios ORDER BY nome")
    usuarios = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", jogos=jogos, usuarios=usuarios)

@app.route('/palpite', methods=['POST'])
def registrar_palpites():
    usuario_id = request.form['usuario']
    senha = request.form['senha']

    conn = conectar_db()
    cur = conn.cursor()

    # Validar senha do usuário
    cur.execute("SELECT senha FROM usuarios WHERE id = %s", (usuario_id,))
    resultado = cur.fetchone()
    if not resultado or resultado[0] != senha:
        return "Senha incorreta."

    # Loop nos jogos
    for key in request.form:
        if key.startswith("palpite_"):
            jogo_id = key.split("_")[1]
            palpite_casa = request.form.get(f"palpite_{jogo_id}_casa")
            palpite_fora = request.form.get(f"palpite_{jogo_id}_fora")

            # Inserir palpite
            cur.execute("""
                INSERT INTO palpites (id_usuario, id_jogo, palpite_1, palpite_2)
                VALUES (%s, %s, %s)
            """, (usuario_id, jogo_id, palpite_casa, palpite_fora))

    conn.commit()
    cur.close()
    conn.close()
    
    return "Palpites salvos com sucesso!"

if __name__ == '__main__':
    app.run(debug=True)