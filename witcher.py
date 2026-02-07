import random
import time
import json
import os
import sys
import io

# === System Setup ===
def setup_windows_encoding():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (AttributeError, Exception):
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, 
                encoding='utf-8',
                errors='replace',
                line_buffering=True
            )
        import os
        os.environ['PYTHONIOENCODING'] = 'utf-8'
setup_windows_encoding()

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    ORANGE = '\033[38;5;208m' 
    END = '\033[0m'

def roll_dice(sides, modifier=0):
    return random.randint(1, sides) + modifier

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_separator():
    print(f"{Colors.WHITE}" + "="*60 + f"{Colors.END}")

# === Data & Config ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(BASE_DIR, "save.json")

def get_monsters(conjunction_active=False):
    monsters = {
        "drowner": {
            "name": "Drowner", "hp": 25, "min_dmg": 3, "max_dmg": 7,
            "type": "Necrophage", "desc": "พรายน้ำ ตัวเหม็นคาว แพ้ไฟ",
            "weakness": "Igni", "loot": "Drowner Brain", "exp": 20
        },
        "ghoul": {
            "name": "Ghoul", "hp": 30, "min_dmg": 4, "max_dmg": 9,
            "type": "Necrophage", "desc": "กินซากศพ เคลื่อนที่ไว",
            "weakness": "Necrophage Oil", "loot": "Ghoul Blood", "exp": 25
        },
        "bandit": {
            "name": "Bandit Leader", "hp": 40, "min_dmg": 5, "max_dmg": 10,
            "type": "Human", "desc": "โจรป่าดักปล้นนักเดินทาง",
            "weakness": "Axii", "loot": "Oren Pouch", "exp": 30
        },
        "bear": {
            "name": "Grizzly Bear", "hp": 60, "min_dmg": 8, "max_dmg": 14,
            "type": "Beast", "desc": "หมีดุร้าย พละกำลังมหาศาล",
            "weakness": "Quen", "loot": "Bear Fat", "exp": 40
        },
        "bruxa": {
            "name": "Bruxa", "hp": 55, "min_dmg": 10, "max_dmg": 18,
            "type": "Vampire", "desc": "แวมไพร์สาว ล่องหนได้",
            "weakness": "Yrden", "loot": "Vampire Fang", "exp": 60
        },
        "fiend": {
            "name": "Fiend", "hp": 100, "min_dmg": 12, "max_dmg": 22,
            "type": "Relict", "desc": "อสูรสามตา สะกดจิตได้",
            "weakness": "Samum Bomb", "loot": "Fiend Eye", "exp": 100
        }
    }
    if conjunction_active:
        for key in monsters:
            monsters[key]['name'] = f"Chaos {monsters[key]['name']}"
            monsters[key]['hp'] = int(monsters[key]['hp'] * 1.5)
            monsters[key]['min_dmg'] += 4
            monsters[key]['desc'] += f" {Colors.RED}[Conjunction]{Colors.END}"
    return monsters

def get_recipes():
    return {
        "Swallow": {"ingredients": {"Drowner Brain": 1, "Dwarven Spirit": 1}, "desc": "ฟื้นฟู HP"},
        "Thunderbolt": {"ingredients": {"Ghoul Blood": 1, "Dwarven Spirit": 1}, "desc": "เพิ่มพลังโจมตี"},
        "Cat": {"ingredients": {"Fiend Eye": 1, "Dwarven Spirit": 1}, "desc": "มองในที่มืด/คริติคอล"}
    }

