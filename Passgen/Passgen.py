import random
import string
import csv
import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from zxcvbn import zxcvbn  # Importamos zxcvbn para evaluar la fortaleza de las contraseñas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox, QLineEdit, QPushButton, QLabel, QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout

# Función para derivar la clave usando una clave maestra y un salt
def derive_key(master_password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key

# Función para cifrar la contraseña
def encrypt_password(password, key):
    f = Fernet(key)
    encrypted_password = f.encrypt(password.encode())
    return encrypted_password.decode()

# Función para descifrar la contraseña
def decrypt_password(encrypted_password, key):
    f = Fernet(key)
    decrypted_password = f.decrypt(encrypted_password.encode())
    return decrypted_password.decode()

# Generar un salt aleatorio
def generate_salt():
    return os.urandom(16)

# Función para generar la contraseña
def generate_password(length, use_uppercase, use_numbers, use_symbols):
    characters = string.ascii_lowercase
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_numbers:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

# Función para evaluar la fortaleza de la contraseña usando zxcvbn
def evaluate_password_strength(password):
    result = zxcvbn(password)
    score = result['score']
    feedback = result['feedback']['suggestions']

    if score == 4:
        return "Very Strong", "green", feedback
    elif score == 3:
        return "Strong", "lime", feedback
    elif score == 2:
        return "Moderate", "orange", feedback
    elif score == 1:
        return "Weak", "red", feedback
    else:
        return "Very Weak", "darkred", feedback

# Función para guardar la contraseña en un archivo CSV
def save_password_csv(filename, site, encrypted_password, salt):
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=',')
        if not file_exists or os.stat(filename).st_size == 0:
            writer.writerow(["SITE", "PASSWORD", "SALT"])
        writer.writerow([site, encrypted_password, salt.hex()])

# Función para recuperar la contraseña
def retrieve_password(site, master_password):
    if not os.path.exists("passwords.csv"):
        return None, None

    with open("passwords.csv", 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0] == site:
                encrypted_password = row[1]
                salt = bytes.fromhex(row[2])
                key = derive_key(master_password, salt)
                try:
                    decrypted_password = decrypt_password(encrypted_password, key)
                    return decrypted_password, encrypted_password
                except Exception:
                    return None, None
        return None, None

# Clase para la ventana emergente (Para mostrar la contraseña recuperada)
class PasswordRetrievePopup(QDialog):
    def __init__(self, parent, site, decrypted_password):
        super().__init__(parent)
        self.setWindowTitle(f"Password for {site}")
        self.setGeometry(300, 200, 400, 250)

        layout = QVBoxLayout()

        self.label = QLabel(f"Password for {site}:", self)
        self.label.setStyleSheet('color: lime; font-size: 18px;')
        layout.addWidget(self.label)

        self.password_label = QLabel(decrypted_password, self)
        self.password_label.setStyleSheet('color: lime; font-size: 14px; padding: 10px; background: black;')
        layout.addWidget(self.password_label)

        self.button_copy = QPushButton("Copy Retrieved Password", self)
        self.button_copy.clicked.connect(self.copy_password)
        layout.addWidget(self.button_copy)

        self.button_close = QPushButton("Close", self)
        self.button_close.clicked.connect(self.close)
        layout.addWidget(self.button_close)

        self.setLayout(layout)

    def copy_password(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.password_label.text())
        QMessageBox.information(self, "Copied", "Password copied to clipboard!")

