import sys
import os
import threading
import random
import time
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel)
from PySide6.QtGui import QFont, QTextCursor, QColor
from PySide6.QtCore import Qt, Signal, QObject

# ==========================================
# ส่วนจัดการ GUI Bridge (Signal & Slot)
# ==========================================
class GameSignals(QObject):
    print_signal = Signal(str, str)
    clear_signal = Signal()
    input_request = Signal(str)

signals = GameSignals()

# ตัวแปร Global เพื่ออ้างอิง App
app_instance = None

# ฟังก์ชัน Helper สำหรับ Game Logic เรียกใช้
def log(text, color="#ecf0f1"):
    """พิมพ์ข้อความลง GUI"""
    signals.print_signal.emit(str(text), color)

def ask(prompt=""):
    """ขอ Input จาก GUI"""
    if prompt:
        log(f"\n{prompt}", "#3498db") # สีฟ้าสำหรับ Prompt
    if app_instance:
        return app_instance.wait_for_input()
    return ""

def clear_screen():
    """ล้างหน้าจอ GUI"""
    signals.clear_signal.emit()

# ==========================================
# Game Logic & Data
# ==========================================
class Colors:
    # เก็บเป็น Hex Code แทน ANSI Code เดิม
    RED = "#e74c3c"
    GREEN = "#2ecc71"
    YELLOW = "#f1c40f"
    BLUE = "#3498db"
    PURPLE = "#9b59b6"
    CYAN = "#1abc9c"
    WHITE = "#ecf0f1"
    GRAY = "#95a5a6"

def roll_dice(sides, modifier=0):
    return random.randint(1, sides) + modifier

def load_data():
    monsters = {
        "goblin": {
            "name": "ก็อบลิน", "hp": 15, "min_dmg": 1, "max_dmg": 6,
            "description": "มอนสเตอร์ตัวเล็กตาแดง"
        },
        "orc": {
            "name": "ออร์ค", "hp": 25, "min_dmg": 2, "max_dmg": 8,
            "description": "ยักษ์เขียวคล้ำหน้าตาโหดร้าย"
        },
        "succubus": {
            "name": "ซักคิวบัส", "hp": 30, "min_dmg": 2, "max_dmg": 12,
            "description": "ปีศาจสาวพราวเสน่ห์ แต่แววตาอำมหิต"
        }
    }
    return monsters

class Character:
    def __init__(self, name, race, char_class):
        self.name = name
        self.race = race
        self.char_class = char_class
        self.max_hp = 20
        self.hp = 20
        self.base_damage = 5
        self.armor = 0
        self.gold = 50
        self.exp = 0
        self.level = 1
        self.inventory = []
        self.status_effects = []
        
        # ปรับ Stat ตามเผ่า/อาชีพ (ย่อเพื่อความกระชับ)
        if race == "orc":
            self.max_hp += 10
            self.base_damage += 2
        elif char_class == "warrior":
            self.max_hp += 5
            self.base_damage += 2

        self.hp = self.max_hp

    # --- ฟังก์ชันที่คุณต้องการ ---
    def show_stats(self):
        log("═" * 30, "#555")
        log(f"👤 ชื่อ: {self.name} | Lv: {self.level}", "#f1c40f")
        log(f"❤️ HP: {self.hp}/{self.max_hp} | 💰 Gold: {self.gold}", "#e74c3c")
        log("═" * 30, "#555")
    # -------------------------

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.armor)
        self.hp -= actual_damage
        log(f"โดนโจมตี {actual_damage} หน่วย!", Colors.RED)
        return self.hp > 0

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
        log(f"ฟื้นฟู {amount} HP", Colors.GREEN)

# ==========================================
# Game Flow (Refactored for GUI)
# ==========================================
def combat_turn(player, monster):
    log("------------------------------", Colors.GRAY)
    log(f"⚔️ {monster['name']} (HP: {monster['hp']})", Colors.RED)
    
    log("1.โจมตี 2.ใช้ไอเทม 3.หนี")
    choice = ask("เลือกการกระทำ (1-3):")

    if choice == "1":
        # Player Turn
        dmg = roll_dice(player.base_damage)
        monster['hp'] -= dmg
        log(f"คุณโจมตี {monster['name']} {dmg} หน่วย!", Colors.GREEN)
        
        if monster['hp'] <= 0:
            return True # ชนะ
            
        # Enemy Turn
        enemy_dmg = roll_dice(monster['max_dmg'])
        log(f"{monster['name']} สวนกลับ!", Colors.RED)
        player.take_damage(enemy_dmg)
        
    elif choice == "2":
        log("ยังไม่มีไอเทม (ฟีเจอร์นี้กำลังพัฒนา)", Colors.GRAY)
    elif choice == "3":
        if roll_dice(20) > 10:
            log("หนีสำเร็จ!", Colors.GREEN)
            return "flee"
        else:
            log("หนีไม่พ้น!", Colors.RED)
            player.take_damage(roll_dice(5))
            
    return False # ยังไม่จบ

