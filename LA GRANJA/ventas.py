import os
from flask import Flask, render_template, request
import oracledb

app = Flask(__name__)

# Conexión a Oracle (usa variables de entorno por seguridad)
dsn = os.getenv("ORACLE_DSN", "localhost:1521/XEPDB1")
user = os.getenv("ORACLE_USER", "C##ANGEL")
password = os.getenv("ORACLE_PASSWORD", "M423i32R4")

try:
    conexion = oracledb.connect(user=user, password=password, dsn=dsn)
    print("✅ Conexión exitosa a Oracle.")
except Exception as e:
    print(f"❌ Error en la conexión: {e}")

@app.route('/ventas', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            print("📋 Datos recibidos del formulario:", request.form)

            cliente_nombre = request.form.get('nombre')
            cliente_telefono = request.form.get('telefono')
            cliente_direccion = request.form.get('direccion')

            tipos_huevo = request.form.getlist('tipo_huevo[]')
            cantidades_cubetas = list(map(int, request.form.getlist('cantidad_cubetas[]')))
            cantidades_unidades = list(map(int, request.form.getlist('cantidad_unidades[]')))

            precios_unidad = {
                "HUEVO BLANCO A": 417, "HUEVO BLANCO AA": 450, "HUEVO BLANCO B": 367, "HUEVO BLANCO EXTRA": 533,
                "HUEVO ROJO A": 417, "HUEVO ROJO AA": 450, "HUEVO ROJO B": 367, "HUEVO ROJO EXTRA": 533
            }
            precios_cubeta = {
                "HUEVO BLANCO A": 12500, "HUEVO BLANCO AA": 13500, "HUEVO BLANCO B": 11000, "HUEVO BLANCO EXTRA": 16000,
                "HUEVO ROJO A": 12500, "HUEVO ROJO AA": 13500, "HUEVO ROJO B": 11000, "HUEVO ROJO EXTRA": 16000
            }

            valor_total = 0
            cursor = conexion.cursor()

            for tipo, cubetas, unidades in zip(tipos_huevo, cantidades_cubetas, cantidades_unidades):
                valor_total += (cubetas * precios_cubeta[tipo]) + (unidades * precios_unidad[tipo])
                cantidad_total = (cubetas * 30) + unidades

                cursor.execute("""
                    UPDATE huevos
                    SET cantidad = cantidad - :cantidad
                    WHERE tipo_huevo = :tipo_huevo
                """, {"cantidad": cantidad_total, "tipo_huevo": tipo})

                cursor.execute("""
                    INSERT INTO ventas_huevos (id, cliente_nombre, cliente_telefono, cliente_direccion, tipo_huevo, cantidad_cubetas, cantidad_unidades, fecha_venta, valor_total)
                    VALUES (ventas_huevos_seq.NEXTVAL, :nombre, :telefono, :direccion, :tipo_huevo, :cantidad_cubetas, :cantidad_unidades, SYSDATE, :valor_total)
                """, {
                    "nombre": cliente_nombre,
                    "telefono": cliente_telefono,
                    "direccion": cliente_direccion,
                    "tipo_huevo": tipo,
                    "cantidad_cubetas": cubetas,
                    "cantidad_unidades": unidades,
                    "valor_total": valor_total
                })

            conexion.commit()
            cursor.close()
            return f"✅ Venta registrada con éxito. Valor total: ${valor_total}"

        except Exception as e:
            print(f"❌ Error al procesar la venta: {e}")
            return f"❌ Error al procesar la venta: {e}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