# Ventana de Entrada de Contraseña Maestra
class MasterPasswordDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Master Password")
        self.setGeometry(400, 200, 350, 100)
        
        self.setStyleSheet("""
            background-color: black;
            color: lime;
            font-size: 14px;
        """)

        self.layout = QFormLayout()

        self.master_password_label = QLabel("Enter Master Password:", self)
        self.layout.addWidget(self.master_password_label)

        self.master_password_input = QLineEdit(self)
        self.master_password_input.setEchoMode(QLineEdit.Password)  # Ocultar texto
        self.layout.addWidget(self.master_password_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def get_master_password(self):
        return self.master_password_input.text()

# Ventana principal de la aplicación
class PasswordGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Password Generator")
        self.setGeometry(300, 100, 600, 150)
        self.setStyleSheet("""
            background-color: black;
            color: lime;
            font-size: 14px;
        """)

        self.layout = QVBoxLayout()

        # La variable 'master_password' almacena la contraseña maestra
        self.master_password = None

        # Pedir la contraseña maestra antes de permitir cualquier interacción
        self.master_password_dialog = MasterPasswordDialog(self)
        if self.master_password_dialog.exec_() == QDialog.Accepted:
            self.master_password = self.master_password_dialog.get_master_password()

            if not self.master_password:
                QMessageBox.critical(self, "Error", "Master password is required!")
                self.close()

        else:
            self.close()

        # Layout y los widgets para la generación y almacenamiento de contraseñas
        self.label_length = QLabel("Password Length (At least 6 recommended):", self)
        self.layout.addWidget(self.label_length)

        self.entry_length = QLineEdit(self)
        self.layout.addWidget(self.entry_length)

        self.check_uppercase = QCheckBox("Include Uppercase Letters", self)
        self.layout.addWidget(self.check_uppercase)

        self.check_numbers = QCheckBox("Include Numbers", self)
        self.layout.addWidget(self.check_numbers)

        self.check_symbols = QCheckBox("Include Symbols", self)
        self.layout.addWidget(self.check_symbols)

        self.label_usage = QLabel("Site Description:", self)
        self.layout.addWidget(self.label_usage)

        self.entry_usage = QLineEdit(self)
        self.layout.addWidget(self.entry_usage)

        # Crear un layout horizontal para los botones
        self.button_layout = QHBoxLayout()
        self.button_generate = QPushButton("Generate Password", self)
        self.button_generate.clicked.connect(self.gen_n_ev_password)
        self.button_generate.setStyleSheet("background-color: lime; color: black;")
        self.button_layout.addWidget(self.button_generate)

        self.button_save = QPushButton("Save Password", self)
        self.button_save.clicked.connect(self.save_password)
        self.button_save.setStyleSheet("background-color: lime; color: black;")
        self.button_layout.addWidget(self.button_save)

        self.button_retrieve = QPushButton("Retrieve Password", self)
        self.button_retrieve.clicked.connect(self.retrieve_password)
        self.button_retrieve.setStyleSheet("background-color: lime; color: black;")
        self.button_layout.addWidget(self.button_retrieve)

        # Añadir los botones horizontales al layout principal
        self.layout.addLayout(self.button_layout)

        self.label_generated_password = QLabel("", self)
        self.layout.addWidget(self.label_generated_password)

        self.label_password_strength = QLabel("", self)
        self.layout.addWidget(self.label_password_strength)

        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)


    def gen_n_ev_password(self):
        try:
            length = int(self.entry_length.text())
            if length < 6:
                raise ValueError("Password length should be at least 6 characters.")
            
            use_uppercase = self.check_uppercase.isChecked()
            use_numbers = self.check_numbers.isChecked()
            use_symbols = self.check_symbols.isChecked()

            password = generate_password(length, use_uppercase, use_numbers, use_symbols)
            self.label_generated_password.setText(password)

            strength, color, suggestions = evaluate_password_strength(password)
            self.label_password_strength.setText(f"Strength: {strength}")
            self.label_password_strength.setStyleSheet(f'color: {color};')

            if suggestions:
                suggestion_text = "\n".join(suggestions)
                QMessageBox.information(self, "Suggestions", suggestion_text)
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", str(ve))

    def save_password(self):
        site = self.entry_usage.text()
        password = self.label_generated_password.text()

        if not site or not password:
            QMessageBox.warning(self, "Input Error", "Please provide a site description and generate a password.")
            return

        salt = generate_salt()
        key = derive_key(self.master_password, salt)
        encrypted_password = encrypt_password(password, key)

        save_password_csv("passwords.csv", site, encrypted_password, salt)
        QMessageBox.information(self, "Success", "Password saved successfully!")

    def retrieve_password(self):
        site = self.entry_usage.text()

        if not site:
            QMessageBox.warning(self, "Input Error", "Please provide a site description.")
            return

        decrypted_password, encrypted_password = retrieve_password(site, self.master_password)

        if decrypted_password:
            self.popup = PasswordRetrievePopup(self, site, decrypted_password)
            self.popup.exec_()
        else:
            QMessageBox.warning(self, "Error", "No password found for the specified site or invalid master password.")

# Función principal
if __name__ == '__main__':
    app = QApplication([])
    window = PasswordGeneratorApp()
    window.show()
    app.exec_()