# --- Class Witcher ---
class Witcher:
    def __init__(self, name, school):
        self.name = name
        self.school = school
        self.level = 1
        self.exp = 0
        self.gold = 100
        self.inventory = ["Witcher Silver Sword", "Bread", "Dwarven Spirit"]
        self.active_quests = []
        
        self.max_hp = 100
        self.base_dmg = 6
        self.sign_power = 1
        self.crit_chance = 5
        self.temp_buff = 0  # บัฟชั่วคราวจากการดื่มยาก่อนสู้
        
        if school == "Wolf":
            self.max_hp = 110
            self.base_dmg = 8
            self.desc = "สมดุล (Geralt's Path)"
        elif school == "Griffin":
            self.sign_power = 3
            self.max_hp = 90
            self.desc = "เชี่ยวชาญ Sign"
        elif school == "Bear":
            self.max_hp = 150
            self.base_dmg = 9
            self.sign_power = 0
            self.crit_chance = 0
            self.desc = "ถึกทน โจมตีหนัก เชื่องช้า"
        elif school == "Cat":
            self.max_hp = 80
            self.base_dmg = 10
            self.crit_chance = 15
            self.desc = "โจมตีรุนแรง แต่เปราะบาง"
        elif school == "Viper":
            self.max_hp = 100
            self.base_dmg = 7
            self.crit_chance = 10
            self.inventory.append("Thunderbolt")
            self.desc = "นักลอบสังหาร เชี่ยวชาญยาพิษ"
        elif school == "Lynx":
            self.max_hp = 95
            self.base_dmg = 7
            self.crit_chance = 25
            self.desc = "สำนักใหม่ ความเร็วและคริติคอลสูงสุด"
        
        self.hp = self.max_hp

    def to_dict(self):
        return {
            "name": self.name, "school": self.school, "level": self.level,
            "exp": self.exp, "gold": self.gold, "inventory": self.inventory,
            "active_quests": self.active_quests, "max_hp": self.max_hp,
            "base_dmg": self.base_dmg, "sign_power": self.sign_power,
            "crit_chance": self.crit_chance
        }

    @classmethod
    def from_dict(cls, data):
        player = cls(data["name"], data["school"])
        player.level = data["level"]
        player.exp = data["exp"]
        player.gold = data["gold"]
        player.inventory = data["inventory"]
        player.active_quests = data.get("active_quests", [])
        player.max_hp = data["max_hp"]
        player.base_dmg = data["base_dmg"]
        player.sign_power = data["sign_power"]
        player.crit_chance = data["crit_chance"]
        player.hp = player.max_hp
        player.temp_buff = 0 
        return player

    # --- Added Methods (Fix Crash) ---
    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp < 0: self.hp = 0
        print(f"{Colors.RED}{self.name} โดนโจมตี {dmg} หน่วย! (เหลือ HP: {self.hp}){Colors.END}")

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp: self.hp = self.max_hp
        print(f"{Colors.GREEN}ฟื้นฟู {amount} HP (HP: {self.hp}){Colors.END}")

    def gain_exp(self, amount):
        self.exp += amount
        print(f"ได้รับ {amount} EXP")
        # Level up logic check
        req_exp = self.level * 100
        if self.exp >= req_exp:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp = 0
        self.max_hp += 10
        self.base_dmg += 2
        self.hp = self.max_hp
        print(f"\n{Colors.YELLOW}*** LEVEL UP! Rank {self.level} ***{Colors.END}")

    def use_sign(self, sign_name, enemy=None):
        dmg = 0
        effect = ""
        
        if sign_name == "Igni":
            dmg = 10 + (self.sign_power * 6)
            print(f"{Colors.ORANGE}Igni!{Colors.END} พ่นไฟใส่ศัตรู")
        elif sign_name == "Aard":
            dmg = 4 + (self.sign_power * 2)
            effect = "stun"
            print(f"{Colors.CYAN}Aard!{Colors.END} กระแทกศัตรู")
        elif sign_name == "Quen":
            print(f"{Colors.YELLOW}Quen!{Colors.END} สร้างเกราะ")
            return 0, "shield"
        elif sign_name == "Yrden":
            effect = "slow"
            print(f"{Colors.PURPLE}Yrden!{Colors.END} วางกับดักหนืด")
        elif sign_name == "Axii":
            if enemy:
                print(f"{Colors.WHITE}Axii!{Colors.END} สะกดจิต {enemy['name']} ให้มึนงง!")
                effect = "hypnotize"
            else:
                print(f"{Colors.WHITE}Axii!{Colors.END} (ใช้ในการเจรจา)")
        
        return dmg, effect

    def brew_potion(self, potion_name):
        recipes = get_recipes()
        if potion_name not in recipes:
            print("ไม่รู้จักสูตรยานี้")
            return

        ingredients_needed = recipes[potion_name]["ingredients"]
        for ing, qty in ingredients_needed.items():
            if self.inventory.count(ing) < qty:
                print(f"{Colors.RED}ขาดวัตถุดิบ: {ing}{Colors.END}")
                return
        
        for ing, qty in ingredients_needed.items():
            for _ in range(qty):
                self.inventory.remove(ing)
        
        self.inventory.append(potion_name)
        print(f"{Colors.GREEN}ปรุงยา {potion_name} สำเร็จ!{Colors.END}")

