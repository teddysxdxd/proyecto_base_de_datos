# main.py
import tkinter as tk
from tkinter import messagebox, simpledialog
from db_manager import DBManager

class TurismoApp:
    def __init__(self, master):
        self.master = master
        master.title("Sistema de Gestión de Turismo")
        self.db = DBManager()
        self.db.connect()

        self.user_id = None # Para simular el login del cliente
        
        # Estilos
        master.option_add('*Font', 'Arial 10')
        master.option_add('*Button.padding', 5)

        # Pantalla de Selección de Modo
        self.setup_mode_selection()

    def setup_mode_selection(self):
        """Pantalla inicial para seleccionar modo Cliente o Administrador."""
        self.clear_frame()
        tk.Label(self.master, text="Seleccione el Modo de Operación", font=('Arial', 14, 'bold')).pack(pady=20)
        
        tk.Button(self.master, text="Modo Cliente (Ver/Editar Datos Propios)", command=self.show_client_login, width=30).pack(pady=10)
        tk.Button(self.master, text="Modo Administrador (CRUD Completo)", command=self.show_admin_login, width=30).pack(pady=10)
        
        tk.Button(self.master, text="Cerrar Aplicación", command=self.close_app, width=30, bg='red', fg='white').pack(pady=20)

    def clear_frame(self):
        """Limpia todos los widgets del frame principal."""
        for widget in self.master.winfo_children():
            widget.destroy()

    def close_app(self):
        """Cierra la conexión y la aplicación."""
        self.db.close()
        self.master.quit()

    # --- Lógica de Login ---

    def show_client_login(self):
        """Solicita ID del Turista para simular el login del cliente."""
        self.user_id = simpledialog.askinteger("Login Cliente", "Ingrese su ID de Turista:")
        if self.user_id:
            self.show_client_view()
        else:
            messagebox.showwarning("Login", "ID de Turista no ingresado.")

    def show_admin_login(self):
        """Simula un login de administrador (sin verificación real)."""
        # Se podría implementar un check de usuario/contraseña real aquí
        password = simpledialog.askstring("Login Administrador", "Ingrese la contraseña de Admin (123)", show='*')
        if password == '123':
            self.show_admin_view()
        else:
            messagebox.showerror("Login", "Contraseña incorrecta.")
            self.setup_mode_selection()

    # --- Vistas ---

    def show_client_view(self):
        """Interfaz para el cliente: Ver y actualizar sus propios datos."""
        self.clear_frame()
        tk.Label(self.master, text=f"Vista Cliente - Turista ID: {self.user_id}", font=('Arial', 12, 'bold')).pack(pady=10)

        # Botón para volver
        tk.Button(self.master, text="<< Volver a Selección de Modo", command=self.setup_mode_selection).pack(pady=5, padx=10, anchor='w')

        # 1. Mostrar datos guardados
        self.display_client_data()
        
        # 2. Funcionalidad de Actualización
        tk.Button(self.master, text="Actualizar Mis Datos", command=self.update_client_data_dialog).pack(pady=10)

    def display_client_data(self):
        """Recupera y muestra los datos del cliente actual."""
        columns, data = self.db.select_turista_by_id(self.user_id)
        
        data_frame = tk.Frame(self.master)
        data_frame.pack(pady=10, padx=20)
        
        if data:
            tk.Label(data_frame, text="**Datos Personales Guardados**", font=('Arial', 10, 'bold')).grid(row=0, columnspan=2, pady=5)
            
            # Mapeo de columnas y datos para mostrar
            display_map = {
                'NOMBRE1': 'Primer Nombre', 'APELLIDO1': 'Primer Apellido', 
                'DIRECCION': 'Dirección', 'CORREO': 'Correo', 'TELEFONO': 'Teléfono'
            }
            
            for i, col_name in enumerate(columns):
                label_text = display_map.get(col_name, col_name)
                tk.Label(data_frame, text=f"{label_text}:", anchor='w', justify=tk.LEFT).grid(row=i+1, column=0, padx=5, pady=2, sticky='w')
                tk.Label(data_frame, text=data[i] if data[i] else "N/A", anchor='w', justify=tk.LEFT).grid(row=i+1, column=1, padx=5, pady=2, sticky='w')
        else:
            tk.Label(data_frame, text="No se encontraron datos de Turista Activo con ese ID.").grid(row=0, column=0)


    def update_client_data_dialog(self):
        """Abre un diálogo para que el cliente actualice su dirección."""
        new_address = simpledialog.askstring("Actualizar Dirección", "Ingrese su nueva dirección:")
        
        if new_address:
            # Recuperar datos actuales para no sobreescribir nulos
            # Nota: Esta es una simplificación. En una app real, se cargaría el objeto completo.
            
            # Asumimos que la operación de actualizar solo la dirección es suficiente para la demo.
            data_to_update = {'direccion': new_address}
            
            # Buscar el registro para obtener todos los campos requeridos por el UPDATE
            columns, current_data = self.db.select_all("Turista", active_only=False)
            current_turista = next((dict(zip(columns, row)) for row in current_data if row[0] == self.user_id), None)

            if current_turista:
                update_data = {
                    'nombre1': current_turista[1], 'nombre2': current_turista[2], 
                    'apellido1': current_turista[4], 'apellido2': current_turista[5], 
                    'direccion': new_address
                }
                
                if self.db.update_turista_data(self.user_id, update_data):
                    messagebox.showinfo("Éxito", "¡Dirección actualizada correctamente! (Verifique Bitácora)")
                    self.show_client_view() # Refresca la vista
                else:
                    messagebox.showerror("Error", "No se pudo actualizar la dirección.")

    
    # --- Vista Administrador ---

    def show_admin_view(self):
        """Interfaz para el administrador: CRUD completo sobre Turista."""
        self.clear_frame()
        tk.Label(self.master, text="Vista Administrador: Gestión de Turistas", font=('Arial', 12, 'bold')).pack(pady=10)
        
        tk.Button(self.master, text="<< Volver a Selección de Modo", command=self.setup_mode_selection).pack(pady=5, padx=10, anchor='w')

        # Botones de Acciones CRUD
        actions_frame = tk.Frame(self.master)
        actions_frame.pack(pady=10)
        tk.Button(actions_frame, text="Insertar Nuevo Turista", command=self.admin_insert_turista_dialog, bg='green', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(actions_frame, text="Actualizar Turista Existente", command=self.admin_update_turista_dialog, bg='orange').pack(side=tk.LEFT, padx=5)
        tk.Button(actions_frame, text="Eliminado Lógico", command=self.admin_logical_delete_dialog, bg='red', fg='white').pack(side=tk.LEFT, padx=5)

        # Listado de Turistas Activos
        self.display_admin_turistas()
        
    def display_admin_turistas(self):
        """Muestra una lista de todos los turistas activos."""
        columns, data = self.db.select_all("Turista", active_only=True)
        
        list_frame = tk.Frame(self.master)
        list_frame.pack(pady=10, padx=20)
        
        tk.Label(list_frame, text="**Turistas Activos**", font=('Arial', 10, 'bold')).grid(row=0, columnspan=3, pady=5)
        
        # Encabezados de la lista
        headers = ['ID', 'Nombre Completo', 'Dirección']
        for col, header in enumerate(headers):
             tk.Label(list_frame, text=header, font=('Arial', 10, 'underline')).grid(row=1, column=col, padx=10)

        if data:
            for row_num, row_data in enumerate(data):
                # ID
                tk.Label(list_frame, text=row_data[0]).grid(row=row_num+2, column=0, padx=10)
                # Nombre Completo
                nombre_completo = f"{row_data[1]} {row_data[4]}"
                tk.Label(list_frame, text=nombre_completo).grid(row=row_num+2, column=1, padx=10)
                # Dirección
                tk.Label(list_frame, text=row_data[6]).grid(row=row_num+2, column=2, padx=10)
        else:
            tk.Label(list_frame, text="No hay turistas activos para mostrar.").grid(row=2, columnspan=3)
            
    # --- Métodos de CRUD de Administrador ---

    def admin_insert_turista_dialog(self):
        """Diálogo para insertar un nuevo Turista."""
        data = {
            'n1': simpledialog.askstring("Insertar", "Primer Nombre:"),
            'n2': simpledialog.askstring("Insertar", "Segundo Nombre (opcional):"),
            'a1': simpledialog.askstring("Insertar", "Primer Apellido:"),
            'a2': simpledialog.askstring("Insertar", "Segundo Apellido (opcional):"),
            'dir': simpledialog.askstring("Insertar", "Dirección:")
        }
        
        if data['n1'] and data['a1'] and self.db.insert_turista(data):
            messagebox.showinfo("Éxito", "Turista ingresado correctamente.")
            self.show_admin_view()
        else:
            messagebox.showerror("Error", "La inserción falló o faltan campos obligatorios.")

    def admin_update_turista_dialog(self):
        """Diálogo para actualizar la dirección de un Turista."""
        turista_id = simpledialog.askinteger("Actualizar", "ID del Turista a actualizar:")
        if turista_id:
            new_address = simpledialog.askstring("Actualizar", f"Nueva Dirección para ID {turista_id}:")
            
            # Lógica similar a la de Cliente: obtener datos actuales para el UPDATE
            columns, current_data = self.db.select_all("Turista", active_only=False)
            current_turista = next((dict(zip(columns, row)) for row in current_data if row[0] == turista_id), None)
            
            if current_turista and new_address:
                 update_data = {
                    'nombre1': current_turista[1], 'nombre2': current_turista[2], 
                    'apellido1': current_turista[4], 'apellido2': current_turista[5], 
                    'direccion': new_address
                }
                 if self.db.update_turista_data(turista_id, update_data):
                    messagebox.showinfo("Éxito", f"Turista ID {turista_id} actualizado.")
                    self.show_admin_view()
                 else:
                     messagebox.showerror("Error", "Error al actualizar Turista.")
            else:
                messagebox.showerror("Error", "Turista no encontrado o dirección no ingresada.")


    def admin_logical_delete_dialog(self):
        """Diálogo para realizar un eliminado lógico."""
        turista_id = simpledialog.askinteger("Eliminado Lógico", "ID del Turista a desactivar:")
        if turista_id and messagebox.askyesno("Confirmar", f"¿Está seguro de INACTIVAR al Turista ID {turista_id}?"):
            if self.db.logical_delete("Turista", "id_turista", turista_id):
                messagebox.showinfo("Éxito", f"Turista ID {turista_id} deshabilitado (eliminado lógico).")
                self.show_admin_view()
            else:
                messagebox.showerror("Error", "Error al realizar el eliminado lógico.")


if __name__ == "__main__":
    root = tk.Tk()
    app = TurismoApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close_app) # Asegura cerrar la conexión al cerrar la ventana
    root.mainloop()