import random
import time
import json
import os
import sys
import io

def setup_windows_encoding():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            print("Using sys.stdout.reconfigure() for UTF-8")
        except (AttributeError, Exception):
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, 
                encoding='utf-8',
                errors='replace',
                line_buffering=True
            )
            print("Using io wrapper for UTF-8 support")
        import os
        os.environ['PYTHONIOENCODING'] = 'utf-8'
setup_windows_encoding()

# สีข้อความ
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def roll_dice(sides, modifier=0):
    """ทอยลูกเต๋า"""
    return random.randint(1, sides) + modifier

def clear_screen():
    """ล้างหน้าจอ"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_separator():
    """เส้นคั่น"""
    print("="*50)

def get_save_slots():
    """ตรวจสอบสล็อตเซฟที่มีอยู่"""
    save_slots = []
    for i in range(3):
        if os.path.exists(f"save{i}.json"):
            save_slots.append(i)
    return save_slots

def save_game(player, enemies_defeated):
    """บันทึกเกม"""
    clear_screen()
    print(f"{Colors.BOLD}=== บันทึกเกม ==={Colors.END}")
    
    save_slots = get_save_slots()
    
    if len(save_slots) < 3:
        print(f"\n{Colors.CYAN}มีสล็อตเซฟว่างอยู่:{Colors.END}")
        for i in range(3):
            if i not in save_slots:
                print(f"{i+1}. สร้างเซฟใหม่ในสล็อต {i+1}")
    
    if save_slots:
        print(f"\n{Colors.YELLOW}สล็อตเซฟที่มีอยู่:{Colors.END}")
        for slot in save_slots:
            try:
                with open(f"save{slot}.json", "r", encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"{slot+1}. เซฟสล็อต {slot+1}: {data['player']['name']} ระดับ {data['player']['level']}")
            except:
                print(f"{slot+1}. เซฟสล็อต {slot+1}: ไม่สามารถอ่านข้อมูลได้")
    
    print("\n4. ยกเลิกการบันทึก")
    
    while True:
        choice = input("\nเลือกสล็อตเซฟ (1-4): ")
        
        if choice == "4":
            print(f"{Colors.YELLOW}ยกเลิกการบันทึก{Colors.END}")
            return False
        
        try:
            slot = int(choice) - 1
            if 0 <= slot <= 2:
                # เตรียมข้อมูลที่จะบันทึก
                save_data = {
                    "player": {
                        "name": player.name,
                        "race": player.race,
                        "char_class": player.char_class,
                        "max_hp": player.max_hp,
                        "hp": player.hp,
                        "base_damage": player.base_damage,
                        "armor": player.armor,
                        "gold": player.gold,
                        "exp": player.exp,
                        "level": player.level,
                        "inventory": player.inventory,
                        "status_effects": player.status_effects
                    },
                    "game_stats": {
                        "enemies_defeated": enemies_defeated,
                        "save_timestamp": time.time()
                    }
                }
                with open(f"save{slot}.json", "w", encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
                
                print(f"{Colors.GREEN}บันทึกเกมสำเร็จในสล็อต {slot+1}!{Colors.END}")
                input(f"\n{Colors.YELLOW}กด Enter เพื่อกลับไป...{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}โปรดเลือกสล็อต 1-3 หรือ 4 เพื่อยกเลิก{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}โปรดป้อนตัวเลขที่ถูกต้อง{Colors.END}")

def load_game():
    """โหลดเกมจากไฟล์เซฟ"""
    clear_screen()
    print(f"{Colors.BOLD}=== โหลดเกม ==={Colors.END}")
    
    save_slots = get_save_slots()
    
    if not save_slots:
        print(f"{Colors.RED}ไม่พบไฟล์เซฟเกม{Colors.END}")
        input(f"\n{Colors.YELLOW}กด Enter เพื่อกลับไป...{Colors.END}")
        return None, 0
    
    print(f"\n{Colors.CYAN}สล็อตเซฟที่มีอยู่:{Colors.END}")
    for slot in save_slots:
        try:
            with open(f"save{slot}.json", "r", encoding='utf-8') as f:
                data = json.load(f)
                timestamp = data['game_stats']['save_timestamp']
                save_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
                print(f"{slot+1}. เซฟสล็อต {slot+1}: {data['player']['name']} (ระดับ {data['player']['level']}) - {save_time}")
        except:
            print(f"{slot+1}. เซฟสล็อต {slot+1}: ไม่สามารถอ่านข้อมูลได้")
    
    print(f"\n{len(save_slots)+1}. ยกเลิกการโหลด")
    
    while True:
        try:
            choice = int(input("\nเลือกสล็อตเซฟที่จะโหลด: "))
            
            if choice == len(save_slots) + 1:
                print(f"{Colors.YELLOW}ยกเลิกการโหลด{Colors.END}")
                return None, 0
            
            slot = choice - 1
            if slot in save_slots:
                try:
                    with open(f"save{slot}.json", "r", encoding='utf-8') as f:
                        data = json.load(f)
                    
                    player_data = data['player']
                    player = Character(
                        player_data['name'], 
                        player_data['race'], 
                        player_data['char_class']
                    )

                    player.max_hp = player_data['max_hp']
                    player.hp = player_data['hp']
                    player.base_damage = player_data['base_damage']
                    player.armor = player_data['armor']
                    player.gold = player_data['gold']
                    player.exp = player_data['exp']
                    player.level = player_data['level']
                    player.inventory = player_data['inventory']
                    player.status_effects = player_data['status_effects']
                    
                    enemies_defeated = data['game_stats']['enemies_defeated']
                    
                    print(f"{Colors.GREEN}โหลดเกมสำเร็จ!{Colors.END}")
                    print(f"ยินดีต้อนรับกลับ {player.name} ระดับ {player.level}")
                    
                    input(f"\n{Colors.YELLOW}กด Enter เพื่อเริ่มการผจญภัยต่อ...{Colors.END}")
                    return player, enemies_defeated
                    
                except Exception as e:
                    print(f"{Colors.RED}เกิดข้อผิดพลาดในการโหลด: {e}{Colors.END}")
                    return None, 0
            else:
                print(f"{Colors.RED}สล็อตที่เลือกไม่มีไฟล์เซฟ{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}โปรดป้อนตัวเลขที่ถูกต้อง{Colors.END}")

# โหลดข้อมูลจาก JSON (ถ้ามี)
def load_data():
    """โหลดข้อมูลมอนสเตอร์และไอเทม"""
    monsters = {
        "goblin": {
            "name": "ก็อบลิน",
            "hp": 15,
            "min_dmg": 1,
            "max_dmg": 6,
            "description": "มอนสเตอร์ตัวเล็กตาแดง",
            "gore_texts": {
                "crit_hit": [
                    "คุณฟันคอของก็อบลินขาดลอย! หัวมันกระเด็นไปกระแทกผนังพร้อมเสียงกระแทกเปียก",
                    "คุณแทงดาบทะลุท้องก็อบลินแล้วฉีกขึ้นมาจนถึงคาง ไส้และเลือดทะลักท่วมพื้น",
                    "คุณฟาดศอกกลางหน้า ก็อบลิน กะโหลกแตกเสียงดังกร๊อบ หนังตาข้างซ้ายหลุดจากเบ้า"
                ],
                "crit_fail": [
                    "ดาบของคุณพลาดและเสียบลงพื้นจนด้ามหัก เศษไม้ทิ่มฝ่ามือคุณเลือดไหล",
                    "คุณสะดุดกองอึก็อบลินล้มหน้าคว่ำ กลิ่นเหม็นสาปเข้าจมูก",
                    "ก็อบลินหลบได้ คุณโจมตีพลาดและหกล้มก้นกระแทกพื้นจนกระดูกก้นกบร้าว"
                ]
            }
        },
        "orc": {
            "name": "ออร์ค",
            "hp": 25,
            "min_dmg": 2,
            "max_dmg": 8,
            "description": "ยักษ์เขียวคล้ำหน้าตาโหดร้าย ฟันเหลืองและตัวเหม็น",
            "gore_texts": {
                "crit_hit": [
                    "คุณฟันแขนขวาออร์คขาด เนื้อและเอ็นฉีกขาดพร้อมเสียงกรอบแกรน",
                    "คุณแทงดาบเข้าตาออร์คด้านซ้ายทะลุออกหลังหัว น้ำตาและเลือดสมองกระเซ็น",
                    "คุณจู่โจมที่หัวออร์คอย่างแรง ของเหลวสีแดงคลุ้งกระจาย"
                ],
                "crit_fail": [
                    "ออร์คถ่มน้ำลายใส่หน้า คุณสูดเข้าไปสำลักและอาเจียนออกมา",
                    "คุณลื่นบนเลือดตัวเองล้มทับตะเกียงไฟ เนื้อหลังไหม้ส่งเสียงฉ่ามีควันขึ้น",
                    "ออร์คเตะถุงอัณฑะคุณเสียงดังเป๊ก คุณล้มลงปวดเบี้ยวไม่อาจลุก"
                ]
            }
        },
        "necrophile": {
            "name": "เนโครไฟล์",
            "hp": 35,
            "min_dmg": 3,
            "max_dmg": 10,
            "description": "ร่างเน่าเปื่อยที่ยังเคลื่อนไหวได้และมีหนอนไต่",
            "gore_texts": {
                "crit_hit": [
                    "คุณฟันร่างเนโครไฟล์เป็นสองท่อน หนอนนับร้อยร่วงหล่นดิ้นไปทั่ว",
                    "คุณเผาร่างเนโครไฟล์ด้วยไฟ กลิ่นเนื้อคนไหม้ปนน้ำเหลืองโชยเข้าจมูก",
                    "คุณทุบหัวเนโครไฟล์จนกะโหลกแบน สมองเน่าสีเขียวพุ่งออกทางรูตา"
                ],
                "crit_fail": [
                    "เนโครไฟล์อ้วกน้ำเหลืองใส่คุณ คุณสำลักและอาเจียนตาม",
                    "คุณเหยียบซากเน่าลื่นล้ม ตะปูสนิมทิ่มทะลุขา",
                    "เนโครไฟล์ฉีกเสื้อคุณและเลียหน้าอก คุณสะท้อนจนตัวแข็งไม่ขยับ"
                ]
            }
        },
        "succubus": {
            "name": "ซักคิวบัส",
            "hp": 30,
            "min_dmg": 2,
            "max_dmg": 12,
            "description": "ปีศาจเพศหญิงร่างเซ็กซี่แต่ตาแดงก่ำและมีเขา",
            "nsfw_texts": {
                "crit_hit": [
                    "คุณแทงดาบทะลุอกซักคิวบัส แต่มันยังยิ้มเยาะขณะเลือดสีดำไหล",
                    "คุณฟันคอซักคิวบัสขาด หลอดเลือดฉีดเลือดสีดำเป็นฝอยบนผนัง",
                    "คุณตัดปีกซักคิวบัส มันร้องครวญครางแบบสุดเสียงที่ฟังแล้วเข่าอ่อน"
                ],
                "crit_fail": [
                    "ซักคิวบัสจูบคุณจนขาดอากาศ รู้สึกเหมือนวิญญาณกำลังถูกดูด",
                    "มันลูบไล้ระหว่างขาคุณจนคุณแข็งทื่อ ไม่สามารถขยับได้",
                    "ซักคิวบัสใช้หางพันคอคุณและบีบจนลิ้นห้อย โลกมืดลงช้าๆ"
                ],
                "special": [
                    "ซักคิวบัสถูอวัยวะคุณผ่านกางเกง 'น่าเอ็นดู...เล็กกว่าที่คิดนะ'",
                    "มันเปิดเสื้อให้เห็นทรวงอก 'อยากมาเล่นด้วยไหม? แค่ยอมแพ้ก็ได้'",
                    "ซักคิวบัสเลียปาก 'ฉันจะทำให้เธอเสียใจที่ยังมีชีวิตอยู่'"
                ]
            }
        }
    }
    
    items = {
        "health potion": {
            "name": "น้ำยาบำบัด",
            "heal": 20,
            "description": "ของเหลวสีแดงข้น กลิ่นโลหิตผสมสมุนไพร"
        },
        "rage potion": {
            "name": "น้ำยาคลั่ง",
            "damage_bonus": 5,
            "duration": 3,
            "description": "ของเหลวสีดำเดือดปุดๆ กลิ่นเลือดผสมเหล็กไหล"
        },
        "dagger": {
            "name": "มีดสั้นเบ้อเริ่ม",
            "damage": 4,
            "description": "มีดสนิมติดเลือดเก่า ด้ามห่อด้วยหนังมนุษย์"
        },
        "vibrator": {
            "name": "เครื่องสั่นประหลาด",
            "special": "ทำให้ศัตรูสับสน",
            "description": "อุปกรณ์ไฟฟ้าที่ยังทำงานได้ ปลายมีคราบสีขาว"
        },
        "orc's club": {  
        "name": "Orc's club",
        "damage": 3,
        "description": "กระบองไม้ใหญ่ของออร์ค",
        "special": "มีโอกาสทำให้ศัตรูสตั้น"
        }
    }
    
    return monsters, items

class Character:
    def __init__(self, name, race, char_class):
        self.name = name
        self.race = race
        self.char_class = char_class
        self.max_hp = 0
        self.hp = 0
        self.base_damage = 0
        self.armor = 0
        self.gold = 0
        self.exp = 0
        self.level = 1
        self.inventory = []
        self.status_effects = []
        
        # stat ตามเผ่า
        if race == "human":
            self.max_hp = 25
            self.base_damage = 6
            self.armor = 2
        elif race == "elf":
            self.max_hp = 20
            self.base_damage = 8
            self.armor = 1
        elif race == "orc":
            self.max_hp = 30
            self.base_damage = 10
            self.armor = 0
            self.has_orc_club = True
            self.inventory.append("orc's club")
        elif race == "vampire":
            self.max_hp = 35
            self.base_damage = 9
            self.armor = 3
            self.inventory.append("vampire bite")
        
        # ปรับตามอาชีพ
        if char_class == "warrior":
            self.max_hp += 10
            self.base_damage += 4
        elif char_class == "rogue":
            self.max_hp += 5
            self.base_damage += 6
            self.inventory.append("dagger")
        elif char_class == "mage":
            self.max_hp += 3
            self.base_damage += 8
            self.inventory.append("fireball scroll")
        elif char_class == "necromancer":
            self.max_hp += 15
            self.base_damage += 7
            self.inventory.append("dead scroll")
        
        self.hp = self.max_hp
        self.gold = random.randint(10, 100)
    
    def show_stats(self):
        """แสดงสถานะตัวละคร"""
        print_separator()
        print(f"{Colors.BOLD}{self.name} - ระดับ {self.level}{Colors.END}")
        print(f"เผ่า: {self.race} | อาชีพ: {self.char_class}")
        print(f"HP: {Colors.RED}{self.hp}/{self.max_hp}{Colors.END}")
        print(f"โจมตี: {self.base_damage}")
        print(f"เกราะ: {self.armor}")
        print(f"ทอง: {Colors.YELLOW}{self.gold}{Colors.END} | EXP: {self.exp}")
        
        if self.inventory:
            print(f"\n{Colors.CYAN}สิ่งของ:{Colors.END}")
            for item in self.inventory:
                print(f"  - {item}")
        
        if self.status_effects:
            print(f"\n{Colors.PURPLE}สถานะผิดปกติ:{Colors.END}")
            for effect in self.status_effects:
                print(f"  - {effect}")
    
    def take_damage(self, damage):
        """รับความเสียหาย"""
        actual_damage = max(1, damage - self.armor)
        self.hp -= actual_damage
        
        # คำอธิบายความเสียหายแบบโหดๆ
        wounds = [
            f"เลือดสีแดงฉ่ำไหลจากแผลใหม่",
            f"กระดูกซี่โครงร้าวส่งเสียงกรือด",
            f"เลือดกระฉาดใส่ผนังเป็นรูปดอกไม้",
            f"เนื้อฉีกขาดเห็นเอ็นสีขาวด้านใน"
        ]
        
        if actual_damage >= 10:
            critical_wounds = [
                f"{Colors.RED}ดวงตาแตกกระจาย!{Colors.END}",
                f"{Colors.RED}นิ้วมือขาดสามนิ้ว!{Colors.END}",
                f"{Colors.RED}กระเพาะอาหารทะลุ!{Colors.END}"
            ]
            print(f"{random.choice(critical_wounds)}")
        
        print(f"ได้รับความเสียหาย {actual_damage} หน่วย ({random.choice(wounds)})")
        return self.hp > 0
    
    def heal(self, amount):
        """รักษาตัว"""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        heal_amount = self.hp - old_hp
        
        heals = [
            f"แผลปิดสนิทอย่างน่าอัศจรรย์",
            f"เลือดหยุดไหลและเนื้อใหม่งอกขึ้น",
            f"ความเจ็บปวดหายไปเหมือนไม่เคยมี",
            f"ร่างกายรู้สึกสดชื่นราวกับตื่นจากฝัน"
        ]
        
        print(f"รักษาได้ {heal_amount} HP ({random.choice(heals)})")
        return heal_amount

def create_character():
    """สร้างตัวละครใหม่"""
    clear_screen()
    print(f"{Colors.BOLD}=== สร้างตัวละคร ==={Colors.END}")
    
    name = input("ชื่อตัวละครของคุณ: ")
    
    print(f"\n{Colors.CYAN}เลือกเผ่า:{Colors.END}")
    races = [
        ("human", "มนุษย์ - สมดุลทุกด้าน"),
        ("elf", "เอลฟ์ - โจมตีแม่นยำ, HP น้อย"),
        ("orc", "ออร์ค - แข็งแกร่ง, ป้องกันต่ำ"),
        ("vampire", "แวมไพร์ - HP สูง, อ่อนต่อแสง")
    ]
    
    for i, (race_id, desc) in enumerate(races, 1):
        print(f"{i}. {race_id.title()} - {desc}")
    
    race_choice = int(input("เลือกเผ่า (1-4): ")) - 1
    selected_race = races[race_choice][0]
    
    print(f"\n{Colors.CYAN}เลือกอาชีพ:{Colors.END}")
    classes = [
        ("warrior", "นักรบ - HP สูง, โจมตีหนัก"),
        ("rogue", "โจร - โจมตีรวดเร็ว, มีดสั้นเริ่มต้น"),
        ("mage", "นักเวท - โจมตีเวทสูง, HP ต่ำ"),
        ("necromancer", "เนโครแมนเซอร์ - ควบคุมศพ, HP ปานกลาง")
    ]
    
    for i, (class_id, desc) in enumerate(classes, 1):
        print(f"{i}. {class_id.title()} - {desc}")
    
    class_choice = int(input("เลือกอาชีพ (1-4): ")) - 1
    selected_class = classes[class_choice][0]
    
    character = Character(name, selected_race, selected_class)
    
    clear_screen()
    print(f"{Colors.GREEN}สร้างตัวละครสำเร็จ!{Colors.END}")
    character.show_stats()
    
    input(f"\n{Colors.YELLOW}กด Enter เพื่อเริ่มการผจญภัย...{Colors.END}")
    return character

def critical_success_effect(attacker, defender, monster_data=None):
    """เอฟเฟกต์เมื่อทอยได้ 20 (Critical Success)"""
    effects = [
        {
            "name": "ตัดศรีษะ",
            "description": "โจมตีตัดคอขาดสะบั้น",
            "damage_multiplier": 3,
            "text": f"{Colors.RED}ตัดศรีษะขาด! ศรีษะกระเด็นไป{Colors.END}"
        },
        {
            "name": "แทงทะลุ",
            "description": "อาวุธทะลุร่างศัตรู",
            "damage_multiplier": 2.5,
            "text": f"{Colors.RED}แทงทะลุร่าง! ปลายอาวุธโผล่ออกอีกด้าน{Colors.END}"
        },
        {
            "name": "ทุบแหลก",
            "description": "ทุบจนกระดูกแหลกเหลว",
            "damage_multiplier": 2,
            "text": f"{Colors.RED}กระดูกแหลกเป็นผุยผง!{Colors.END}"
        }
    ]
    
    effect = random.choice(effects)
    
    # ถ้ามีข้อมูลมอนสเตอร์พิเศษ
    if monster_data and "gore_texts" in monster_data:
        gore_text = random.choice(monster_data["gore_texts"]["crit_hit"])
        print(f"{Colors.RED}{gore_text}{Colors.END}")
    elif monster_data and "nsfw_texts" in monster_data:
        nsfw_text = random.choice(monster_data["nsfw_texts"]["crit_hit"])
        print(f"{Colors.PURPLE}{nsfw_text}{Colors.END}")
    else:
        print(effect["text"])
    
    return effect["damage_multiplier"]

def critical_fail_effect(attacker, defender, monster_data=None):
    """เอฟเฟกต์เมื่อทอยได้ 1 (Critical Fail)"""
    fails = [
        {
            "name": "อาวุธหัก",
            "description": "อาวุธหักระหว่างต่อสู้",
            "damage_to_self": 5,
            "text": f"{Colors.RED}อาวุธหัก! เศษอาวุธบินกลับมาทิ่มตัวเอง{Colors.END}"
        },
        {
            "name": "หกล้ม",
            "description": "หกล้มและได้บาดเจ็บ",
            "damage_to_self": 3,
            "status": "stunned",
            "text": f"{Colors.RED}หกล้มหัวฟาดพื้น! โลกหมุน{Colors.END}"
        },
        {
            "name": "โจมตีพลาดหนัก",
            "description": "โจมตีพลาดและเปิดช่องโหว่",
            "damage_to_self": 0,
            "next_enemy_bonus": 2,
            "text": f"{Colors.RED}เปิดช่องโหว่ให้ศัตรู!{Colors.END}"
        }
    ]
    
    fail = random.choice(fails)
    
    # ถ้ามีข้อมูลมอนสเตอร์พิเศษ
    if monster_data and "gore_texts" in monster_data:
        gore_text = random.choice(monster_data["gore_texts"]["crit_fail"])
        print(f"{Colors.RED}{gore_text}{Colors.END}")
    elif monster_data and "nsfw_texts" in monster_data:
        nsfw_text = random.choice(monster_data["nsfw_texts"]["crit_fail"])
        print(f"{Colors.PURPLE}{nsfw_text}{Colors.END}")
    else:
        print(fail["text"])
    
    # สร้างความเสียหายให้ตัวเอง
    if fail.get("damage_to_self", 0) > 0:
        attacker.take_damage(fail["damage_to_self"])
    
    # เพิ่มสถานะผิดปกติ
    if fail.get("status"):
        attacker.status_effects.append(fail["status"])
    
    return fail.get("next_enemy_bonus", 1)

def combat_turn(player, monster, monster_data):
    """เทิร์นการต่อสู้"""
    print_separator()
    print(f"{Colors.BOLD}HP คุณ: {player.hp}/{player.max_hp} | HP {monster['name']}: {monster['hp']}{Colors.END}")
    
    # ตัวเลือกการกระทำ
    actions = [
        ("1", "โจมตี", "attack"),
        ("2", "ใช้สกิลพิเศษ", "skill"),
        ("3", "ใช้ไอเทม", "item"),
        ("4", "ตั้งรับ", "defend"),
        ("5", "วิ่งหนี", "flee")
    ]
    
    print(f"\n{Colors.CYAN}เลือกการกระทำ:{Colors.END}")
    for action_id, action_name, _ in actions:
        print(f"{action_id}. {action_name}")
    
    choice = input("เลือกการกระทำ: ")
    
    player_damage = 0
    enemy_damage_bonus = 1
    
    if choice == "1":  # โจมตีพื้นฐาน
        print(f"\n{Colors.YELLOW}คุณทอยเต๋า d20 เพื่อโจมตี...{Colors.END}")
        time.sleep(1)
        
        attack_roll = roll_dice(20)
        print(f"ทอยได้: {attack_roll}")
        
        if attack_roll == 20:  # Critical Success
            print(f"{Colors.GREEN} CRITICAL SUCCESS! {Colors.END}")
            multiplier = critical_success_effect(player, monster, monster_data)
            damage = roll_dice(player.base_damage) * multiplier
            player_damage = int(damage)
            
        elif attack_roll == 1:  # Critical Fail
            print(f"{Colors.RED} CRITICAL FAILURE! {Colors.END}")
            enemy_damage_bonus = critical_fail_effect(player, monster, monster_data)
            player_damage = 0
            
        elif attack_roll >= 10:  #โจมตีปกติ
            damage = roll_dice(player.base_damage)
            hits = [
                f"คุณฟันบ่าศัตรูเลือดสาด",
                f"คุณแทงท้องศัตรูทะลุหลังบางส่วน",
                f"คุณทุบเข่าศัตรูเสียงดังกร๊อบ"
            ]
            print(f"{Colors.GREEN}โจมตีสำเร็จ! {random.choice(hits)}{Colors.END}")
            player_damage = damage
            
        else:  # โจมตีพลาด
            misses = [
                f"ศัตรูหลบได้อย่างฉิวเฉียด",
                f"อาวุธของคุณสะท้อนกับเกราะ",
                f"คุณพลาดเป้าหมายไปไกล"
            ]
            print(f"{Colors.RED}โจมตีพลาด! {random.choice(misses)}{Colors.END}")
            player_damage = 0
    
    elif choice == "2":  # ใช้สกิลพิเศษ
        skills = {
            "warrior": ("ฟันรุนแรง", "โจมตีแรงเป็นสองเท่า แต่เสี่ยงพลาดสูง", 2, 15),
            "rogue": ("แทงข้างหลัง", "โจมตีเพิ่มความเสียหายหากศัตรูเผลอ", 1.5, 12),
            "mage": ("ไฟร์บอล", "ลูกไฟทำความเสียหายเวท", 3, 10),
            "necromancer": ("ดูดเลือด", "ดูด HP ศัตรูมาฟื้นฟูตัวเอง", 1, 8)
        }
        
        skill_name, skill_desc, multiplier, required_roll = skills[player.char_class]
        print(f"\n{Colors.PURPLE}ใช้สกิล: {skill_name}{Colors.END}")
        print(f"{skill_desc}")
        
        skill_roll = roll_dice(20)
        print(f"ทอยเต๋าสกิลได้: {skill_roll}")
        
        if skill_roll >= required_roll:
            damage = roll_dice(player.base_damage) * multiplier
            player_damage = int(damage)
            
            skill_success = [
                f"สกิลสำเร็จอย่างงดงาม!",
                f"พลังอันตรายพุ่งเข้าหาศัตรู!",
                f"ศัตรูไม่สามารถต้านทานได้!"
            ]
            print(f"{Colors.GREEN}{random.choice(skill_success)}{Colors.END}")
        else:
            print(f"{Colors.RED}สกิลล้มเหลว!{Colors.END}")
            player_damage = 0
    
    elif choice == "3":  # ใช้ไอเทม
        if player.inventory:
            print(f"\n{Colors.CYAN}ไอเทมในกระเป๋า:{Colors.END}")
            for i, item in enumerate(player.inventory, 1):
                print(f"{i}. {item}")
            
            item_choice = input("เลือกไอเทมที่จะใช้ (หรือกด 0 เพื่อยกเลิก): ")
            if item_choice:
                idx = int(item_choice) - 1
                if 0 <= idx < len(player.inventory):
                    used_item = player.inventory.pop(idx)
                    print(f"ใช้ {used_item}!")
                    
                    if "potion" in used_item:
                        heal_amount = random.randint(15, 25)
                        player.heal(heal_amount)
                    elif "dagger" in used_item:
                        player_damage = roll_dice(6) + 2
                        print(f"ใช้มีดสั้นโจมตีเพิ่ม!")
        else:
            print(f"{Colors.RED}ไม่มีไอเทม!{Colors.END}")
    
    elif choice == "4":  # ตั้งรับ
        print(f"{Colors.BLUE}คุณตั้งท่าป้องกัน...{Colors.END}")
        player.armor += 3
        return 0, 1  # ไม่โจมตี, โบนัสศัตรูปกติ
    
    elif choice == "5":  # วิ่งหนี
        flee_roll = roll_dice(20)
        if flee_roll > 12:
            print(f"{Colors.GREEN}คุณหนีรอดได้!{Colors.END}")
            return "flee", 1
        else:
            print(f"{Colors.RED}คุณหนีไม่รอด!{Colors.END}")
            # ศัตรูได้โบนัสเมื่อคุณพยายามหนี
            return 0, 1.5
    
    # ศัตรูโจมตีกลับ (ถ้าผู้เล่นไม่ได้หนี)
    if choice != "5" or (choice == "5" and player_damage == 0):
        print(f"\n{Colors.RED}>>> {monster['name']} โจมตีกลับ! <<<{Colors.END}")
        time.sleep(1)
        
        enemy_attack = roll_dice(20)
        
        if enemy_attack == 20:  # ศัตรู Critical Success
            print(f"{Colors.RED} ศัตรู CRITICAL SUCCESS! {Colors.END}")
            
            # คำอธิบาย Critical Success ของศัตรู
            crits = [
                f"{monster['name']} ฉีกแขนคุณจนเกือบขาด!",
                f"{monster['name']} กัดคอคุณเลือดพ่น!",
                f"{monster['name']} ทุบหน้าอกคุณจนกระดูกหัก!"
            ]
            print(random.choice(crits))
            
            enemy_damage = roll_dice(monster['max_dmg'], monster['min_dmg']) * 2
            enemy_damage *= enemy_damage_bonus
            
        elif enemy_attack == 1:  # ศัตรู Critical Fail
            print(f"{Colors.GREEN} ศัตรู CRITICAL FAILURE! {Colors.END}")
            
            fails = [
                f"{monster['name']} ลื่นบนเลือดตัวเองล้ม!",
                f"{monster['name']} โจมตีพลาดจนอาวุธหัก!",
                f"{monster['name']} เตะโดนอะไรแข็งจนนิ้วเท้าหัก!"
            ]
            print(random.choice(fails))
            
            enemy_damage = 0
            # ศัตรูทำร้ายตัวเอง
            self_damage = roll_dice(3)
            monster['hp'] -= self_damage
            print(f"{monster['name']} ทำร้ายตัวเอง {self_damage} หน่วย!")
            
        elif enemy_attack >= 8:  # ศัตรูโจมตีสำเร็จปกติ
            enemy_damage = roll_dice(monster['max_dmg'] - monster['min_dmg'] + 1, monster['min_dmg'] - 1)
            enemy_damage *= enemy_damage_bonus
            
            hits = [
                f"{monster['name']} โจมตีโดนคุณ!",
                f"{monster['name']} ข่วนคุณเลือดออก!",
                f"{monster['name']} ต่อยคุณจนเลือดกำเดาไหล!"
            ]
            print(random.choice(hits))
            
        else:  # ศัตรูโจมตีพลาด
            print(f"{Colors.GREEN}{monster['name']} โจมตีพลาด!{Colors.END}")
            enemy_damage = 0
        
        # ลดเกราะที่เพิ่มจากตั้งรับ
        if choice == "4":
            player.armor -= 3
        
        # ศัตรูสร้างความเสียหาย
        if enemy_damage > 0:
            player.take_damage(int(enemy_damage))
    
    return player_damage, enemy_damage_bonus

def random_encounter():
    """สุ่มการเผชิญหน้ากับมอนสเตอร์"""
    monsters, _ = load_data()
    monster_list = list(monsters.values())
    monster = random.choice(monster_list)
    
    # สร้าง instance ของมอนสเตอร์
    monster_instance = {
        'name': monster['name'],
        'hp': monster['hp'],
        'min_dmg': monster['min_dmg'],
        'max_dmg': monster['max_dmg'],
        'description': monster['description']
    }
    
    return monster_instance, monster

def shop(player):
    """ร้านค้า"""
    clear_screen()
    print(f"{Colors.YELLOW}=== ร้านค้าผิดกฎหมาย ==={Colors.END}")
    print("เจ้าของร้านตาเดียวมองคุณด้วยความสงสัย...")
    
    items_for_sale = [
        ("น้ำยาบำบัดดำ", "ฟื้นฟู 25-40 HP (อาจมีผลข้างเคียง)", 30),
        ("ดาบสาป", "โจมตี +7 (สาปให้เลือดไหลไม่หยุด)", 75),
        ("เกราะหนังมนุษย์", "ป้องกัน +5 (ส่งเสียงร้องตอนโดนโจมตี)", 100),
        ("ยาเพิ่มพลัง", "เพิ่มความเสียหาย 2 เท่า 3 เทิร์น (หัวใจวายเสี่ยง 20%)", 50),
        ("เครื่องสั่นประหลาด", "ทำให้ศัตรูสับสน 2 เทิร์น", 40)
    ]
    
    print(f"\n{Colors.CYAN}ทองของคุณ: {player.gold} GP{Colors.END}")
    print_separator()
    
    for i, (name, desc, price) in enumerate(items_for_sale, 1):
        print(f"{i}. {name} - {price} GP")
        print(f"   {desc}")
    
    print(f"\n{len(items_for_sale)+1}. ออกจากร้าน")
    
    while True:
        choice = input("\nเลือกสินค้า: ")
        
        if choice == str(len(items_for_sale)+1):
            break
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(items_for_sale):
                item_name, _, price = items_for_sale[idx]
                
                if player.gold >= price:
                    player.gold -= price
                    player.inventory.append(item_name)
                    print(f"{Colors.GREEN}ซื้อ {item_name} สำเร็จ!{Colors.END}")
                else:
                    print(f"{Colors.RED}ทองไม่พอ!{Colors.END}")
        except:
            print(f"{Colors.RED}ตัวเลือกไม่ถูกต้อง!{Colors.END}")
        
        print(f"ทองคงเหลือ: {player.gold} GP")

def main():
    """ฟังก์ชันหลักของเกม"""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.PURPLE}=== CLI DUNGEONS - UNCUT EDITION ==={Colors.END}")
    print("เกมนี้มีเนื้อหาทางเพศและความรุนแรง")
    print("เล่นต่อหมายความว่ายอมรับเนื้อหาทั้งหมด")
    print_separator()
    
    consent = input("ยอมรับข้อตกลง? (Y/n): ").lower()
    if consent != 'y':
        print("ออกจากเกม")
        return
    
    # สร้างหรือโหลดตัวละคร
    print("\n1. สร้างตัวละครใหม่")
    print("2. โหลดตัวละคร")
    print("3. ออกจากเกม")
    
    start_choice = input("เลือก: ")
    
    if start_choice == "1":
        player = create_character()
        enemies_defeated = 0 
    elif start_choice == "2":
        player, enemies_defeated = load_game()
    if player is None:  # ถ้าโหลดไม่สำเร็จ
        player = create_character()
        enemies_defeated = 0
    elif start_choice == "3":
        return
    else:
        print("เริ่มเกมใหม่")
        player = create_character()
        enemies_defeated = 0

    # เริ่มเกมหลัก
    game_active = True
    enemies_defeated = 0
    
    while game_active and player.hp > 0:
        clear_screen()
        print(f"{Colors.BOLD}=== การผจญภัย ==={Colors.END}")
        print(f"ศัตรูที่กำจัดแล้ว: {enemies_defeated}")
        player.show_stats()
        
        print_separator()
        print("เลือกการกระทำ:")
        print("1. สำรวจดันเจี้ยน")
        print("2. หาร้านค้า")
        print("3. พักผ่อน (ฟื้นฟู HP)")
        print("4. บันทึกเกม")
        print("5. ออกจากเกม")
        
        choice = input("เลือก: ")
        
        if choice == "1":  # สำรวจดันเจี้ยน
            clear_screen()
            print(f"{Colors.YELLOW}คุณเดินลึกลงไปในดันเจี้ยน...{Colors.END}")
            time.sleep(1)
            
            encounter_roll = roll_dice(20)
            
            if encounter_roll <= 15:  # เผชิญหน้ามอนสเตอร์
                monster_instance, monster_data = random_encounter()
                print(f"\n{Colors.RED}  เผชิญหน้ากับ {monster_instance['name']}! {Colors.END}")
                print(f"{monster_instance['description']}")
                
                # แสดงข้อความพิเศษของมอนสเตอร์บางชนิด
                if monster_instance['name'] == "ซักคิวบัส" and "nsfw_texts" in monster_data:
                    special_text = random.choice(monster_data["nsfw_texts"]["special"])
                    print(f"\n{Colors.PURPLE}{special_text}{Colors.END}")
                
                input(f"\n{Colors.YELLOW}กด Enter เพื่อเริ่มการต่อสู้...{Colors.END}")
                
                # การต่อสู้
                while monster_instance['hp'] > 0 and player.hp > 0:
                    player_damage, _ = combat_turn(player, monster_instance, monster_data)
                    
                    if player_damage == "flee":
                        break
                    
                    # ผู้เล่นสร้างความเสียหายให้มอนสเตอร์
                    if player_damage > 0:
                        monster_instance['hp'] -= player_damage
                        print(f"{Colors.GREEN}สร้างความเสียหาย {player_damage} หน่วยให้ {monster_instance['name']}!{Colors.END}")
                    
                    # เช็คสถานะมอนสเตอร์
                    if monster_instance['hp'] <= 0:
                        print(f"\n{Colors.GREEN}✨ คุณสังหาร {monster_instance['name']} ได้! ✨{Colors.END}")
                        
                        # รางวัล
                        exp_gain = monster_instance['max_dmg'] * 5
                        gold_gain = random.randint(10, 30)
                        
                        player.exp += exp_gain
                        player.gold += gold_gain
                        enemies_defeated += 1
                        
                        print(f"ได้รับ {exp_gain} EXP และ {gold_gain} GP")
                        
                        # เลเวลอัพ
                        if player.exp >= player.level * 100:
                            player.level += 1
                            player.max_hp += 10
                            player.hp = player.max_hp
                            player.base_damage += 2
                            print(f"{Colors.CYAN}✨ ระดับขึ้น! ตอนนี้ระดับ {player.level} ✨{Colors.END}")
                        
                        # โอกาสได้ไอเทม
                        if roll_dice(20) > 15:
                            loot_items = ["น้ำยาบำบัด", "มีดสั้น", "แหวนพิศวง"]
                            loot = random.choice(loot_items)
                            player.inventory.append(loot)
                            print(f"พบไอเทม: {loot}")
                        
                        input(f"\n{Colors.YELLOW}กด Enter เพื่อดำเนินการต่อ...{Colors.END}")
                        break
                    
                    if player.hp <= 0:
                        break
                    
                    input(f"\n{Colors.YELLOW}กด Enter สำหรับเทิร์นต่อไป...{Colors.END}")
            
            elif encounter_roll <= 18:  # พบสมบัติ
                print(f"\n{Colors.YELLOW}💰 คุณพบหีบสมบัติ! 💰{Colors.END}")
                
                treasure_type = random.choice(["gold", "item", "both"])
                
                if treasure_type in ["gold", "both"]:
                    gold_found = random.randint(20, 60)
                    player.gold += gold_found
                    print(f"พบทอง {gold_found} GP!")
                
                if treasure_type in ["item", "both"]:
                    treasures = ["น้ำยาลึกลับ", "กุญแจพิศวง", "แผนที่สมบัติ", "กระดูกศักดิ์สิทธิ์"]
                    treasure = random.choice(treasures)
                    player.inventory.append(treasure)
                    print(f"พบไอเทม: {treasure}")
                
                input(f"\n{Colors.YELLOW}กด Enter เพื่อดำเนินการต่อ...{Colors.END}")
            
            else:  # ไม่พบอะไร
                print(f"\n{Colors.WHITE}คุณเดินทางมาทั้งวันแต่ไม่พบอะไรน่าสนใจ...{Colors.END}")
                input(f"\n{Colors.YELLOW}กด Enter เพื่อดำเนินการต่อ...{Colors.END}")
        
        elif choice == "2":  # ร้านค้า
            shop(player)
        
        elif choice == "3":  # พักผ่อน
            clear_screen()
            print(f"{Colors.BLUE}คุณพักผ่อนในที่ปลอดภัย...{Colors.END}")
            
            heal_amount = min(15, player.max_hp - player.hp)
            if heal_amount > 0:
                player.heal(heal_amount)
                
                # โอกาสถูกโจมตีขณะพักผ่อน
                if roll_dice(20) == 1:
                    print(f"\n{Colors.RED}⚠️  คุณถูกโจมตีขณะนอนหลับ! {Colors.END}")
                    surprise_damage = roll_dice(6)
                    player.take_damage(surprise_damage)
            else:
                print("คุณรู้สึกสดชื่นอยู่แล้ว")
            
            input(f"\n{Colors.YELLOW}กด Enter เพื่อดำเนินการต่อ...{Colors.END}")
        
        elif choice == "5":  # ออกเกม
            print(f"\n{Colors.CYAN}ขอบคุณที่เล่นเกม!{Colors.END}")
            print(f"คุณกำจัดศัตรูได้ {enemies_defeated} ตัว")
            print(f"ระดับสุดท้าย: {player.level}")
            game_active = False
    
    # Game Over
    if player.hp <= 0:
        clear_screen()
        print(f"{Colors.RED}{'='*50}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD} GAME OVER {Colors.END}")
        print(f"{Colors.RED}{'='*50}{Colors.END}")
        
        death_scenes = [
            "ร่างกายคุณเริ่มเย็นลง... โลกมืดค่อย ๆ มืด... เสียงสุดท้ายที่ได้ยินคือเสียงหัวใจตัวเอง",
            "เลือดไหลไม่หยุด... คุณรู้สึกตัวลอยขึ้น เห็นร่างตัวเองนอนอยู่ด้านล่าง",
            "ศัตรูกวาดตาคุณครั้งสุดท้ายก่อนที่ทุกอย่างจะดับสูญ",
            "คุณสำลักเลือดตัวเอง... หายใจไม่ออก..."
        ]
        
        print(f"\n{random.choice(death_scenes)}")
        print(f"\n{Colors.YELLOW}สถิติสุดท้าย:{Colors.END}")
        print(f"ระดับ: {player.level}")
        print(f"ศัตรูที่กำจัด: {enemies_defeated}")
        print(f"ทองที่เก็บได้: {player.gold} GP")

if __name__ == "__main__":
    main()
