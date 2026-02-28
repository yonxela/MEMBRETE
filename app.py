import customtkinter as ctk
import sqlite3
from tkinter import messagebox

# Configuración de apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AppControlResidencial(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema VECINOS DELCO II - Login")
        self.geometry("400x450")
        
        # UI de Login
        self.label_titulo = ctk.CTkLabel(self, text="INICIO DE SESIÓN", font=("Roboto", 24))
        self.label_titulo.pack(pady=30)

        self.user_entry = ctk.CTkEntry(self, placeholder_text="Usuario (o DPI)")
        self.user_entry.pack(pady=10, padx=30, fill="x")

        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Contraseña", show="*")
        self.pass_entry.pack(pady=10, padx=30, fill="x")

        self.btn_login = ctk.CTkButton(self, text="Ingresar", command=self.validar_acceso)
        self.btn_login.pack(pady=20)

    def validar_acceso(self):
        usuario = self.user_entry.get()
        clave = self.pass_entry.get()

        # Conexión a la DB
        try:
            conn = sqlite3.connect('ControlResidencial.db')
            cursor = conn.cursor()
            
            # Consulta para verificar Rol y Vínculo
            cursor.execute("""
                SELECT u.id_rol, v.nombre, v.status, v.numero_lote 
                FROM Usuarios u 
                LEFT JOIN Vecinos v ON u.id_vecino_vinculado = v.id_vecino
                WHERE u.username = ? AND u.password_hash = ?
            """, (usuario, clave))
            
            resultado = cursor.fetchone()
            conn.close()

            if resultado:
                rol_id, nombre, status, lote = resultado
                if rol_id == 1: # DIRECTIVA
                    self.abrir_modulo_directiva()
                else: # VECINO
                    self.abrir_modulo_vecino(nombre, status, lote)
            else:
                messagebox.showerror("Error", "Usuario o clave incorrectos")
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudo conectar a la base de datos:\n{e}")

    def abrir_modulo_directiva(self):
        self.destroy()
        print("Abriendo Panel de Administración Total...")
        # Lógica para Módulo de Registro

    def abrir_modulo_vecino(self, nombre, status, lote):
        self.destroy()
        ventana_v = ctk.CTk()
        ventana_v.title(f"Estatus del Vecino - Lote {lote}")
        ventana_v.geometry("500x300")
        
        color_franja = "#27ae60" if status == 1 else "#c0392b"
        texto_pago = "PAGOS AL DÍA" if status == 1 else "NO HA PAGADO"

        ctk.CTkLabel(ventana_v, text=f"Bienvenido, {nombre}", font=("Roboto", 20)).pack(pady=20)
        
        franja = ctk.CTkLabel(ventana_v, text=texto_pago, fg_color=color_franja, 
                              text_color="white", font=("Roboto", 18, "bold"), height=50)
        franja.pack(side="bottom", fill="x")
        
        ventana_v.mainloop()

if __name__ == "__main__":
    app = AppControlResidencial()
    app.mainloop()
