# db_manager.py - Actualizado para usar python-oracledb

# CAMBIO 1: Importar 'oracledb' en lugar de 'cx_Oracle'
import oracledb as oracle 
from oracledb_config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SERVICE

class DBManager:
    """Clase para gestionar la conexión y operaciones CRUD con Oracle."""

    def __init__(self):
        self.connection = None
        
        # CAMBIO 2: La conexión directa ya no requiere oracle.makedsn
        # En su lugar, el DSN se define con el formato HOST:PORT/SERVICE_NAME
        self.dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"


    def connect(self):
        """Establece la conexión a la base de datos."""
        try:
            # Uso del método de conexión optimizado de oracledb
            self.connection = oracle.connect(
                user=DB_USER, 
                password=DB_PASSWORD, 
                dsn=self.dsn
            )
            print("Conexión a Oracle exitosa.")
        except oracle.Error as e:
            error, = e.args
            # La estructura de error puede variar ligeramente, pero el código es robusto
            print(f"Error de conexión a Oracle: {error.code} - {error.message}")
            self.connection = None


    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.connection:
            self.connection.close()
            print("Conexión a Oracle cerrada.")


    # --- Métodos de Lectura (Consulta) ---

    def select_all(self, table_name, active_only=True):
        """Retorna todos los registros activos de una tabla."""
        # Se asume que self.connection es válido aquí
        cursor = self.connection.cursor()
        
        # Se mantienen los nombres de tablas que tienen 'estado_registro'
        tables_with_state = ['Turista', 'Sucursal', 'Hotel', 'Avion', 'Categoria_Plaza', 'Vuelo', 'Correo', 'Telefono']
        
        if active_only and table_name in tables_with_state:
            query = f"SELECT * FROM {table_name} WHERE estado_registro = 'A'"
        else:
            query = f"SELECT * FROM {table_name}"
        
        try:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            return columns, cursor.fetchall()
        except oracle.Error as e:
            print(f"Error al leer datos de {table_name}: {e}")
            return [], []
        finally:
            cursor.close()


    def select_turista_by_id(self, turista_id):
        """Retorna los datos de un turista específico para la vista Cliente."""
        cursor = self.connection.cursor()
        query = """
            SELECT 
                t.nombre1, t.apellido1, t.direccion, c.correo, tel.telefono
            FROM 
                Turista t
            LEFT JOIN Correo c ON t.id_turista = c.id_turista AND c.estado_registro = 'A'
            LEFT JOIN Telefono tel ON t.id_turista = tel.id_turista AND tel.estado_registro = 'A'
            WHERE t.id_turista = :id AND t.estado_registro = 'A'
        """
        try:
            # oracledb usa la misma sintaxis de binding
            cursor.execute(query, {'id': turista_id})
            columns = [col[0] for col in cursor.description]
            return columns, cursor.fetchone()
        except oracle.Error as e:
            print(f"Error al buscar Turista ID {turista_id}: {e}")
            return [], None
        finally:
            cursor.close()

    # --- Método de Actualización ---

    def update_turista_data(self, turista_id, data):
        """Actualiza datos básicos de un Turista."""
        cursor = self.connection.cursor()
        query = """
            UPDATE Turista
            SET nombre1 = :n1, nombre2 = :n2, apellido1 = :a1, apellido2 = :a2, direccion = :dir
            WHERE id_turista = :id
        """
        try:
            # Los parámetros de data deben coincidir con los placeholders de la consulta
            cursor.execute(query, {
                'n1': data.get('nombre1'),
                'n2': data.get('nombre2'),
                'a1': data.get('apellido1'),
                'a2': data.get('apellido2'),
                'dir': data.get('direccion'),
                'id': turista_id
            })
            self.connection.commit()
            print(f"Turista ID {turista_id} actualizado.")
            return True
        except oracle.Error as e:
            error, = e.args
            print(f"Error al actualizar Turista: {error.message}")
            return False
        finally:
            cursor.close()
    
    # --- Método de Inserción ---

    def insert_turista(self, data):
        """Inserta un nuevo Turista."""
        cursor = self.connection.cursor()
        query = """
            INSERT INTO Turista (nombre1, nombre2, apellido1, apellido2, direccion)
            VALUES (:n1, :n2, :a1, :a2, :dir)
        """
        try:
            # Asegurar que 'data' contiene todas las claves requeridas por la consulta
            cursor.execute(query, data)
            self.connection.commit()
            print("Nuevo Turista insertado.")
            return True
        except oracle.Error as e:
            error, = e.args
            print(f"Error al insertar Turista: {error.message}")
            return False
        finally:
            cursor.close()

    # --- Método de Eliminación Lógica ---

    def logical_delete(self, table_name, pk_column, pk_value):
        """Realiza un eliminado lógico (estado_registro = 'I')."""
        cursor = self.connection.cursor()
        query = f"""
            UPDATE {table_name}
            SET estado_registro = 'I'
            WHERE {pk_column} = :pk_val
        """
        try:
            cursor.execute(query, {'pk_val': pk_value})
            self.connection.commit()
            print(f"Registro en {table_name} con ID {pk_value} marcado como Inactivo.")
            return True
        except oracle.Error as e:
            error, = e.args
            print(f"Error al realizar eliminado lógico en {table_name}: {error.message}")
            return False
        finally:
            cursor.close()