def run_rpg_game():
    """ฟังก์ชันหลักของเกมที่จะรันใน Thread"""
    time.sleep(0.5) # รอ UI โหลดเสร็จนิดนึง
    log("=== ยินดีต้อนรับสู่ RPG TERMINAL ===", Colors.YELLOW)
    
    name = ask("กรุณาระบุชื่อผู้กล้าของคุณ:")
    if not name: name = "ผู้กล้านิรนาม"
    
    player = Character(name, "human", "warrior")
    player.show_stats()

    monsters = load_data()
    
    while player.hp > 0:
        log("\nคุณจะทำอะไรต่อไป?", Colors.BLUE)
        log("1. ออกสำรวจ | 2. ดูสถานะ | 3. พักผ่อน | 4. ออกจากเกม")
        choice = ask("เลือก (1-4):")
        
        if choice == "1":
            log("คุณเดินเข้าไปในป่าลึก...", Colors.GRAY)
            time.sleep(1)
            
            if roll_dice(20) > 10:
                # เจอศัตรู
                m_key = random.choice(list(monsters.keys()))
                monster = monsters[m_key].copy() # Copy มาเพื่อไม่ให้แก้ค่าต้นฉบับ
                
                log(f"\n⚠️ พบ {monster['name']}! {monster['description']}", Colors.RED)
                
                while monster['hp'] > 0 and player.hp > 0:
                    result = combat_turn(player, monster)
                    if result == True:
                        log(f"🏆 ชนะแล้ว! ได้รับ Gold 10", Colors.YELLOW)
                        player.gold += 10
                        player.exp += 20
                        break
                    elif result == "flee":
                        break
                    
                    time.sleep(0.5)
            else:
                # เจอเหตุการณ์
                log("ไม่พบอะไรน่าสนใจ... แต่เจอก้อนทอง!", Colors.YELLOW)
                player.gold += 5

        elif choice == "2":
            player.show_stats()
            
        elif choice == "3":
            log("คุณพักผ่อน... HP ฟื้นฟูเต็มเปี่ยม", Colors.GREEN)
            player.hp = player.max_hp
            
        elif choice == "4":
            log("ลาก่อนผู้กล้า...", Colors.GRAY)
            break
            
        else:
            log("คำสั่งไม่ถูกต้อง", Colors.RED)

    if player.hp <= 0:
        log("\nGAME OVER", Colors.RED)

# ==========================================
# Modern Terminal UI PySide6
# ==========================================
class ModernTerminal(QMainWindow):
    def __init__(self):
        super().__init__()
        global app_instance
        app_instance = self
        
        self.setWindowTitle("RPG CLI Beta EDITION - UTF8")
        self.resize(1000, 700)
        
        # คิวสำหรับจัดการ Input
        self.input_queue = []
        self.input_lock = threading.Condition()

        # ส่วนประกอบ UI
        self.setup_ui()
        self.apply_styles()
        
        # เชื่อมต่อ Signals
        signals.print_signal.connect(self.append_text)
        signals.clear_signal.connect(self.display.clear)

        # เริ่ม Thread เกม
        self.game_thread = threading.Thread(target=run_rpg_game, daemon=True)
        self.game_thread.start()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Header
        self.status_bar = QLabel(" ระบบปฏิบัติการ: GorgonOS v1.0 | Encoding: UTF-8 ")
        layout.addWidget(self.status_bar)

        # Display Area
        self.display = QTextEdit()
        self.display.setReadOnly(True)
        self.display.setUndoRedoEnabled(False)
        layout.addWidget(self.display)

        # Input Area
        input_layout = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("พิมพ์คำสั่งที่นี่...")
        self.entry.returnPressed.connect(self.handle_submit)
        
        self.send_btn = QPushButton("ENTER")
        self.send_btn.clicked.connect(self.handle_submit)
        
        input_layout.addWidget(self.entry)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; }
            QLabel { color: #555; font-size: 10px; font-family: 'Segoe UI', sans-serif; }
            QTextEdit { 
                background-color: #0d0d0d; 
                color: #ecf0f1; 
                font-family: 'Consolas', 'Sarabun', monospace; 
                font-size: 16px;
                border: 2px solid #2c3e50;
                border-radius: 5px;
                padding: 10px;
            }
            QLineEdit { 
                background-color: #2c3e50; 
                color: white; 
                border: none; 
                border-radius: 5px; 
                padding: 12px;
                font-size: 14px;
                font-family: 'Consolas', 'Sarabun', monospace; 
            }
            QPushButton { 
                background-color: #e67e22; 
                color: white; 
                font-weight: bold; 
                border-radius: 5px; 
                padding: 8px 20px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover { background-color: #d35400; }
        """)

    def append_text(self, text, color):
        # แปลงข้อความให้เป็น HTML เพื่อใส่สี
        safe_text = text.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        html = f'<span style="color:{color};">{safe_text}</span>'
        self.display.append(html)
        self.display.moveCursor(QTextCursor.End)

    def handle_submit(self):
        text = self.entry.text()
        self.append_text(f"<b>> {text}</b>", "#2ecc71")
        self.entry.clear()
        
        with self.input_lock:
            self.input_queue.append(text)
            self.input_lock.notify_all()

    def wait_for_input(self):
        """ฟังก์ชันนี้จะถูกเรียกจาก Thread เกม เพื่อหยุดรอ Input"""
        with self.input_lock:
            while not self.input_queue:
                self.input_lock.wait()
            return self.input_queue.pop(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernTerminal()
    window.show()
    sys.exit(app.exec())
