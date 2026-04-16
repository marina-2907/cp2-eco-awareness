from flask import Flask, render_template, request, jsonify
from db import get_connection

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/distribuir", methods=["POST"])
def distribuir():
    data = request.get_json()
    id_evento = data.get("id_evento")

    if not id_evento:
        return jsonify({"erro": "Informe o ID do evento."}), 400

    try:
        id_evento = int(id_evento)
    except ValueError:
        return jsonify({"erro": "ID do evento inválido."}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("BEGIN DISTRIBUIR_CASHBACK_EVENTO(:id); END;", {"id": id_evento})
        conn.commit()

        cursor.execute("""
            SELECT ID_USUARIO, NOME, SALDO
            FROM USUARIOS
            ORDER BY ID_USUARIO
        """)
        usuarios = [{"id": r[0], "nome": r[1], "saldo": float(r[2])} for r in cursor.fetchall()]

        cursor.execute("""
            SELECT ID_USUARIO, TIPO_INGRESSO, TOTAL_PRESENCAS,
                   PERCENTUAL_APLICADO, VALOR_CASHBACK
            FROM CASHBACK_LOG
            WHERE ID_EVENTO = :id
            ORDER BY ID_LOG
        """, {"id": id_evento})
        logs = [
            {
                "id_usuario": r[0],
                "tipo_ingresso": r[1],
                "total_presencas": r[2],
                "percentual": float(r[3]) * 100,
                "cashback": float(r[4])
            }
            for r in cursor.fetchall()
        ]

        return jsonify({"sucesso": True, "usuarios": usuarios, "logs": logs})

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"erro": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/health")
def health():
    return jsonify({"status": "ok", "mensagem": "Eco-Awareness online!"})

if __name__ == "__main__":
    app.run(debug=True)