# === Game Systems ===
def save_game(player):
    try:
        print(f"บันทึกที่: {os.path.abspath(SAVE_FILE)}")
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(player.to_dict(), f, ensure_ascii=False, indent=4)
        print(f"{Colors.GREEN}>> บันทึกเกมเรียบร้อยที่ {SAVE_FILE}{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}เกิดข้อผิดพลาดในการบันทึก: {e}{Colors.END}")

def load_game():
    if not os.path.exists(SAVE_FILE):
        print(f"{Colors.RED}ไม่พบไฟล์เซฟ{Colors.END}")
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Witcher.from_dict(data)
    except Exception as e:
        print(f"{Colors.RED}ไฟล์เซฟเสียหาย: {e}{Colors.END}")
        return None

def combat(player, monster_key, conjunction_active):
    monsters = get_monsters(conjunction_active)
    monster = monsters[monster_key].copy()
    
    print_separator()
    print(f"{Colors.RED}COMBAT STARTED! VS {monster['name']}{Colors.END}")
    
    # แจ้งเตือนบัฟถ้ามี
    if player.temp_buff > 0:
        print(f"{Colors.YELLOW}>> บัฟโจมตีทำงาน (+{player.temp_buff} Dmg) <<{Colors.END}")

    enemy_hp = monster['hp']
    player_shield = 0
    enemy_stunned = False
    
    while player.hp > 0 and enemy_hp > 0:
        print(f"\n{player.name}: {player.hp}/{player.max_hp} HP | {monster['name']}: {enemy_hp} HP")
        print("1. Fast Attack  2. Strong Attack")
        print("3. Use Sign     4. Items/Potions")
        
        choice = input("Action: ")
        dmg_dealt = 0
        
        # Player Turn
        if choice == "1":
            if roll_dice(100) <= player.crit_chance:
                dmg_dealt = (player.base_dmg * 2) + player.temp_buff
                print(f"{Colors.YELLOW}CRITICAL HIT!{Colors.END}")
            else:
                dmg_dealt = player.base_dmg + roll_dice(3) + player.temp_buff
        
        elif choice == "2":
            if roll_dice(100) > 40: # Hit chance
                dmg_dealt = player.base_dmg + roll_dice(8) + 2 + player.temp_buff
                print("ฟันรุนแรง!")
            else:
                print("โจมตีหนักพลาดเป้า!")
        
        elif choice == "3":
            print("Signs: (1)Igni (2)Aard (3)Quen (4)Yrden (5)Axii")
            s = input("Select: ")
            s_dmg, effect = 0, ""
            if s=="1": s_dmg, effect = player.use_sign("Igni", monster)
            if s=="2": s_dmg, effect = player.use_sign("Aard", monster)
            if s=="3": s_dmg, effect = player.use_sign("Quen", monster)
            if s=="4": s_dmg, effect = player.use_sign("Yrden", monster)
            if s=="5": s_dmg, effect = player.use_sign("Axii", monster)
            
            dmg_dealt = s_dmg
            if effect == "shield": player_shield = 20
            if effect == "stun": enemy_stunned = True 
            if effect == "hypnotize": 
                enemy_stunned = True
                print(f"{monster['name']} ยืนนิ่งด้วยความมึนงง!")
            
            if monster['weakness'] == "Igni" and s=="1": dmg_dealt *= 1.5
            if monster['weakness'] == "Axii" and s=="5": 
                print(f"{Colors.GREEN}Axii ได้ผลดีเยี่ยมกับ {monster['name']}!{Colors.END}")
                enemy_stunned = True 
        
        elif choice == "4":
            print(f"Inventory: {player.inventory}")
            use = input("พิมพ์ชื่อไอเทม (หรือ Enter เพื่อปิด): ")
            
            # Fix Cancelling inventory ---
            if use == "":
                continue

            if use in player.inventory:
                if use == "Swallow":
                    player.heal(30)
                    player.inventory.remove(use)
                elif use == "Thunderbolt":
                    print("พลังโจมตีเพิ่มขึ้นชั่วคราว!")
                    dmg_dealt += 10 
                    player.inventory.remove(use)
                else:
                    print("ไอเทมนี้ใช้ในต่อสู้ไม่ได้")
                    continue # ไม่เสียเทิร์นถ้าเลือกผิด
            else:
                print("ไม่มีไอเทมนั้น")
                continue # ไม่เสียเทิร์น

        # Apply Damage
        if dmg_dealt > 0:
            enemy_hp -= int(dmg_dealt)
            print(f"ทำดาเมจ {int(dmg_dealt)} หน่วย")
        
        if enemy_hp <= 0:
            print(f"\n{Colors.GREEN}VICTORY!{Colors.END}")
            print(f"ได้รับ: {monster['loot']} และ {monster['exp']} XP")
            player.inventory.append(monster['loot'])
            player.gain_exp(monster['exp'])
            player.temp_buff = 0 # รีเซ็ตบัฟหลังจบการต่อสู้
            
            # Check Quest Completion
            if monster_key in player.active_quests:
                print(f"{Colors.YELLOW}>> เควสต์กำจัด {monster['name']} สำเร็จ! รับรางวัล 100 Gold <<{Colors.END}")
                player.gold += 100
                player.active_quests.remove(monster_key)
            return True

        # Enemy Turn
        if enemy_stunned:
            print(f"{monster['name']} ติดสถานะมึนงง/สะกดจิต! (ข้ามเทิร์น)")
            enemy_stunned = False
        else:
            enemy_dmg = roll_dice(monster['max_dmg'], monster['min_dmg'])
            if player_shield > 0:
                print(f"{Colors.YELLOW}Quen รับดาเมจแทน!{Colors.END}")
                player_shield = 0
                enemy_dmg = 0
            
            player.take_damage(enemy_dmg) # method exists
            
    # ถ้าแพ้แล้ว Reset Buff
    player.temp_buff = 0
    return False

