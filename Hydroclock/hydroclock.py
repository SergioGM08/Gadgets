import tkinter as tk
from tkinter import messagebox
from plyer import notification
import time
import threading
from datetime import datetime, time as dt_time

class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hydroclock")
        
        # Variables para controlar el estado de las notificaciones
        self.running = False
        self.reminder_thread = None
        
        # Configurar colores
        self.root.configure(bg='#87CEFA')  # Fondo azul claro

        # Barra superior
        self.root.wm_attributes('-topmost', 1)  # Asegura que la ventana esté encima de otras ventanas
        top_bar = tk.Frame(self.root, bg='#4682B4', height=30)  # Azul oscuro
        top_bar.pack(fill=tk.X)

        # Configuración de la barra superior
        top_bar_label = tk.Label(top_bar, text="HYDROCLOCK", bg='#4682B4', fg='white')
        top_bar_label.pack(pady=5)

        # Configuración del marco principal
        frame = tk.Frame(self.root, bg='#87CEFA')
        frame.pack(pady=20, padx=20, fill=tk.X)

        # Etiqueta y entrada para el intervalo de tiempo
        tk.Label(frame, text="Reminder interval (in minutes):", bg='#87CEFA', fg='white').grid(row=0, column=0, columnspan=2, pady=5, sticky='w')
        self.entry_interval = tk.Entry(frame)
        self.entry_interval.grid(row=0, column=2, padx=10)

        # Etiquetas y entradas para la hora de inicio
        tk.Label(frame, text="Start Time (HH:MM):", bg='#87CEFA', fg='white').grid(row=1, column=0, columnspan=2, pady=5, sticky='w')
        tk.Label(frame, text="Hour:", bg='#87CEFA', fg='white').grid(row=1, column=2, padx=5, sticky='w')
        self.entry_start_hour = tk.Entry(frame, width=5)
        self.entry_start_hour.grid(row=1, column=3, padx=5, sticky='w')

        tk.Label(frame, text="Minute:", bg='#87CEFA', fg='white').grid(row=1, column=4, padx=5, sticky='w')
        self.entry_start_minute = tk.Entry(frame, width=5)
        self.entry_start_minute.grid(row=1, column=5, padx=5, sticky='w')

        # Etiquetas y entradas para la hora de fin
        tk.Label(frame, text="End Time (HH:MM):", bg='#87CEFA', fg='white').grid(row=2, column=0, columnspan=2, pady=5, sticky='w')
        tk.Label(frame, text="Hour:", bg='#87CEFA', fg='white').grid(row=2, column=2, padx=5, sticky='w')
        self.entry_end_hour = tk.Entry(frame, width=5)
        self.entry_end_hour.grid(row=2, column=3, padx=5, sticky='w')

        tk.Label(frame, text="Minute:", bg='#87CEFA', fg='white').grid(row=2, column=4, padx=5, sticky='w')
        self.entry_end_minute = tk.Entry(frame, width=5)
        self.entry_end_minute.grid(row=2, column=5, padx=5, sticky='w')

        # Botón para comenzar
        start_button = tk.Button(frame, text="Start", command=self.start_app, bg='#4682B4', fg='white')
        start_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Botón para detener
        stop_button = tk.Button(frame, text="Stop", command=self.stop_app, bg='#B22222', fg='white')
        stop_button.grid(row=3, column=2, columnspan=2, pady=10)

    def show_reminder(self):
        notification.notify(
            title='HYDROCLOCK',
            message='It\'s time to drink water!',
            app_name='Hydroclock',
            timeout=10  # Duration of the notification in seconds
        )

    def is_within_time_range(self, start_time, end_time):
        now = datetime.now().time()
        return start_time <= now <= end_time

    def reminder_loop(self, interval, start_time, end_time):
        while self.running:
            time.sleep(interval)
            if self.is_within_time_range(start_time, end_time):
                self.show_reminder()

    def start_app(self):
        try:
            interval = int(self.entry_interval.get()) * 60  # Convert minutes to seconds
            
            # Get and convert start and end times
            start_hour = int(self.entry_start_hour.get())
            start_minute = int(self.entry_start_minute.get())
            end_hour = int(self.entry_end_hour.get())
            end_minute = int(self.entry_end_minute.get())

            start_time = dt_time(datetime.now().replace(hour=start_hour, minute=start_minute).hour,
                                datetime.now().replace(hour=start_hour, minute=start_minute).minute)
            end_time = dt_time(datetime.now().replace(hour=end_hour, minute=end_minute).hour,
                              datetime.now().replace(hour=end_hour, minute=end_minute).minute)

            if not self.running:
                self.running = True
                self.reminder_thread = threading.Thread(target=self.reminder_loop, args=(interval, start_time, end_time), daemon=True)
                self.reminder_thread.start()
                messagebox.showinfo("Reminder Set", "Reminder has been set successfully!")  # Añadido mensaje de confirmación
        except ValueError:
            messagebox.showerror("Error", "Please enter valid values.")

    def stop_app(self):
        if self.running:
            self.running = False
            if self.reminder_thread:
                self.reminder_thread.join()  # Espera a que el hilo termine
            self.reminder_thread = None  # Limpiar referencia al hilo
            messagebox.showinfo("Stopped", "Notifications have been disabled.")

# Run the application
root = tk.Tk()
app = ReminderApp(root)
root.mainloop()
