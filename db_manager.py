# db_manager.py - FINAL con CRUD, Bitacora y M:N

import oracledb as oracle
from datetime import date 

# Asegúrate de que este archivo exista y tenga tus credenciales:
# DB_USER = "turismo"
# DB_PASSWORD = "123"
# DB_HOST = "localhost" o la IP de tu VM
# DB_PORT = "1521"
# DB_SERVICE = "XEPDB1" (o el nombre de tu servicio/SID)
try:
    from oracledb_config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SERVICE
except ImportError:
    print("WARNING: oracledb_config.py no encontrado. Usando valores de placeholder.")
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SERVICE = "user", "pass", "host", "1521", "service"


class DBManager:
    """Clase para gestionar la conexión y operaciones CRUD con Oracle."""

    def __init__(self):
        self.connection = None
        self.dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"


    def connect(self):
        """Establece la conexión a la base de datos."""
        try:
            self.connection = oracle.connect(
                user=DB_USER, 
                password=DB_PASSWORD, 
                dsn=self.dsn
            )
            print("Conexión a Oracle exitosa.")
        except oracle.Error as e:
            error, = e.args
            print(f"Error de conexión a Oracle: {error.code} - {error.message}")
            self.connection = None


    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.connection:
            self.connection.close()
            print("Conexión a Oracle cerrada.")

    # ======================================================================
    # === MÉTODOS DE LECTURA (SELECT) ======================================
    # ======================================================================

    def select_all(self, table_name, active_only=True):
        """Retorna todos los registros (opcionalmente solo activos) de una tabla."""
        if not self.connection: return [], []
        cursor = self.connection.cursor()
        
        tables_with_state = [
            'Turista', 'Sucursal', 'Hotel', 'Avion', 'Categoria_Plaza', 
            'Vuelo', 'Correo', 'Telefono', 'Categoria_Plaza_Ocupada', 'Flag_Bitacora'
        ]
        
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
        """
        Retorna los datos del Turista (incluyendo todos los nombres/apellidos) 
        y el correo y teléfono ACTIVO.
        """
        if not self.connection: return [], None
        cursor = self.connection.cursor()
        query = """
            SELECT 
                t.id_turista, t.nombre1, t.nombre2, t.nombre3, t.apellido1, t.apellido2, t.direccion, 
                c.correo, tel.telefono
            FROM 
                Turista t
            LEFT JOIN Correo c ON t.id_turista = c.id_turista AND c.estado_registro = 'A'
            LEFT JOIN Telefono tel ON t.id_turista = tel.id_turista AND tel.estado_registro = 'A'
            WHERE t.id_turista = :id AND t.estado_registro = 'A'
        """
        try:
            cursor.execute(query, {'id': turista_id})
            columns = [col[0] for col in cursor.description]
            return columns, cursor.fetchone()
        except oracle.Error as e:
            print(f"Error al buscar Turista ID {turista_id}: {e}")
            return [], None
        finally:
            cursor.close()
            
    def search_turista_by_name(self, nombre, apellido):
        """Busca turistas activos por Primer Nombre y Primer Apellido."""
        if not self.connection: return [], []
        cursor = self.connection.cursor()
        
        query = """
            SELECT 
                ID_TURISTA, NOMBRE1, APELLIDO1, DIRECCION 
            FROM 
                Turista 
            WHERE 
                UPPER(NOMBRE1) = UPPER(:nombre) AND 
                UPPER(APELLIDO1) = UPPER(:apellido) AND 
                ESTADO_REGISTRO = 'A'
        """
        try:
            cursor.execute(query, {'nombre': nombre, 'apellido': apellido})
            columns = [col[0] for col in cursor.description]
            data = cursor.fetchall()
            return columns, data
        except oracle.Error as e:
            print(f"Error al buscar turista por nombre: {e}")
            return [], []
        finally:
            cursor.close()

    def select_turista_reservations(self, turista_id):
        """Obtiene las reservas (Hotel, Vuelo, Sucursal) activas de un turista."""
        if not self.connection: return {}
        cursor = self.connection.cursor()
        reservations = {'hotel': None, 'vuelo': None, 'sucursal': None}

        # Query Hotel
        query_hotel = """
            SELECT h.nombre, th.regimen, th.fecha_llegada, th.fecha_salida
            FROM Turista_Hotel th JOIN Hotel h ON th.id_hotel = h.id_hotel
            WHERE th.id_turista = :id
        """
        # Query Vuelo (Simplificado para mostrar datos clave)
        query_vuelo = """
            SELECT v.origen || ' -> ' || v.destino AS ruta, v.fecha_hora, cp.nombre AS categoria
            FROM Turista_Vuelo tv 
            JOIN Vuelo v ON tv.id_vuelo = v.id_vuelo
            JOIN Categoria_Plaza_Ocupada cpo ON tv.id_categoria_plaza_ocupada = cpo.id_categoria_plaza_ocupada
            JOIN Categoria_Plaza cp ON cpo.id_categoria = cp.id_categoria
            WHERE tv.id_turista = :id
        """
        # Query Sucursal
        query_sucursal = """
            SELECT s.direccion, s.ciudad
            FROM Turista_Sucursal ts JOIN Sucursal s ON ts.id_sucursal = s.id_sucursal
            WHERE ts.id_turista = :id
        """
        try:
            cursor.execute(query_hotel, {'id': turista_id})
            reservations['hotel'] = cursor.fetchone()
            
            cursor.execute(query_vuelo, {'id': turista_id})
            reservations['vuelo'] = cursor.fetchone()
            
            cursor.execute(query_sucursal, {'id': turista_id})
            reservations['sucursal'] = cursor.fetchone()

            return reservations
        except oracle.Error as e:
            print(f"Error al obtener reservas del Turista ID {turista_id}: {e}")
            return {}
        finally:
            cursor.close()

    def select_bitacora_full(self):
        """
        Selecciona todos los registros de la tabla Bitacora, ordenados por fecha.
        """
        if not self.connection: return [], []
        cursor = self.connection.cursor()
        query = """
            SELECT 
                ID_BITACORA, FECHA, NOMBRE_TABLA_MODIFICADA, TIPO_ACCION, 
                CAMPO_MODIFICADO, VALOR_ANTERIOR, VALOR_ACTUAL, ID_FLAG_BITACORA 
            FROM Bitacora 
            ORDER BY FECHA DESC
        """
        try:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            data = cursor.fetchall()
            return columns, data
        except oracle.Error as e:
            print(f"Error al seleccionar la Bitacora: {e}")
            return [], []
        finally:
            cursor.close()
            
    def get_catalog_for_dropdown(self, table_name, id_col, name_col):
        """Obtiene ID y Nombre de una tabla para usar en ComboBoxes."""
        if not self.connection: return []
        cursor = self.connection.cursor()
        
        # Las tablas de catálogo tienen estado_registro, excepto algunas de unión
        query = f"SELECT {id_col}, {name_col} FROM {table_name} WHERE estado_registro = 'A' ORDER BY {name_col}"
        
        try:
            cursor.execute(query)
            # Retorna una lista de tuplas [(ID, Nombre), ...]
            return cursor.fetchall() 
        except oracle.Error as e:
            print(f"Error al obtener catálogo {table_name}: {e}")
            return []
        finally:
            cursor.close()

    # ======================================================================
    # === MÉTODOS DE INSERCIÓN BÁSICOS =====================================
    # ======================================================================

    def insert_turista(self, data):
        """Inserta un nuevo Turista y retorna su ID."""
        if not self.connection: return 0
        cursor = self.connection.cursor()
        new_id = cursor.var(int) 

        query = """
            INSERT INTO Turista (nombre1, nombre2, nombre3, apellido1, apellido2, direccion, estado_registro)
            VALUES (:n1, :n2, :n3, :a1, :a2, :dir, 'A')
            RETURNING id_turista INTO :new_id
        """
        try:
            cursor.execute(query, {
                'n1': data.get('n1'), 'n2': data.get('n2'), 'n3': data.get('n3'), 
                'a1': data.get('a1'), 'a2': data.get('a2'), 'dir': data.get('dir'),
                'new_id': new_id
            })
            self.connection.commit()
            return new_id.getvalue()[0]
        except oracle.Error as e:
            error, = e.args
            print(f"Error al insertar Turista: {error.message}")
            self.connection.rollback()
            return 0
        finally:
            cursor.close()

    def insert_correo(self, turista_id, correo):
        """Inserta un nuevo Correo activo para un Turista."""
        if not self.connection: return False
        cursor = self.connection.cursor()
        query = "INSERT INTO Correo (id_turista, correo, estado_registro) VALUES (:id, :correo, 'A')"
        try:
            cursor.execute(query, {'id': turista_id, 'correo': correo})
            self.connection.commit()
            return True
        except oracle.Error as e:
            print(f"Error al insertar correo para Turista ID {turista_id}: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def insert_telefono(self, turista_id, telefono):
        """Inserta un nuevo Teléfono activo para un Turista."""
        if not self.connection: return False
        cursor = self.connection.cursor()
        query = "INSERT INTO Telefono (id_turista, telefono, estado_registro) VALUES (:id, :telefono, 'A')"
        try:
            cursor.execute(query, {'id': turista_id, 'telefono': telefono})
            self.connection.commit()
            return True
        except oracle.Error as e:
            print(f"Error al insertar teléfono para Turista ID {turista_id}: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
            
    # ======================================================================
    # === MÉTODOS DE RELACIÓN M:N (RESERVAS) - NUEVOS ======================
    # ======================================================================
    
    def insert_turista_sucursal(self, turista_id, sucursal_id):
        """Asigna un Turista a una Sucursal."""
        if not self.connection: return False
        cursor = self.connection.cursor()
        
        # Eliminar cualquier asignación anterior (para simplificar: 1 turista = 1 sucursal)
        self.clear_turista_reservations(turista_id, 'Turista_Sucursal')
        
        query = "INSERT INTO Turista_Sucursal (id_turista, id_sucursal) VALUES (:tid, :sid)"
        try:
            cursor.execute(query, {'tid': turista_id, 'sid': sucursal_id})
            self.connection.commit()
            return True
        except oracle.Error as e:
            print(f"Error al asignar sucursal al Turista ID {turista_id}: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def insert_turista_hotel(self, turista_id, hotel_id, regimen, llegada, salida):
        """Asigna un Turista a un Hotel con fechas y régimen."""
        if not self.connection: return False
        cursor = self.connection.cursor()

        # Eliminar cualquier asignación anterior (para simplificar: 1 turista = 1 hotel)
        self.clear_turista_reservations(turista_id, 'Turista_Hotel')

        query = """
            INSERT INTO Turista_Hotel (id_turista, id_hotel, regimen, fecha_llegada, fecha_salida)
            VALUES (:tid, :hid, :reg, TO_DATE(:llegada, 'YYYY-MM-DD'), TO_DATE(:salida, 'YYYY-MM-DD'))
        """
        try:
            cursor.execute(query, {
                'tid': turista_id, 
                'hid': hotel_id, 
                'reg': regimen, 
                'llegada': llegada,
                'salida': salida
            })
            self.connection.commit()
            return True
        except oracle.Error as e:
            print(f"Error al reservar hotel para Turista ID {turista_id}: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def insert_turista_vuelo(self, turista_id, vuelo_id, cpo_id):
        """Asigna un Turista a un Vuelo con una Plaza Ocupada."""
        if not self.connection: return False
        cursor = self.connection.cursor()

        # Eliminar cualquier asignación anterior (para simplificar: 1 turista = 1 vuelo)
        self.clear_turista_reservations(turista_id, 'Turista_Vuelo')
        
        query = """
            INSERT INTO Turista_Vuelo (id_turista, id_vuelo, id_categoria_plaza_ocupada)
            VALUES (:tid, :vid, :cpo)
        """
        try:
            cursor.execute(query, {'tid': turista_id, 'vid': vuelo_id, 'cpo': cpo_id})
            self.connection.commit()
            # Opcional: Marcar CPO como 'ocupada' si la tabla de CPO no tiene un estado
            return True
        except oracle.Error as e:
            print(f"Error al reservar vuelo para Turista ID {turista_id}: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
            
    def clear_turista_reservations(self, turista_id, table_name):
        """Elimina las reservas de un turista en una tabla M:N específica."""
        if not self.connection: return
        cursor = self.connection.cursor()
        query = f"DELETE FROM {table_name} WHERE id_turista = :id"
        try:
            cursor.execute(query, {'id': turista_id})
            self.connection.commit()
        except oracle.Error as e:
            print(f"Error al limpiar reservas en {table_name}: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    # ======================================================================
    # === MÉTODOS DE ACTUALIZACIÓN y ELIMINADO LÓGICO ======================
    # ======================================================================

    def update_turista_data(self, turista_id, data):
        """Actualiza todos los campos básicos de un Turista."""
        if not self.connection: return False
        cursor = self.connection.cursor()
        
        query = """
            UPDATE Turista
            SET nombre1 = :n1, nombre2 = :n2, nombre3 = :n3, 
                apellido1 = :a1, apellido2 = :a2, direccion = :dir
            WHERE id_turista = :id
        """
        try:
            cursor.execute(query, {
                'n1': data.get('nombre1'), 'n2': data.get('nombre2'), 'n3': data.get('nombre3'),
                'a1': data.get('apellido1'), 'a2': data.get('apellido2'), 'dir': data.get('direccion'),
                'id': turista_id
            })
            self.connection.commit()
            return True
        except oracle.Error as e:
            error, = e.args
            print(f"Error al actualizar Turista: {error.message}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
            
    def update_correo_or_insert(self, turista_id, nuevo_correo):
        """Desactiva el correo anterior y registra el nuevo como activo."""
        if not self.connection: return False
        cursor = self.connection.cursor()
        try:
            update_old = "UPDATE Correo SET estado_registro = 'I' WHERE id_turista = :id AND estado_registro = 'A'"
            cursor.execute(update_old, {'id': turista_id})
            insert_new = "INSERT INTO Correo (id_turista, correo, estado_registro) VALUES (:id, :correo, 'A')"
            cursor.execute(insert_new, {'id': turista_id, 'correo': nuevo_correo})
            self.connection.commit()
            return True
        except oracle.Error as e:
            print(f"Error al actualizar/insertar correo: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def update_telefono_or_insert(self, turista_id, nuevo_telefono):
        """Desactiva el teléfono anterior y registra el nuevo como activo."""
        if not self.connection: return False
        cursor = self.connection.cursor()
        try:
            update_old = "UPDATE Telefono SET estado_registro = 'I' WHERE id_turista = :id AND estado_registro = 'A'"
            cursor.execute(update_old, {'id': turista_id})
            insert_new = "INSERT INTO Telefono (id_turista, telefono, estado_registro) VALUES (:id, :telefono, 'A')"
            cursor.execute(insert_new, {'id': turista_id, 'telefono': nuevo_telefono})
            self.connection.commit()
            return True
        except oracle.Error as e:
            print(f"Error al actualizar/insertar teléfono: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def logical_delete(self, table_name, pk_column, pk_value):
        """Realiza un eliminado lógico (estado_registro = 'I')."""
        if not self.connection: return False
        cursor = self.connection.cursor()
        
        query = f"""
            UPDATE {table_name}
            SET estado_registro = 'I'
            WHERE {pk_column} = :pk_val
        """
        try:
            cursor.execute(query, {'pk_val': pk_value})
            self.connection.commit()
            return True
        except oracle.Error as e:
            error, = e.args
            print(f"Error al realizar eliminado lógico en {table_name}: {error.message}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()