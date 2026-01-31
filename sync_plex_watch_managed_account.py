import sys
import json
import os
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QTextEdit, QMessageBox, QGroupBox, QFormLayout)
from PySide6.QtCore import QThread, Signal, Slot, QObject
from plexapi.server import PlexServer

# --- Fichier de configuration ---
CONFIG_FILE = 'config.json'

# --- Worker Thread pour la synchro ---
class PlexSyncWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(self, plex_url, plex_token, user_source, user_target):
        super().__init__()
        self.plex_url = plex_url
        self.plex_token = plex_token
        self.user_source = user_source
        self.user_target = user_target
        self._is_running = True

    def run(self):
        self.log(f"--- Démarrage de la synchronisation ---")
        self.log(f"Serveur : {self.plex_url}")
        
        try:
            # Connexion Admin
            self.log("Connexion au serveur Plex (Admin)...")
            plex_admin = PlexServer(self.plex_url, self.plex_token)
            
            # Récupération du compte cible
            self.log(f"Récupération du compte de : {self.user_target}")
            account = plex_admin.myPlexAccount()
            user_obj = account.user(self.user_target)
            token_target = user_obj.get_token(plex_admin.machineIdentifier)
            plex_target = PlexServer(self.plex_url, token_target)
            
            self.log(f"--- Synchronisation de {self.user_source} vers {self.user_target} ---")

            # Parcours des bibliothèques
            for section in plex_admin.library.sections():
                if not self._is_running: break
                
                self.log(f"\nTraitement de la bibliothèque : {section.title} ({section.type})")
                
                items_to_sync = []
                if section.type == 'movie':
                    items_to_sync = section.all()
                elif section.type == 'show':
                    items_to_sync = section.search(libtype='episode')
                else:
                    self.log(f"  -> Type ignoré ({section.type})")
                    continue

                count = 0
                for item_source in items_to_sync:
                    if not self._is_running: break
                    
                    # On ne s'intéresse qu'aux items VUS ou EN COURS
                    if item_source.isPlayed or item_source.viewOffset > 0:
                        try:
                            # Recherche de l'équivalent chez le compte cible via ratingKey
                            item_target = plex_target.fetchItem(item_source.ratingKey)
                            
                            # 1. Synchroniser le statut VU
                            if item_source.isPlayed and not item_target.isPlayed:
                                item_target.markPlayed()
                                self.log(f"  [VU] {item_source.title}")
                                count += 1
                            
                            # 2. Synchroniser la position de lecture (En cours)
                            elif item_source.viewOffset > 0:
                                # On évite de toucher si c'est déjà à peu près synchro (à 10s près)
                                if abs(item_target.viewOffset - item_source.viewOffset) > 10000:
                                    item_target.updateProgress(item_source.viewOffset)
                                    progress_min = int(item_source.viewOffset/1000/60)
                                    self.log(f"  [EN COURS] {item_source.title} -> {progress_min} min")
                                    count += 1
                                    
                        except Exception as e:
                            # Item non trouvé ou autre erreur
                            continue
                
                if count == 0:
                     self.log("  -> Rien à synchroniser ici.")

            self.log("\n--- TERMINE ! ---")
            self.finished_signal.emit()

        except Exception as e:
            self.error_signal.emit(str(e))

    def log(self, message):
        self.log_signal.emit(message)

    def stop(self):
        self._is_running = False

# --- Interface Graphique ---
class PlexSyncApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plex Sync Manager")
        self.resize(600, 500)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Groupe Configuration
        config_group = QGroupBox("Configuration")
        form_layout = QFormLayout()

        self.url_input = QLineEdit()
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.source_input = QLineEdit()
        self.target_input = QLineEdit()

        form_layout.addRow("Plex URL (ex: http://IP:32400):", self.url_input)
        form_layout.addRow("Plex Token (Admin):", self.token_input)
        form_layout.addRow("Compte Source (Admin):", self.source_input)
        form_layout.addRow("Compte Cible (Managed):", self.target_input)
        
        config_group.setLayout(form_layout)
        main_layout.addWidget(config_group)

        # Boutons
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Lancer la Synchro")
        self.start_btn.clicked.connect(self.start_sync)
        self.save_btn = QPushButton("Sauvegarder Config")
        self.save_btn.clicked.connect(self.save_config)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.save_btn)
        main_layout.addLayout(btn_layout)

        # Logs
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        main_layout.addWidget(QLabel("Logs :"))
        main_layout.addWidget(self.log_area)

        # Chargement config
        self.load_config()
        self.worker = None

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.url_input.setText(config.get('plex_url', ''))
                    self.token_input.setText(config.get('plex_token', ''))
                    self.source_input.setText(config.get('user_source', ''))
                    self.target_input.setText(config.get('user_target', ''))
            except Exception as e:
                self.log(f"Erreur chargement config: {e}")

    def save_config(self):
        config = {
            'plex_url': self.url_input.text(),
            'plex_token': self.token_input.text(),
            'user_source': self.source_input.text(),
            'user_target': self.target_input.text()
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            QMessageBox.information(self, "Succès", "Configuration sauvegardée !")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de sauvegarder: {e}")

    def start_sync(self):
        if self.worker and self.worker.isRunning():
            return

        url = self.url_input.text()
        token = self.token_input.text()
        source = self.source_input.text()
        target = self.target_input.text()

        if not all([url, token, source, target]):
            QMessageBox.warning(self, "Attention", "Veuillez remplir tous les champs.")
            return

        self.log_area.clear()
        self.start_btn.setEnabled(False)
        self.start_btn.setText("Synchronisation en cours...")

        self.worker = PlexSyncWorker(url, token, source, target)
        self.worker.log_signal.connect(self.log)
        self.worker.error_signal.connect(self.handle_error)
        self.worker.finished_signal.connect(self.sync_finished)
        self.worker.start()

    def log(self, message):
        self.log_area.append(message)
        # Scroll to bottom
        sb = self.log_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    def handle_error(self, error_msg):
        self.log(f"ERREUR CRITIQUE : {error_msg}")
        QMessageBox.critical(self, "Erreur", f"Une erreur est survenue :\n{error_msg}")
        self.sync_finished()

    def sync_finished(self):
        self.start_btn.setEnabled(True)
        self.start_btn.setText("Lancer la Synchro")
        self.worker = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlexSyncApp()
    window.show()
    sys.exit(app.exec())