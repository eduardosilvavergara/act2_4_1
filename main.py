# =========================
# IMPORTS
# =========================
import os
import pandas as pd
import psycopg2
import logging

# =========================
# 1. CREAR ESTRUCTURA
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

data_raw = os.path.join(BASE_DIR, "data/raw")
data_validated = os.path.join(BASE_DIR, "data/validated")
data_rejected = os.path.join(BASE_DIR, "data/rejected")
logs_dir = os.path.join(BASE_DIR, "logs")

os.makedirs(data_raw, exist_ok=True)
os.makedirs(data_validated, exist_ok=True)
os.makedirs(data_rejected, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)

# =========================
# 2. CONFIGURAR LOG
# =========================
log_path = os.path.join(logs_dir, "carga.log")

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)

logging.info("=== INICIO PIPELINE ===")

# =========================
# 3. LEER CSV
# =========================
csv_path = os.path.join(data_raw, "ventas_sucias.csv")

if not os.path.exists(csv_path):
    raise FileNotFoundError("El archivo ventas_sucias.csv no existe en data/raw/")

df = pd.read_csv(csv_path)

# =========================
# 4. LIMPIEZA
# =========================
df['nombre'] = df['nombre'].astype(str).str.strip()
df['nombre'].replace("nan", None, inplace=True)

df['ciudad'] = df['ciudad'].astype(str).str.strip().str.lower()
df['metodo_pago'] = df['metodo_pago'].astype(str).str.strip().str.lower()

# =========================
# 5. CONVERSIÓN TIPOS
# =========================
df['edad'] = pd.to_numeric(df['edad'], errors='coerce')
df['monto'] = pd.to_numeric(df['monto'], errors='coerce')
df['fecha_compra'] = pd.to_datetime(df['fecha_compra'], errors='coerce')

# =========================
# 6. VALIDACIONES
# =========================
metodos_validos = ['tarjeta', 'efectivo', 'transferencia', 'debito']
ciudades_validas = ['santiago', 'valparaiso', 'viña del mar']

df['val_nombre'] = df['nombre'].notna() & (df['nombre'] != "")
df['val_edad'] = df['edad'].between(0, 120)
df['val_monto'] = df['monto'] > 0
df['val_fecha'] = df['fecha_compra'].notna()
df['val_metodo'] = df['metodo_pago'].isin(metodos_validos)
df['val_ciudad'] = df['ciudad'].isin(ciudades_validas)

df['valido'] = (
    df['val_nombre'] &
    df['val_edad'] &
    df['val_monto'] &
    df['val_fecha'] &
    df['val_metodo'] &
    df['val_ciudad']
)

# =========================
# 7. ELIMINAR DUPLICADOS
# =========================
df = df.drop_duplicates(subset=['id'])

# =========================
# 8. SEPARACIÓN
# =========================
validos = df[df['valido'] == True]
rechazados = df[df['valido'] == False]

# =========================
# 9. GUARDAR CSV
# =========================
valid_path = os.path.join(data_validated, "validated.csv")
rech_path = os.path.join(data_rejected, "rechazados.csv")

validos.to_csv(valid_path, index=False)
rechazados.to_csv(rech_path, index=False)

logging.info(f"Registros válidos: {len(validos)}")
logging.info(f"Registros rechazados: {len(rechazados)}")

# =========================
# 10. CONEXIÓN DB
# =========================
conn = psycopg2.connect(
    host="ep-floral-lab-ac48n63j.sa-east-1.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="npg_4d1OGlTyVujk",
    port="5432"
)
cursor = conn.cursor()

# =========================
# 11. CREAR TABLAS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS ciudad (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ventas (
    id INT PRIMARY KEY,
    nombre VARCHAR(100),
    edad INT,
    ciudad_id INT,
    fecha_compra DATE,
    monto INT,
    metodo_pago VARCHAR(50),
    FOREIGN KEY (ciudad_id) REFERENCES ciudad(id)
);
""")

conn.commit()

# =========================
# 12. INSERTAR CIUDADES
# =========================
for ciudad in validos['ciudad'].dropna().unique():
    cursor.execute(
        "INSERT INTO ciudad (nombre) VALUES (%s) ON CONFLICT DO NOTHING",
        (ciudad,)
    )

conn.commit()

# =========================
# 13. INSERTAR VENTAS
# =========================
insertados = 0
ignorados = 0
errores = 0

for _, row in validos.iterrows():
    try:
        cursor.execute("SELECT id FROM ciudad WHERE nombre=%s", (row['ciudad'],))
        result = cursor.fetchone()

        if result is None:
            logging.error(f"Ciudad no encontrada: {row['ciudad']}")
            errores += 1
            continue

        ciudad_id = result[0]

        cursor.execute("""
        INSERT INTO ventas VALUES (%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO NOTHING
        """, (
            int(row['id']),
            row['nombre'],
            int(row['edad']),
            ciudad_id,
            row['fecha_compra'],
            int(row['monto']),
            row['metodo_pago']
        ))

        if cursor.rowcount == 0:
            ignorados += 1
            logging.warning(f"ID {row['id']} duplicado")
        else:
            insertados += 1
            logging.info(f"Insertado ID {row['id']}")

    except Exception as e:
        errores += 1
        conn.rollback()
        logging.error(f"Error ID {row['id']}: {e}")

# =========================
# 14. COMMIT FINAL
# =========================
conn.commit()

# =========================
# 15. RESUMEN
# =========================
logging.info("=== RESUMEN ===")
logging.info(f"Insertados: {insertados}")
logging.info(f"Ignorados: {ignorados}")
logging.info(f"Errores: {errores}")
logging.info("=== FIN PIPELINE ===")

logging.shutdown()

print("Proceso finalizado correctamente 🚀")