# --- Town & Interaction ---
def alchemy_menu(player):
    print_separator()
    print("--- ALCHEMY STATION ---")
    recipes = get_recipes()
    for name, data in recipes.items():
        print(f"{name}: {data['desc']}")
        req_str = ", ".join([f"{k} x{v}" for k,v in data['ingredients'].items()])
        print(f"  ต้องการ: {req_str}")
    
    print(f"\nวัตถุดิบที่มี: {[i for i in player.inventory if 'Brain' in i or 'Blood' in i or 'Spirit' in i or 'Eye' in i]}")
    choice = input("พิมพ์ชื่อยาเพื่อปรุง (หรือ Enter เพื่อออก): ")
    if choice:
        player.brew_potion(choice)

def shop_menu(player):
    print_separator()
    print(f"--- MERCHANT (Gold: {player.gold}) ---")
    items = {
        "1": {"name": "Bread", "price": 5, "type": "food"},
        "2": {"name": "Dwarven Spirit", "price": 15, "type": "ingredient"},
        "3": {"name": "Swallow Recipe", "price": 50, "type": "info"},
        "4": {"name": "Witcher Steel Sword", "price": 100, "type": "weapon"}
    }
    for k, v in items.items():
        print(f"{k}. {v['name']} - {v['price']} Gold")
    
    buy = input("เลือกซื้อ (1-4) หรือกด Enter เพื่อออก: ")
    if buy in items:
        item = items[buy]
        if player.gold >= item['price']:
            player.gold -= item['price']
            player.inventory.append(item['name'])
            print(f"ซื้อ {item['name']} สำเร็จ!")
        else:
            print("เงินไม่พอ!")

