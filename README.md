# 📊 Pipeline de Datos – Carga a Base de Datos (ETL - Load)

## 📌 Descripción

Este proyecto implementa un **pipeline ETL (Extract, Transform, Load)** enfocado en la **etapa de carga de datos** hacia una base de datos relacional (PostgreSQL).

Se procesan datos provenientes de un archivo `ventas_sucias.csv`, aplicando limpieza, validaciones estructurales y semánticas, para finalmente almacenar únicamente los datos válidos en la base de datos.

---

## 🎯 Objetivos

* Garantizar la calidad de los datos antes de su almacenamiento
* Validar integridad estructural y semántica
* Asegurar la integridad referencial en base de datos
* Implementar trazabilidad mediante logging
* Permitir la reproducibilidad del proceso

---

## 🧱 Estructura del Proyecto

```
pipeline-ventas/
│
├── main.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── raw/
│   │   └── ventas_sucias.csv
│   ├── validated/
│   │   └── validated.csv
│   ├── rejected/
│   │   └── rechazados.csv
│
├── logs/
│   └── carga.log
```

---

## ⚙️ Tecnologías Utilizadas

* Python 3.12
* Pandas
* PostgreSQL
* psycopg2
* VS Code

---

## 🔄 Flujo del Pipeline

### 1. Ingesta

Se carga el archivo `ventas_sucias.csv` desde la carpeta `data/raw/`.

---

### 2. Limpieza de Datos

* Eliminación de espacios
* Normalización de texto (minúsculas)
* Manejo de valores nulos

---

### 3. Transformación de Datos

* Conversión de tipos:

  * Edad → numérico
  * Monto → numérico
  * Fecha → datetime

---

### 4. Validaciones

#### ✔ Validaciones Estructurales

* Campos obligatorios no vacíos
* Tipos de datos correctos
* Fechas válidas

#### ✔ Validaciones Semánticas

* Edad entre 0 y 120
* Monto mayor a 0
* Método de pago válido (`tarjeta`, `efectivo`, `transferencia`, `debito`)
* Ciudad válida (`santiago`, `valparaiso`, `viña del mar`)
* Fecha anterior a la actual

---

### 5. Separación de Datos

* `validated.csv` → datos correctos
* `rechazados.csv` → datos inválidos

---

### 6. Carga a Base de Datos

Se utilizan dos tablas:

#### Tabla `ciudad`

* Contiene ciudades únicas

#### Tabla `ventas`

* Contiene ventas válidas
* Relacionada mediante clave foránea con `ciudad`

---

### 7. Integridad y Control

* Uso de `ON CONFLICT DO NOTHING` para evitar duplicados
* Validación de existencia de claves foráneas
* Manejo de errores con logging

---

## 🧾 Logging

Se genera un archivo `logs/carga.log` que registra:

* Inicio y fin del proceso
* Registros insertados
* Registros ignorados (duplicados)
* Errores detectados
* Resumen final

---

## 📦 Instalación

```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecución

```bash
python main.py
```

---

## 📂 Archivos Generados

* `data/validated/validated.csv`
* `data/rejected/rechazados.csv`
* `logs/carga.log`

---

## 🔁 Reproducibilidad

El proceso es completamente reproducible:

* Uso de scripts automatizados
* Validaciones determinísticas
* Control de duplicados
* Registro de ejecución mediante logs

---

## ⚠️ Consideraciones

* No se deben subir credenciales de base de datos al repositorio
* Se recomienda el uso de variables de entorno (`.env`)

---

## 🧠 Conclusión

Este proyecto demuestra la implementación de un pipeline de datos robusto, asegurando calidad, integridad y trazabilidad en la carga de datos hacia una base de datos relacional, cumpliendo con buenas prácticas de ingeniería de datos.

---
