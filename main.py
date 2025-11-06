import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
# Asegúrate de que db_manager.py esté en el mismo directorio
from db_manager import DBManager 
from datetime import date, timedelta 

class TurismoApp:
    def __init__(self, master):
        self.master = master
        master.title("Sistema de Gestión de Turismo")
        self.db = DBManager()
        self.db.connect()

        self.user_id = None
        
        # Estilos
        master.option_add('*Font', 'Arial 10')
        master.option_add('*Button.padding', 5)

        self.setup_mode_selection()

    # --- Funciones de Utilidad ---
    
    def setup_mode_selection(self, message=None):
        self.clear_frame()
        if message:
             messagebox.showinfo("Mensaje", message)

        tk.Label(self.master, text="Seleccione el Modo de Operación", font=('Arial', 14, 'bold')).pack(pady=20)
        
        tk.Button(self.master, text="Modo Cliente", command=self.show_client_pre_login, width=30).pack(pady=10)
        tk.Button(self.master, text="Modo Administrador", command=self.show_admin_login, width=30).pack(pady=10)
        
        tk.Button(self.master, text="Cerrar Aplicación", command=self.close_app, width=30, bg='red', fg='white').pack(pady=20)

    def clear_frame(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def close_app(self):
        self.db.close()
        self.master.quit()

    # ======================================================================
    # === LÓGICA DE CLIENTE (REGISTRO, ACTUALIZACIÓN Y RESERVA) ==========
    # ======================================================================

    def show_client_pre_login(self):
        self.clear_frame()
        tk.Label(self.master, text="Modo Cliente: Identificación", font=('Arial', 12, 'bold')).pack(pady=20)
        
        tk.Button(self.master, text="1. Ya tengo mi ID (Ver/Actualizar)", command=self.show_client_login, width=40, height=2).pack(pady=10)
        tk.Button(self.master, text="2. ¡Quiero registrarme y reservar!", command=self.show_client_registration, width=40, height=2).pack(pady=10)
        
        tk.Button(self.master, text="<< Volver al Menú Principal", command=self.setup_mode_selection).pack(pady=20)

    def show_client_login(self):
        tk.messagebox.showinfo("Login Cliente", "A continuación, ingrese su ID de Turista o presione Cancelar para buscar por Nombre y Apellido.")
        turista_id = simpledialog.askinteger("Login Cliente", "Ingrese su ID de Turista:")
        if turista_id:
            columns, data = self.db.select_turista_by_id(turista_id)
            if data:
                self.user_id = turista_id
                self.show_client_view()
            else:
                messagebox.showerror("Error", "ID no válido o registro inactivo.")
        elif turista_id is None: 
            self._client_search_by_name_and_login()
        else:
            self.show_client_pre_login()

    def _client_search_by_name_and_login(self):
        class SearchByNameDialog(simpledialog.Dialog):
            def body(self, master):
                tk.Label(master, text="Ingrese Primer Nombre:").grid(row=0, sticky='w', padx=5, pady=5)
                tk.Label(master, text="Ingrese Primer Apellido:").grid(row=1, sticky='w', padx=5, pady=5)
                self.e1 = tk.Entry(master, width=30)
                self.e2 = tk.Entry(master, width=30)
                self.e1.grid(row=0, column=1, padx=5, pady=5)
                self.e2.grid(row=1, column=1, padx=5, pady=5)
                return self.e1
            def apply(self):
                self.result = (self.e1.get(), self.e2.get())

        dialog = SearchByNameDialog(self.master, title="Buscar ID por Nombre y Apellido")
        
        if hasattr(dialog, 'result') and dialog.result:
            nombre, apellido = dialog.result
            if nombre and apellido:
                columns, results = self.db.search_turista_by_name(nombre, apellido) 
                if not results:
                    messagebox.showerror("Búsqueda Fallida", "No se encontró ningún turista activo con ese nombre y apellido.")
                elif len(results) == 1:
                    turista_id = results[0][0]
                    messagebox.showinfo("ID Encontrado", f"Su ID de Turista es: {turista_id}\nIniciando sesión...")
                    self.user_id = turista_id
                    self.show_client_view()
                else:
                    messagebox.showwarning("Múltiples Resultados", "Se encontraron varios turistas con ese nombre. Intente ingresar su ID o contacte a un administrador.")
                    self.show_client_pre_login()
            else:
                messagebox.showwarning("Campos Vacíos", "Debe ingresar tanto el nombre como el apellido para buscar.")
                self.show_client_pre_login()
        else:
            messagebox.showwarning("Búsqueda Cancelada", "Búsqueda por nombre cancelada.")
            self.show_client_pre_login()


    def show_client_registration(self):
        """Muestra el FORMULARIO ÚNICO de registro de datos personales."""
        self.clear_frame()
        tk.Label(self.master, text="Paso 1: Datos Personales y Contacto", font=('Arial', 14, 'bold')).pack(pady=20)

        form_frame = tk.Frame(self.master, padx=10, pady=10, relief=tk.GROOVE, borderwidth=1)
        form_frame.pack(pady=10, padx=50)

        self.reg_entries = {}
        fields = {
            'n1': "Primer Nombre (*)", 'n2': "Segundo Nombre", 'n3': "Tercer Nombre",
            'a1': "Primer Apellido (*)", 'a2': "Segundo Apellido", 
            'dir': "Dirección (*)", 'correo': "Correo Electrónico (*)", 'tel': "Número de Teléfono (*)"
        }
        
        row_num = 0
        for key, label_text in fields.items():
            tk.Label(form_frame, text=label_text).grid(row=row_num, column=0, sticky='w', padx=5, pady=5)
            entry = tk.Entry(form_frame, width=40)
            entry.grid(row=row_num, column=1, padx=5, pady=5)
            self.reg_entries[key] = entry
            row_num += 1

        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Siguiente: Seleccionar Reservas", command=self._save_new_turista, bg='green', fg='white', width=30).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancelar y Volver", command=self.show_client_pre_login, width=15).pack(side=tk.LEFT, padx=10)

    def _save_new_turista(self):
        """Guarda los datos personales y avanza al paso de reservas."""
        data = {key: entry.get() for key, entry in self.reg_entries.items()}
        
        if not all([data['n1'], data['a1'], data['dir'], data['correo'], data['tel']]):
            messagebox.showerror("Error de Validación", "Debe ingresar los campos obligatorios (*).")
            return

        final_data = {k: v if v else None for k, v in data.items()}

        new_id = self.db.insert_turista(final_data) 

        if new_id and new_id > 0:
            self.db.insert_correo(new_id, final_data['correo']) 
            self.db.insert_telefono(new_id, final_data['tel'])
            
            self.user_id = new_id
            # ➡️ Pasa al paso de Reservas
            self.show_reservation_step(new_id)
        else:
            messagebox.showerror("Error", "La inserción de datos personales falló.")
    
    def show_reservation_step(self, turista_id):
        """Paso 2: Diálogo para seleccionar Sucursal, Hotel y Vuelo."""
        
        # 1. Obtener Catálogos (ID, Nombre/Descripción)
        sucursales = self.db.get_catalog_for_dropdown('Sucursal', 'ID_SUCURSAL', 'DIRECCION')
        hoteles = self.db.get_catalog_for_dropdown('Hotel', 'ID_HOTEL', 'NOMBRE')
        vuelos = self.db.get_catalog_for_dropdown('Vuelo', 'ID_VUELO', "ORIGEN || ' -> ' || DESTINO")
        
        # Simplificación: Obtenemos el ID de la primera Plaza Ocupada disponible para asignarla.
        try:
             # El [1] es porque select_all retorna (columns, data)
            plazas_ocupadas_data = self.db.select_all('Categoria_Plaza_Ocupada', active_only=True)[1] 
            plazas_ocupadas = [row[0] for row in plazas_ocupadas_data] if plazas_ocupadas_data else []
        except Exception as e:
            plazas_ocupadas = []
            print(f"Error al obtener plazas ocupadas: {e}")

        
        if not (sucursales and hoteles and vuelos and plazas_ocupadas):
            messagebox.showwarning("Catálogos Vacíos", "No hay suficientes datos de catálogos (Sucursal, Hotel, Vuelo, Plazas) para continuar la reserva. Registro completo, pero sin reservas.")
            self.show_client_view()
            return
            
        class ReservationDialog(simpledialog.Dialog):
            def body(self, master):
                self.entries = {}
                tk.Label(master, text=f"Paso 2: Seleccionar Reservas (ID: {turista_id})", font=('Arial', 10, 'bold')).grid(row=0, columnspan=2, pady=5)
                
                # --- Sucursal ---
                tk.Label(master, text="Sucursal de Viaje:").grid(row=1, column=0, sticky='w')
                sucursal_names = [f"{n[1]} ({n[0]})" for n in sucursales]
                self.sucursal_var = tk.StringVar(master)
                self.sucursal_combo = ttk.Combobox(master, textvariable=self.sucursal_var, values=sucursal_names, state="readonly", width=40)
                self.sucursal_combo.grid(row=1, column=1)
                self.entries['sucursal_id'] = sucursales # Guarda la lista para lookup
                
                # --- Hotel ---
                tk.Label(master, text="Hotel:").grid(row=2, column=0, sticky='w')
                hotel_names = [f"{n[1]} ({n[0]})" for n in hoteles]
                self.hotel_var = tk.StringVar(master)
                self.hotel_combo = ttk.Combobox(master, textvariable=self.hotel_var, values=hotel_names, state="readonly", width=40)
                self.hotel_combo.grid(row=2, column=1)
                self.entries['hotel_id'] = hoteles
                
                tk.Label(master, text="Régimen (Ej: Alojamiento):").grid(row=3, column=0, sticky='w')
                self.entries['regimen'] = tk.Entry(master, width=40); self.entries['regimen'].grid(row=3, column=1)
                self.entries['regimen'].insert(0, "Alojamiento")

                tk.Label(master, text="Fecha Llegada (YYYY-MM-DD):").grid(row=4, column=0, sticky='w')
                self.entries['llegada'] = tk.Entry(master, width=40); self.entries['llegada'].grid(row=4, column=1)
                self.entries['llegada'].insert(0, date.today().isoformat())
                
                tk.Label(master, text="Fecha Salida (YYYY-MM-DD):").grid(row=5, column=0, sticky='w')
                self.entries['salida'] = tk.Entry(master, width=40); self.entries['salida'].grid(row=5, column=1)
                self.entries['salida'].insert(0, (date.today() + timedelta(days=7)).isoformat())

                # --- Vuelo ---
                tk.Label(master, text="Vuelo:").grid(row=6, column=0, sticky='w')
                vuelo_names = [f"{n[1]} ({n[0]})" for n in vuelos]
                self.vuelo_var = tk.StringVar(master)
                self.vuelo_combo = ttk.Combobox(master, textvariable=self.vuelo_var, values=vuelo_names, state="readonly", width=40)
                self.vuelo_combo.grid(row=6, column=1)
                self.entries['vuelo_id'] = vuelos

                # Plaza Ocupada (Simplificación: Usar el primer CPO ID disponible)
                self.cpo_id = plazas_ocupadas[0] if plazas_ocupadas else None
                tk.Label(master, text=f"Plaza Asignada: ID {self.cpo_id} (Simplificado)").grid(row=7, column=0, columnspan=2)

                return self.sucursal_combo

            def apply(self):
                # Función auxiliar para extraer el ID de la cadena del Combobox
                def get_id(combo_var):
                    selected_name = combo_var.get()
                    if not selected_name: return None
                    # Extrae el número entre paréntesis
                    try:
                        import re
                        match = re.search(r'\((\d+)\)', selected_name)
                        return int(match.group(1)) if match else None
                    except:
                        return None
                
                self.result_data = {
                    'sucursal_id': get_id(self.sucursal_var),
                    'hotel_id': get_id(self.hotel_var),
                    'vuelo_id': get_id(self.vuelo_var),
                    'regimen': self.entries['regimen'].get(),
                    'llegada': self.entries['llegada'].get(),
                    'salida': self.entries['salida'].get(),
                    'cpo_id': self.cpo_id
                }

        dialog = ReservationDialog(self.master, title="Selección de Reservas")
        
        if hasattr(dialog, 'result_data') and dialog.result_data:
            data = dialog.result_data
            
            # 1. Insertar Sucursal
            if data['sucursal_id']:
                self.db.insert_turista_sucursal(turista_id, data['sucursal_id'])
            
            # 2. Insertar Hotel
            if all([data['hotel_id'], data['regimen'], data['llegada'], data['salida']]):
                self.db.insert_turista_hotel(turista_id, data['hotel_id'], data['regimen'], data['llegada'], data['salida'])

            # 3. Insertar Vuelo
            if all([data['vuelo_id'], data['cpo_id']]):
                self.db.insert_turista_vuelo(turista_id, data['vuelo_id'], data['cpo_id'])

            messagebox.showinfo("¡Registro Completo!", f"Su ID de Turista es: {turista_id}.\nReservas guardadas (Verifique Bitácora).")
            self.show_client_view()
        else:
            messagebox.showwarning("Reservas Canceladas", "Reservas omitidas. Puede gestionarlas más tarde en su vista.")
            self.show_client_view()

    def show_client_view(self):
        self.clear_frame()
        tk.Label(self.master, text=f"Vista Cliente - Mis Datos (ID: {self.user_id})", font=('Arial', 12, 'bold')).pack(pady=10)

        tk.Button(self.master, text="<< Cambiar Usuario o Registrarme", command=self.show_client_pre_login).pack(pady=5, padx=10, anchor='w')

        self.display_client_data()
        
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10, padx=10, fill='x')
        tk.Button(button_frame, text="Actualizar Mis Datos Personales", command=self.update_client_data_dialog).pack(side=tk.LEFT, fill='x', expand=True, padx=5)
        tk.Button(button_frame, text="Actualizar Mis Reservas (Hotel/Vuelo/Sucursal)", command=lambda: self.admin_manage_reservations(self.user_id), bg='lightblue').pack(side=tk.LEFT, fill='x', expand=True, padx=5)

    def display_client_data(self):
        """Recupera y muestra los datos personales y las reservas del cliente actual."""
        # 1. Datos Personales y Contacto
        columns, data = self.db.select_turista_by_id(self.user_id)
        
        data_frame = tk.LabelFrame(self.master, text="Datos Personales y Contacto", padx=10, pady=10)
        data_frame.pack(pady=10, padx=20, fill='x')
        
        if data:
            display_map = {
                'ID_TURISTA': 'ID', 'NOMBRE1': 'Primer Nombre', 'NOMBRE2': 'Segundo Nombre', 'NOMBRE3': 'Tercer Nombre',
                'APELLIDO1': 'Primer Apellido', 'APELLIDO2': 'Segundo Apellido',
                'DIRECCION': 'Dirección', 'CORREO': 'Correo (Activo)', 'TELEFONO': 'Teléfono (Activo)'
            }
            
            for i, col_name in enumerate(columns):
                label_text = display_map.get(col_name, col_name)
                tk.Label(data_frame, text=f"{label_text}:", anchor='w', justify=tk.LEFT).grid(row=i, column=0, padx=5, pady=2, sticky='w')
                tk.Label(data_frame, text=data[i] if data[i] else "N/A", anchor='w', justify=tk.LEFT, bg='lightyellow').grid(row=i, column=1, padx=5, pady=2, sticky='ew')
            data_frame.grid_columnconfigure(1, weight=1)

        # 2. Reservas Activas
        reservations = self.db.select_turista_reservations(self.user_id)
        res_frame = tk.LabelFrame(self.master, text="Mis Reservaciones Activas", padx=10, pady=10)
        res_frame.pack(pady=10, padx=20, fill='x')

        if not any(reservations.values()):
            tk.Label(res_frame, text="No tienes reservas activas (Hotel, Vuelo o Sucursal) en este momento.").pack()
        else:
            if reservations.get('sucursal'):
                s_data = reservations['sucursal']
                tk.Label(res_frame, text=f"Sucursal Asignada: {s_data[0]}, {s_data[1]}").pack(anchor='w')
            
            if reservations.get('hotel'):
                h_data = reservations['hotel']
                # Las fechas vienen como objetos date/datetime, usamos strftime
                llegada_str = h_data[2].strftime('%Y-%m-%d') if h_data[2] else 'N/A'
                salida_str = h_data[3].strftime('%Y-%m-%d') if h_data[3] else 'N/A'
                tk.Label(res_frame, text=f"Hotel: {h_data[0]} ({h_data[1]}). Llegada: {llegada_str} - Salida: {salida_str}").pack(anchor='w')
                
            if reservations.get('vuelo'):
                v_data = reservations['vuelo']
                fecha_str = v_data[1].strftime('%Y-%m-%d %H:%M') if v_data[1] else 'N/A'
                tk.Label(res_frame, text=f"Vuelo: {v_data[0]}. Fecha: {fecha_str}. Clase: {v_data[2]}").pack(anchor='w')


    def update_client_data_dialog(self):
        turista_id = self.user_id
        cols_client, data_client = self.db.select_turista_by_id(turista_id)
        current_data = dict(zip(cols_client, data_client)) if data_client else {}
        
        if not current_data:
            messagebox.showerror("Error", "No se pudo recuperar su registro para actualizar.")
            return

        class UpdateDialog(simpledialog.Dialog):
            def body(self, master):
                self.result_data = {}
                tk.Label(master, text="Actualizar Datos Personales:", font=('Arial', 10, 'bold')).grid(row=0, columnspan=2, pady=5)
                
                self.fields = ['nombre1', 'nombre2', 'nombre3', 'apellido1', 'apellido2', 'direccion', 'correo', 'telefono']
                self.entries = {}
                
                for i, field in enumerate(self.fields):
                    field_key = field.upper()
                    label_text = field.replace('1', ' (P) ').replace('2', ' (S) ').replace('3', ' (T) ').capitalize()
                    tk.Label(master, text=f"{label_text}:").grid(row=i+1, column=0, sticky='w', padx=5, pady=2)
                    
                    current_val = current_data.get(field_key) if current_data.get(field_key) else ""
                    
                    e = tk.Entry(master, width=40)
                    e.insert(0, current_val)
                    e.grid(row=i+1, column=1, padx=5, pady=2)
                    self.entries[field] = e
                
                return self.entries['nombre1']

            def apply(self):
                self.result_data = {field: entry.get() for field, entry in self.entries.items()}
                self.result_data['id'] = turista_id

        dialog = UpdateDialog(self.master, title="Actualizar Datos de Turista")
        
        if hasattr(dialog, 'result_data') and dialog.result_data:
            turista_update = {k: dialog.result_data[k] for k in ['nombre1', 'nombre2', 'nombre3', 'apellido1', 'apellido2', 'direccion']}
            correo = dialog.result_data['correo']
            telefono = dialog.result_data['telefono']
            
            success_turista = self.db.update_turista_data(turista_id, turista_update)
            success_correo = self.db.update_correo_or_insert(turista_id, correo)
            success_telefono = self.db.update_telefono_or_insert(turista_id, telefono)

            if success_turista or success_correo or success_telefono:
                messagebox.showinfo("Éxito", "¡Datos actualizados correctamente! (Verifique Bitácora)")
                self.show_client_view()
            else:
                messagebox.showerror("Error", "No se pudo actualizar los datos.")

    # ======================================================================
    # === LÓGICA DE ADMINISTRADOR (Gestión Completa) =======================
    # ======================================================================

    def show_admin_login(self):
        """Pide la contraseña de Admin con máscara."""
        password = simpledialog.askstring(
            "Login Administrador", 
            "Ingrese la contraseña de Admin (123)", 
            show='*' # <--- Máscara de contraseña
        )
        if password == '123':
            self.show_admin_view()
        else:
            messagebox.showerror("Login", "Contraseña incorrecta.")
            self.setup_mode_selection()

    def show_admin_view(self):
        """Interfaz para el administrador: Gestión completa."""
        self.clear_frame()
        tk.Label(self.master, text="Vista Administrador: Panel de Control", font=('Arial', 14, 'bold')).pack(pady=10)
        
        tk.Button(self.master, text="<< Volver a Selección de Modo", command=self.setup_mode_selection).pack(pady=5, padx=10, anchor='w')

        # --- Frame de Gestión de Turistas ---
        turista_frame = tk.LabelFrame(self.master, text="👥 Gestión de Turistas", padx=10, pady=10)
        turista_frame.pack(pady=10, padx=20, fill='x')
        
        # 🔹 Se eliminó el botón de insertar turista
        tk.Button(turista_frame, text="1. Actualizar Turista Existente", command=lambda: self.admin_manage_contacts_dialog(mode='update'), bg='orange').pack(side=tk.LEFT, padx=5, fill='x', expand=True)
        tk.Button(turista_frame, text="2. Desactivar Turista (Lógico)", command=self.admin_logical_delete_dialog, bg='red', fg='white').pack(side=tk.LEFT, padx=5, fill='x', expand=True)

        # --- Frame de Reservas y Auditoría ---
        consultas_frame = tk.LabelFrame(self.master, text="📊 Reservas y Auditoría", padx=10, pady=10)
        consultas_frame.pack(pady=10, padx=20, fill='x')

        tk.Button(consultas_frame, text="4. Gestionar Reservas (Hotel/Vuelo/Sucursal)", command=self.admin_manage_reservations, bg='lightblue').pack(side=tk.LEFT, padx=5, fill='x', expand=True)
        tk.Button(consultas_frame, text="5. Ver Bitácora de Cambios", command=self.show_admin_bitacora, bg='blue', fg='white').pack(side=tk.LEFT, padx=5, fill='x', expand=True)
        
        self.display_admin_turistas()

    def admin_manage_reservations(self, turista_id=None):
        """Permite al Admin/Cliente gestionar las reservas M:N de un Turista."""
        if not turista_id:
            turista_id = simpledialog.askinteger("Gestionar Reservas", "Ingrese el ID del Turista para gestionar sus reservas:")
        
        if turista_id:
            columns, data = self.db.select_turista_by_id(turista_id)
            if not data:
                messagebox.showerror("Error", f"Turista ID {turista_id} no encontrado o inactivo.")
                return
            
            # Reusa el diálogo de selección de reservas. Esto sobrescribirá cualquier reserva anterior.
            self.show_reservation_step(turista_id)
        else:
            return

    def admin_manage_contacts_dialog(self, mode):
        """Diálogo Único para Insertar/Actualizar Turistas (Admin), sin salto a reservas."""
        turista_id = None
        current_data = {}

        if mode == 'update':
            turista_id = simpledialog.askinteger("Actualizar Turista", "Ingrese el ID del Turista a actualizar:")
            if not turista_id: return 
            
            cols_client, data_client = self.db.select_turista_by_id(turista_id)
            current_data = dict(zip(cols_client, data_client)) if data_client else {}
            
            if not current_data:
                messagebox.showerror("Error", f"No se encontró Turista activo con ID {turista_id}.")
                return

        class ManageTuristaDialog(simpledialog.Dialog):
            def __init__(self, master, title=None, initial_data=None):
                self.initial_data = initial_data if initial_data else {}
                super().__init__(master, title=title)

            def body(self, master):
                self.result_data = {}
                tk.Label(master, text="Datos del Turista:", font=('Arial', 10, 'bold')).grid(row=0, columnspan=2, pady=5)
                self.fields = [
                    ('nombre1', "Primer Nombre (*)"), ('nombre2', "Segundo Nombre"), ('nombre3', "Tercer Nombre"),
                    ('apellido1', "Primer Apellido (*)"), ('apellido2', "Segundo Apellido"), 
                    ('direccion', "Dirección (*)"), ('correo', "Correo Electrónico (*)"), ('telefono', "Número de Teléfono (*)")
                ]
                self.entries = {}
                
                for i, (field, label_text) in enumerate(self.fields):
                    tk.Label(master, text=f"{label_text}:").grid(row=i+1, column=0, sticky='w', padx=5, pady=2)
                    field_key = field.upper()
                    current_val = self.initial_data.get(field_key) if self.initial_data.get(field_key) else ""
                    e = tk.Entry(master, width=40)
                    e.insert(0, current_val)
                    e.grid(row=i+1, column=1, padx=5, pady=2)
                    self.entries[field] = e
                return self.entries['nombre1']

            def apply(self):
                self.result_data = {field: entry.get() for field, entry in self.entries.items()}

        if mode == 'insert':
            dialog_title = "Insertar Nuevo Turista (Admin)"
        else:
            dialog_title = f"Actualizar Turista ID {turista_id} (Admin)"

        dialog = ManageTuristaDialog(self.master, title=dialog_title, initial_data=current_data)
        
        if hasattr(dialog, 'result_data') and dialog.result_data:
            data = dialog.result_data
            
            if not all([data['nombre1'], data['apellido1'], data['direccion'], data['correo'], data['telefono']]):
                messagebox.showerror("Error de Validación", "Faltan campos obligatorios (*).")
                return
            
            turista_data = {k: v if v else None for k, v in data.items() if k not in ['correo', 'telefono']}
            correo = data['correo']
            telefono = data['telefono']

            if mode == 'insert':
                new_id = self.db.insert_turista(turista_data)
                if new_id and new_id > 0:
                    self.db.insert_correo(new_id, correo)
                    self.db.insert_telefono(new_id, telefono)
                    messagebox.showinfo("Éxito", f"Turista ingresado correctamente con ID: {new_id}")
                else:
                    messagebox.showerror("Error", "La inserción falló.")
            
            elif mode == 'update':
                success_turista = self.db.update_turista_data(turista_id, turista_data)
                success_correo = self.db.update_correo_or_insert(turista_id, correo)
                success_telefono = self.db.update_telefono_or_insert(turista_id, telefono)
                
                if success_turista or success_correo or success_telefono:
                    messagebox.showinfo("Éxito", f"Turista ID {turista_id} actualizado.")
                else:
                    messagebox.showerror("Error", "Error al actualizar Turista.")

            self.show_admin_view()
            
    def display_admin_turistas(self):
        try:
            self.list_frame.destroy()
        except AttributeError:
            pass
            
        self.list_frame = tk.LabelFrame(self.master, text="Turistas Activos Registrados", padx=10, pady=10)
        self.list_frame.pack(pady=10, padx=20, fill='x')
        
        columns, data = self.db.select_all("Turista", active_only=True)
        
        tree = ttk.Treeview(self.list_frame, columns=('ID', 'Nombre', 'Apellido', 'Dirección'), show='headings', height=5)
        tree.heading('ID', text='ID')
        tree.heading('Nombre', text='Nombre')
        tree.heading('Apellido', text='Apellido')
        tree.heading('Dirección', text='Dirección')
        
        tree.column('ID', width=50, anchor='center')
        tree.column('Nombre', width=150)
        tree.column('Apellido', width=150)
        tree.column('Dirección', width=200)

        if data:
            for row_data in data:
                id_turista_index = 0
                nombre1_index = 1
                apellido1_index = 4
                direccion_index = 6
                
                tree.insert('', tk.END, values=(
                    row_data[id_turista_index],
                    row_data[nombre1_index],
                    row_data[apellido1_index],
                    row_data[direccion_index]
                ))

        tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

    def admin_logical_delete_dialog(self):
        turista_id = simpledialog.askinteger("Eliminado Lógico", "ID del Turista a desactivar:")
        if turista_id and messagebox.askyesno("Confirmar", f"¿Está seguro de INACTIVAR al Turista ID {turista_id}?"):
            if self.db.logical_delete("Turista", "id_turista", turista_id):
                messagebox.showinfo("Éxito", f"Turista ID {turista_id} deshabilitado (eliminado lógico). (Verifique Bitácora)")
                self.show_admin_view()
            else:
                messagebox.showerror("Error", "Error al realizar el eliminado lógico.")

    def show_admin_bitacora(self):
        columns, data = self.db.select_bitacora_full()
        
        if not data:
            messagebox.showinfo("Bitácora", "No hay registros de auditoría para mostrar.")
            return

        top = tk.Toplevel(self.master)
        top.title("Bitácora de Auditoría")
        top.geometry("900x500")

        frame = tk.Frame(top)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        headers = ['ID', 'Fecha', 'Tabla', 'Acción', 'Campo Modif.', 'Valor Anterior', 'Valor Actual', 'Flag ID']

        tree = ttk.Treeview(frame, columns=headers, show='headings')
        
        widths = [50, 150, 100, 80, 100, 150, 150, 60]
        for i, col_name in enumerate(headers):
            tree.heading(col_name, text=col_name)
            tree.column(col_name, width=widths[i], anchor='center' if i < 4 or i > 6 else 'w')

        for row in data:
            formatted_row = list(row)
            formatted_row[1] = str(formatted_row[1]) if formatted_row[1] else ''
            
            tree.insert('', tk.END, values=formatted_row)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = TurismoApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close_app)
    root.mainloop()