def notice_board(player):
    print_separator()
    print("--- NOTICE BOARD ---")
    contracts = ["drowner", "ghoul", "bandit", "bear"]
    daily_contract = random.choice(contracts)
    
    print(f"ประกาศ: ชาวบ้านเดือดร้อนจาก {daily_contract}!")
    print(f"รางวัล: 100 Gold")
    
    if daily_contract in player.active_quests:
        print("(คุณรับงานนี้ไปแล้ว)")
    else:
        confirm = input("ดึงป้ายประกาศรับงาน? (y/n): ")
        if confirm.lower() == 'y':
            player.active_quests.append(daily_contract)
            print(f"รับงานกำจัด {daily_contract} แล้ว! ไปหามันในป่า")

def talk_to_npc(player):
    print_separator()
    npcs = ["ชาวบ้านขี้เมา", "ยามหน้าเมือง", "หญิงสาวลึกลับ"]
    npc = random.choice(npcs)
    print(f"คุณเดินเข้าไปคุยกับ {npc}...")
    
    if npc == "ชาวบ้านขี้เมา":
        print("'เฮ้... วิทเชอร์... มีเศษเงินสัก 5 โอเรนไหม?'")
        choice = input("1. ให้เงิน  2. ใช้ Axii ไล่ไป: ")
        if choice == "1":
            if player.gold >= 5:
                player.gold -= 5
                print("เขาขอบคุณและให้ข่าวลือ: 'ข้าเห็นปีศาจตาสามดวงในป่าลึก...' (ได้เบาะแส Fiend)")
        elif choice == "2":
            player.use_sign("Axii")
            print("ชาวบ้านเดินจากไปแบบงงๆ")
            
    elif npc == "ยามหน้าเมือง":
        print("'ระวังตัวด้วย ช่วงนี้โจรชุกชุม'")
        print("(คุณได้ข้อมูลตำแหน่ง Bandit)")
    
    elif npc == "หญิงสาวลึกลับ":
        print("'เจ้าดูเหนื่อยนะ... สนใจสมุนไพรไหม?'")
        player.inventory.append("Dwarven Spirit")
        print("นางยัดขวดเหล้าใส่มือคุณแล้วเดินหนีไป")

def explore_town(player):
    print(f"\n{Colors.CYAN}คุณกำลังเดินสำรวจเมือง Novigrad...{Colors.END}")
    event = random.randint(1, 4)
    if event == 1:
        print("คุณพบถุงเงินตกอยู่!")
        found = random.randint(5, 20)
        player.gold += found
        print(f"ได้รับ {found} Gold")
    elif event == 2:
        print("นักเลงท้องถิ่นพยายามหาเรื่อง!")
        choice = input("1. ชกต่อย  2. ใช้ Axii: ")
        if choice == "2":
            player.use_sign("Axii")
            print("นักเลงขอโทษและวิ่งหนีไป (ได้รับ XP นิดหน่อย)")
            player.gain_exp(10)
        else:
            print("คุณต่อยมันร่วงในหมัดเดียว")
    else:
        print("บรรยากาศในเมืองคึกคัก... แต่ไม่มีอะไรเกิดขึ้นเป็นพิเศษ")

def town_hub(player):
    in_town = True
    while in_town:
        clear_screen()
        print(f"{Colors.BOLD}{Colors.BLUE}--- TOWN HUB ---{Colors.END}")
        print(f"Player: {player.name} ({player.school}) | Gold: {player.gold}")
        print("Quests:", player.active_quests)
        print("1. รับงานที่ป้ายประกาศ (Notice Board)")
        print("2. ร้านค้า (Merchant)")
        print("3. ปรุงยา (Alchemy)")
        print("4. เดินเล่น/คุยกับ NPC")
        print("5. ออกจากเมือง (ไปล่า)")
        print("6. บันทึกเกม (Save)")
        
        c = input("เลือก: ")
        if c == "1": notice_board(player); input("Enter...")
        elif c == "2": shop_menu(player); input("Enter...")
        elif c == "3": alchemy_menu(player); input("Enter...")
        elif c == "4": 
            sub = input("1. คุยกับ NPC  2. เดินสำรวจ: ")
            if sub == "1": talk_to_npc(player)
            else: explore_town(player)
            input("Enter...")
        elif c == "5": in_town = False
        elif c == "6": save_game(player); input("Enter...")

