# 🌎 Sistema de Gestión de Turismo

Un sistema desarrollado en **Python** con base de datos **Oracle**, diseñado para gestionar turistas, realizar operaciones CRUD, y mantener auditorías automáticas mediante triggers.

---

## 🧩 Requisitos

- 🐍 **Python 3.7 o superior**
- 🗃️ **Base de datos Oracle (XE o superior)**

---

## ⚙️ Instalación de dependencias

Ejecuta el siguiente comando:

```bash
pip install oracledb
```

---

## 🔧 Configuración de la base de datos

Edita el archivo `oracledb_config.py` y reemplaza con tus credenciales locales:

```python
DB_USER = "turismo"
DB_PASSWORD = "123456"
DB_HOST = "localhost"
DB_PORT = 1521
DB_SERVICE = "XE"
```

---

## 🗂️ Ejecución de scripts SQL

Ejecuta los siguientes archivos en orden dentro de Oracle SQL Developer o tu herramienta preferida:

1. `creacion de tablas paso 1.sql`  
2. `triggers paso 2.sql`  
3. `insercion de datos paso 3.sql`  
4. `eliminado logico paso 4.sql`

---

## ▶️ Ejecución del programa

```bash
python3 main.py
```

---

## 💼 Funcionalidades

### 👤 Modo Cliente
- Visualización y edición de datos personales.

### 🧑‍💼 Modo Administrador
- CRUD completo de turistas.
- Eliminado lógico de registros.
- Auditoría automática mediante triggers.

---

## 🧠 Autor

1. `Teddy Castellanos`  
2. `Javier Sandoval`
3. `Allen Espino`
4. `Erwin Ramirez`

💻 Proyecto para curso de **Base de Datos – Universidad Mariano Gálvez**

---

## 🪪 Licencia

Este proyecto es de uso académico y libre para aprendizaje.
