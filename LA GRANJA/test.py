import oracledb

dsn = "localhost:1521/XEPDB1"
try:
    conexion = oracledb.connect(user="C##ANGEL", password="M423i32R4", dsn=dsn)
    print("✅ Conexión exitosa a Oracle")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