# --- Feature: Inventory & Stats Menu ---
def inventory_menu(player):
    print_separator()
    print(f"{Colors.BOLD}--- INVENTORY & STATS ---{Colors.END}")
    print(f"Name: {player.name} | School: {player.school} | Level: {player.level}")
    print(f"HP: {player.hp}/{player.max_hp} | Base DMG: {player.base_dmg} | Crit: {player.crit_chance}%")
    print(f"Gold: {player.gold}")
    print(f"\nInventory: {player.inventory}")
    
    print("\n[ดื่มยาเตรียมตัวก่อนสู้ได้ที่นี่]")
    use = input("พิมพ์ชื่อยา (Swallow/Thunderbolt) หรือ Enter เพื่อออก: ")
    
    if use in player.inventory:
        if use == "Swallow":
            player.inventory.remove(use)
            player.heal(30)
            print("ดื่ม Swallow แล้ว HP ฟื้นฟู")
        elif use == "Thunderbolt":
            player.inventory.remove(use)
            player.temp_buff = 10
            print(f"{Colors.GREEN}ดื่ม Thunderbolt แล้ว! (ดาเมจจะ +10 ในการต่อสู้ครั้งถัดไป){Colors.END}")
        else:
            print("ไอเทมนี้ใช้ที่นี่ไม่ได้")
    elif use != "":
        print("ไม่มีไอเทมนั้น")

# --- Main Loop ---
def main_menu():
    clear_screen()
    print(f"{Colors.BOLD}=== THE WITCHER: PATH OF DESTINY ==={Colors.END}")
    print("1. New Game")
    print("2. Load Game")
    print("3. Exit")
    
    choice = input("Select: ")
    if choice == "2":
        loaded = load_game()
        if loaded:
            print(f"โหลดเซฟสำเร็จ! {loaded.name}")
            time.sleep(1)
            return loaded
        else:
            input("Enter เพื่อเริ่มเกมใหม่...")
            
    if choice == "3": sys.exit()
    
    # New Game Creation
    clear_screen()
    name = input("ตั้งชื่อ : ")
    print("\nเลือกสำนัก (School):")
    print("1. Wolf (สมดุล) - Geralt's choice")
    print("2. Griffin (เวทมนตร์)")
    print("3. Bear (ถึกทน)")
    print("4. Cat (โจมตีแรง ตัวบาง)")
    print("5. Viper (พิษ/คริติคอล)")
    print("6. Lynx (คล่องแคล่วกึ่งสมดุล)")
    
    s_map = {"1":"Wolf", "2":"Griffin", "3":"Bear", "4":"Cat", "5":"Viper", "6":"Lynx"}
    school = s_map.get(input("เลือก (1-6): "), "Wolf")
    return Witcher(name, school)

def game_loop():
    player = main_menu()
    
    battles = 0
    conjunction = False
    
    while True:
        clear_screen()
        if battles >= 5 and not conjunction:
            conjunction = True
            print(f"{Colors.RED}!!! SECOND CONJUNCTION !!!{Colors.END}")
            print("มิติวิปริต... มอนสเตอร์แข็งแกร่งขึ้น!")
            input("กด Enter...")

        print(f"\n--- WILDERNESS ---")
        print("1. เข้าเมือง (Novigrad)")
        print("2. ออกล่า (Hunt Monster)")
        print("3. นั่งสมาธิ (Heal)")
        print("4. บันทึกเกม")
        print("5. เช็คกระเป๋า (Inventory)")
        print("6. ออกจากเกม")
        
        act = input("เลือก: ")
        
        if act == "1":
            town_hub(player)
            
        elif act == "2":
            monsters = get_monsters(conjunction)
            possible = list(monsters.keys())
            if player.active_quests:
                possible.extend(player.active_quests * 3) 
            
            target = random.choice(possible)
            victory = combat(player, target, conjunction)
            if victory:
                battles += 1
            else:
                print("GAME OVER")
                break
                
        elif act == "3":
            print("นั่งสมาธิข้างกองไฟ...")
            player.hp = player.max_hp
            print("HP เต็มแล้ว")
            input("Enter...")
            
        elif act == "4":
            save_game(player)
            input("Enter...")

        elif act == "5":
            inventory_menu(player)
            input("Enter...")
            
        elif act == "6":
            break

if __name__ == "__main__":
    game_loop()