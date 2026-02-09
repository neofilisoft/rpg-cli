// witcher.cpp - The Witcher RPG (C++ Version)
// Compile: g++ -std=c++17 witcher.cpp -o witcher
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <random>
#include <ctime>
#include <algorithm>
#include <cstdlib>
#include <sstream>
#include <iomanip>
#include <memory>
#include <limits>

#ifdef _WIN32
#include <windows.h>
#endif

// ===== Color Codes for Cross-Platform =====
class Colors {
public:
    static const std::string RED;
    static const std::string GREEN;
    static const std::string YELLOW;
    static const std::string BLUE;
    static const std::string PURPLE;
    static const std::string CYAN;
    static const std::string WHITE;
    static const std::string BOLD;
    static const std::string ORANGE;
    static const std::string END;
    
    static void init() {
        #ifdef _WIN32
        HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
        // Enable VT100 escape codes on Windows 10+
        DWORD mode = 0;
        GetConsoleMode(hConsole, &mode);
        SetConsoleMode(hConsole, mode | ENABLE_VIRTUAL_TERMINAL_PROCESSING);
        #endif
    }
};

// ANSI Color Codes
const std::string Colors::RED = "\033[91m";
const std::string Colors::GREEN = "\033[92m";
const std::string Colors::YELLOW = "\033[93m";
const std::string Colors::BLUE = "\033[94m";
const std::string Colors::PURPLE = "\033[95m";
const std::string Colors::CYAN = "\033[96m";
const std::string Colors::WHITE = "\033[97m";
const std::string Colors::BOLD = "\033[1m";
const std::string Colors::ORANGE = "\033[38;5;208m";
const std::string Colors::END = "\033[0m";

// ===== Utility Functions =====
void clearScreen() {
    #ifdef _WIN32
    system("cls");
    #else
    system("clear");
    #endif
}

void printSeparator() {
    std::cout << Colors::WHITE << std::string(60, '=') << Colors::END << std::endl;
}

int rollDice(int minVal, int maxVal) {
    static std::random_device rd;
    static std::mt19937 gen(rd());
    std::uniform_int_distribution<> dist(minVal, maxVal);
    return dist(gen);
}

void waitForEnter() {
    std::cout << "Press Enter to continue...";
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    std::cin.get();
}

// ===== Game Data Structures =====
struct DifficultySettings {
    double enemyHpMult;
    double enemyDmgMult;
    double expMult;
    double goldMult;
};

struct Skill {
    std::string description;
    int cost;
    std::string type;
};

struct Monster {
    std::string name;
    int hp;
    int minDmg;
    int maxDmg;
    std::string type;
    std::string weakness;
    std::string loot;
    int exp;
    std::string ai;
};

// ===== Global Game Data =====
std::map<std::string, DifficultySettings> DIFFICULTY_SETTINGS = {
    {"Just the Story", {0.8, 0.7, 1.2, 1.0}},
    {"Story and Swords", {1.0, 1.0, 1.0, 1.0}},
    {"Blood and Broken Bones", {1.2, 1.3, 0.8, 1.2}},
    {"Death March!", {1.5, 1.6, 0.6, 1.5}}
};

std::map<std::string, Skill> SKILL_TREE = {
    {"Muscle Memory", {"Increase light attack damage +20%", 1, "Combat"}},
    {"Strength Training", {"Increase strong attack damage +20%", 1, "Combat"}},
    {"Far-Reaching Aard", {"Aard deals more damage", 1, "Signs"}},
    {"Melt Armor", {"Igni reduces enemy defense", 1, "Signs"}},
    {"Delusion", {"Axii has higher chance to stun enemy", 1, "Signs"}},
    {"Heightened Tolerance", {"Potions heal more", 1, "Alchemy"}}
};

std::map<std::string, Monster> getMonsters(bool conjunctionActive = false) {
    std::map<std::string, Monster> monsters = {
        {"drowner", {"Drowner", 40, 5, 10, "Necrophage", "Igni", "Drowner Brain", 25, "Aggressive"}},
        {"ghoul", {"Ghoul", 50, 6, 12, "Necrophage", "Silver", "Ghoul Blood", 30, "Aggressive"}},
        {"bandit", {"Bandit", 60, 8, 15, "Human", "Axii", "Oren Pouch", 40, "Balanced"}},
        {"bear", {"Grizzly Bear", 120, 12, 22, "Beast", "Quen", "Bear Fat", 70, "Tank"}},
        {"fiend", {"Fiend", 250, 20, 35, "Relict", "Samum", "Fiend Eye", 150, "Smart"}}
    };
    
    if (conjunctionActive) {
        for (auto& pair : monsters) {
            pair.second.hp = static_cast<int>(pair.second.hp * 1.5);
            pair.second.name = "Chaos " + pair.second.name;
        }
    }
    return monsters;
}

// ===== Enemy AI System =====
class EnemyAI {
private:
    std::string behaviorType;
    
public:
    EnemyAI(const std::string& type) : behaviorType(type) {}
    
    std::string decideAction(double hpPercent) {
        if (behaviorType == "Aggressive") return "Attack";
        if (behaviorType == "Tank") return (hpPercent < 30) ? "Defend" : "Attack";
        if (behaviorType == "Smart") {
            if (hpPercent < 25) return "Heal";
            return (rollDice(1, 100) > 50) ? "Attack" : "Special";
        }
        if (behaviorType == "Balanced") {
            return (rollDice(1, 100) > 30) ? "Attack" : "Defend";
        }
        return "Attack";
    }
};

// ===== Witcher Class =====
class Witcher {
private:
    void applySchoolBonus() {
        if (school == "Wolf") {
            maxHp = 110;
            baseDmg = 12;
        } else if (school == "Griffin") {
            signPower = 3;
        } else if (school == "Bear") {
            maxHp = 160;
            defense = 5;
            baseDmg = 14;
        } else if (school == "Cat") {
            baseDmg = 15;
            critChance = 15;
        }
        hp = maxHp;
    }
    
public:
    std::string name;
    std::string school;
    std::string difficulty;
    int level;
    int exp;
    int skillPoints;
    int gold;
    std::vector<std::string> inventory;
    std::map<std::string, bool> skillsLearned;
    int tempBuff;
    int ngPlus;
    
    // Stats
    int maxHp;
    int hp;
    int baseDmg;
    int defense;
    int signPower;
    int critChance;
    std::string equippedSword;
    std::string equippedArmor;
    
    // Constructors
    Witcher(const std::string& n, const std::string& s, const std::string& diff = "Story and Swords")
        : name(n), school(s), difficulty(diff), level(1), exp(0), skillPoints(0), gold(100),
          tempBuff(0), ngPlus(0), maxHp(100), hp(100), baseDmg(10), defense(0),
          signPower(1), critChance(5), equippedSword("Witcher Silver Sword"),
          equippedArmor("Leather Jacket") {
        
        inventory = {"Bread", "Dwarven Spirit"};
        
        // Initialize skills
        for (const auto& skill : SKILL_TREE) {
            skillsLearned[skill.first] = false;
        }
        
        applySchoolBonus();
    }
    
    // Level up system
    void gainExp(int amount) {
        double mult = DIFFICULTY_SETTINGS[difficulty].expMult;
        int actualExp = static_cast<int>(amount * mult);
        exp += actualExp;
        std::cout << "Gained " << actualExp << " XP" << std::endl;
        
        if (exp >= 100) {
            levelUp();
        }
    }
    
    void levelUp() {
        level++;
        exp = 0;
        skillPoints++;
        maxHp += 15;
        baseDmg += 2;
        hp = maxHp;
        std::cout << Colors::YELLOW << "\n*** LEVEL UP! Rank " << level 
                  << " (Gained 1 Skill Point) ***" << Colors::END << std::endl;
    }
    
    // Save/Load helpers
    std::map<std::string, std::string> toMap() const {
        std::map<std::string, std::string> data;
        data["name"] = name;
        data["school"] = school;
        data["difficulty"] = difficulty;
        data["level"] = std::to_string(level);
        data["exp"] = std::to_string(exp);
        data["skill_points"] = std::to_string(skillPoints);
        data["gold"] = std::to_string(gold);
        data["max_hp"] = std::to_string(maxHp);
        data["base_dmg"] = std::to_string(baseDmg);
        data["defense"] = std::to_string(defense);
        data["sign_power"] = std::to_string(signPower);
        data["crit_chance"] = std::to_string(critChance);
        data["equipped_sword"] = equippedSword;
        data["equipped_armor"] = equippedArmor;
        data["temp_buff"] = std::to_string(tempBuff);
        data["ng_plus"] = std::to_string(ngPlus);
        
        // Serialize inventory
        std::string invStr;
        for (size_t i = 0; i < inventory.size(); i++) {
            invStr += inventory[i];
            if (i != inventory.size() - 1) invStr += "|";
        }
        data["inventory"] = invStr;
        
        // Serialize skills
        std::string skillsStr;
        for (const auto& skill : skillsLearned) {
            skillsStr += skill.first + ":" + (skill.second ? "1" : "0");
            skillsStr += ";";
        }
        data["skills_learned"] = skillsStr;
        
        return data;
    }
    
    static Witcher fromMap(const std::map<std::string, std::string>& data) {
        Witcher witcher(data.at("name"), data.at("school"), data.at("difficulty"));
        
        witcher.level = std::stoi(data.at("level"));
        witcher.exp = std::stoi(data.at("exp"));
        witcher.skillPoints = std::stoi(data.at("skill_points"));
        witcher.gold = std::stoi(data.at("gold"));
        witcher.maxHp = std::stoi(data.at("max_hp"));
        witcher.baseDmg = std::stoi(data.at("base_dmg"));
        witcher.defense = std::stoi(data.at("defense"));
        witcher.signPower = std::stoi(data.at("sign_power"));
        witcher.critChance = std::stoi(data.at("crit_chance"));
        witcher.equippedSword = data.at("equipped_sword");
        witcher.equippedArmor = data.at("equipped_armor");
        witcher.tempBuff = std::stoi(data.at("temp_buff"));
        witcher.ngPlus = std::stoi(data.at("ng_plus"));
        witcher.hp = witcher.maxHp;
        
        // Deserialize inventory
        std::string invStr = data.at("inventory");
        if (!invStr.empty()) {
            std::stringstream ss(invStr);
            std::string item;
            while (std::getline(ss, item, '|')) {
                if (!item.empty()) witcher.inventory.push_back(item);
            }
        }
        
        // Deserialize skills
        std::string skillsStr = data.at("skills_learned");
        if (!skillsStr.empty()) {
            std::stringstream ss(skillsStr);
            std::string pair;
            while (std::getline(ss, pair, ';')) {
                size_t colon = pair.find(':');
                if (colon != std::string::npos) {
                    std::string skillName = pair.substr(0, colon);
                    bool learned = (pair.substr(colon + 1) == "1");
                    witcher.skillsLearned[skillName] = learned;
                    
                    // Apply passive effects
                    if (learned) {
                        if (skillName == "Muscle Memory") witcher.baseDmg += 3;
                        if (skillName == "Strength Training") witcher.baseDmg += 5;
                    }
                }
            }
        }
        
        // Ensure all skills exist
        for (const auto& skill : SKILL_TREE) {
            if (witcher.skillsLearned.find(skill.first) == witcher.skillsLearned.end()) {
                witcher.skillsLearned[skill.first] = false;
            }
        }
        
        return witcher;
    }
    
    // Display status
    void displayStatus() const {
        printSeparator();
        std::cout << Colors::BOLD << Colors::CYAN << name << " (" << school << " School)" 
                  << Colors::END << std::endl;
        std::cout << "Level: " << level << " | HP: " << hp << "/" << maxHp 
                  << " | Gold: " << gold << std::endl;
        std::cout << "Damage: " << baseDmg << " | Defense: " << defense 
                  << " | Sign Power: " << signPower << std::endl;
        std::cout << "Skill Points: " << skillPoints << " | NG+: " << ngPlus << std::endl;
        printSeparator();
    }
};

// ===== Game Systems =====
class GameManager {
private:
    static const std::string SAVE_FILE;
    
    static std::vector<std::string> getMonsterKeys() {
        auto monsters = getMonsters();
        std::vector<std::string> keys;
        for (const auto& pair : monsters) {
            keys.push_back(pair.first);
        }
        return keys;
    }
    
public:
    // Skill Tree Menu
    static void skillTreeMenu(Witcher& player) {
        while (true) {
            clearScreen();
            std::cout << Colors::PURPLE << "--- SKILL TREE (Points: " 
                      << player.skillPoints << ") ---" << Colors::END << std::endl;
            
            std::vector<std::string> skills;
            for (const auto& pair : SKILL_TREE) {
                skills.push_back(pair.first);
            }
            
            for (size_t i = 0; i < skills.size(); i++) {
                const auto& skillName = skills[i];
                const auto& skill = SKILL_TREE.at(skillName);
                std::string status = player.skillsLearned.at(skillName) 
                    ? Colors::GREEN + "[Learned]" + Colors::END 
                    : "[Cost: " + std::to_string(skill.cost) + "]";
                
                std::cout << (i + 1) << ". " << skillName << " (" << skill.type << ") - " 
                          << status << std::endl;
                std::cout << "   > " << skill.description << std::endl;
            }
            
            std::cout << (skills.size() + 1) << ". Back" << std::endl;
            
            std::string choice;
            std::cout << "Select skill to learn: ";
            std::getline(std::cin, choice);
            
            if (choice.empty()) continue;
            
            try {
                int idx = std::stoi(choice) - 1;
                
                if (idx == static_cast<int>(skills.size())) break;
                
                if (idx >= 0 && idx < static_cast<int>(skills.size())) {
                    std::string skillName = skills[idx];
                    
                    if (player.skillsLearned.at(skillName)) {
                        std::cout << "You already learned this skill!" << std::endl;
                    } else if (player.skillPoints >= SKILL_TREE.at(skillName).cost) {
                        player.skillPoints -= SKILL_TREE.at(skillName).cost;
                        player.skillsLearned[skillName] = true;
                        
                        // Apply passive effects
                        if (skillName == "Muscle Memory") player.baseDmg += 3;
                        if (skillName == "Strength Training") player.baseDmg += 5;
                        
                        std::cout << "Learned " << skillName << " successfully!" << std::endl;
                    } else {
                        std::cout << "Not enough Skill Points!" << std::endl;
                    }
                    waitForEnter();
                }
            } catch (...) {
              
            }
        }
    }
    
    // Combat System
    static bool combat(Witcher& player, const std::string& monsterKey, bool conjunctionActive = false) {
        auto monsters = getMonsters(conjunctionActive);
        Monster monster = monsters[monsterKey];
        
        // Apply difficulty and NG+ scaling
        DifficultySettings diff = DIFFICULTY_SETTINGS[player.difficulty];
        double ngMult = 1.0 + (player.ngPlus * 0.5);
        
        monster.hp = static_cast<int>(monster.hp * diff.enemyHpMult * ngMult) + (player.level * 10);
        monster.minDmg = static_cast<int>(monster.minDmg * diff.enemyDmgMult) + player.ngPlus * 2;
        monster.maxDmg = static_cast<int>(monster.maxDmg * diff.enemyDmgMult) + player.ngPlus * 5;
        
        if (player.ngPlus > 0) {
            monster.name = Colors::RED + "[NG+" + std::to_string(player.ngPlus) + "]" 
                         + Colors::END + " " + monster.name;
        }
        
        int enemyHp = monster.hp;
        EnemyAI ai(monster.ai);
        
        printSeparator();
        std::cout << "Witcher encounters: " << monster.name << std::endl;
        
        while (player.hp > 0 && enemyHp > 0) {
            std::cout << "\n" << player.name << ": " << player.hp << "/" << player.maxHp 
                      << " HP | " << monster.name << ": " << enemyHp << " HP" << std::endl;
            std::cout << "1. Fast Attack  2. Strong Attack  3. Sign  4. Item  5. Defend" << std::endl;
            
            std::string choice;
            std::cout << "Choose action: ";
            std::getline(std::cin, choice);
            
            int dmg = 0;
            bool playerDefending = false;
            
            if (choice == "1") { // Fast Attack
                dmg = player.baseDmg + player.tempBuff + rollDice(1, 4);
                if (player.skillsLearned.at("Muscle Memory")) {
                    dmg = static_cast<int>(dmg * 1.2);
                }
                std::cout << "You deal " << dmg << " damage!" << std::endl;
                
            } else if (choice == "2") { // Strong Attack
                if (rollDice(1, 10) > 3) {
                    dmg = static_cast<int>((player.baseDmg + player.tempBuff) * 1.5) + rollDice(1, 8);
                    if (player.skillsLearned.at("Strength Training")) {
                        dmg = static_cast<int>(dmg * 1.2);
                    }
                    std::cout << "You deal " << dmg << " damage!" << std::endl;
                } else {
                    std::cout << "Strong attack missed!" << std::endl;
                }
                
            } else if (choice == "3") { // Sign
                std::cout << "Choose Sign: 1.Aard 2.Igni 3.Quen 4.Axii 5.Yrden" << std::endl;
                std::string signChoice;
                std::getline(std::cin, signChoice);
                
                if (signChoice == "1") { // Aard
                    dmg = 10 * player.signPower;
                    if (player.skillsLearned.at("Far-Reaching Aard")) {
                        dmg *= 1.5;
                    }
                    std::cout << "Used Aard for " << dmg << " damage!" << std::endl;
                    
                } else if (signChoice == "2") { // Igni
                    dmg = 15 * player.signPower;
                    if (player.skillsLearned.at("Melt Armor")) {
                        monster.minDmg = std::max(1, monster.minDmg - 3);
                        monster.maxDmg = std::max(2, monster.maxDmg - 5);
                    }
                    std::cout << "Used Igni for " << dmg << " damage!" << std::endl;
                    
                } else if (signChoice == "3") { // Quen
                    player.tempBuff = 5;
                    std::cout << "Quen shield activated! (+5 defense)" << std::endl;
                    
                } else if (signChoice == "4") { // Axii
                    if (rollDice(1, 100) > 50 || player.skillsLearned.at("Delusion")) {
                        std::cout << "Axii stunned the enemy! They skip a turn!" << std::endl;
                        enemyHp -= dmg;
                        continue; // Enemy skips turn
                    } else {
                        std::cout << "Axii failed!" << std::endl;
                    }
                } else if (signChoice == "5") { // Yrden
                    std::cout << "Yrden trap set! Enemy slowed." << std::endl;
                }
                
            } else if (choice == "4") { // Item
                if (!player.inventory.empty()) {
                    std::cout << "Inventory: ";
                    for (size_t i = 0; i < player.inventory.size(); i++) {
                        std::cout << (i + 1) << "." << player.inventory[i] << " ";
                    }
                    std::cout << "\nChoose item (0 to cancel): ";
                    
                    std::string itemChoice;
                    std::getline(std::cin, itemChoice);
                    
                    try {
                        int idx = std::stoi(itemChoice) - 1;
                        if (idx >= 0 && idx < static_cast<int>(player.inventory.size())) {
                            std::string item = player.inventory[idx];
                            if (item == "Bread" || item == "Dwarven Spirit") {
                                player.hp = std::min(player.maxHp, player.hp + 30);
                                if (player.skillsLearned.at("Heightened Tolerance")) {
                                    player.hp = std::min(player.maxHp, player.hp + 15);
                                }
                                player.inventory.erase(player.inventory.begin() + idx);
                                std::cout << "Used " << item << "! HP restored." << std::endl;
                            }
                        }
                    } catch (...) {
                        // Invalid choice
                    }
                } else {
                    std::cout << "Inventory empty!" << std::endl;
                }
                continue; // Item doesn't deal damage
                
            } else if (choice == "5") { // Defend
                playerDefending = true;
                std::cout << "You take a defensive stance!" << std::endl;
            }
            
            // Apply player damage
            if (dmg > 0) {
                enemyHp -= dmg;
            }
            
            // Check if enemy defeated
            if (enemyHp <= 0) {
                std::cout << Colors::GREEN << "Victory!" << Colors::END << std::endl;
                player.gainExp(monster.exp);
                player.gold += static_cast<int>(10 * diff.goldMult);
                player.inventory.push_back(monster.loot);
                return true;
            }
            
            // Enemy turn
            double hpPercent = (static_cast<double>(enemyHp) / monster.hp) * 100.0;
            std::string action = ai.decideAction(hpPercent);
            
            if (action == "Attack") {
                int eDmg = rollDice(monster.minDmg, monster.maxDmg);
                if (playerDefending) {
                    eDmg = std::max(1, eDmg / 2);
                }
                eDmg = std::max(0, eDmg - player.defense - player.tempBuff);
                player.hp -= eDmg;
                std::cout << monster.name << " attacks you for " << eDmg << " damage!" << std::endl;
                
            } else if (action == "Defend") {
                std::cout << monster.name << " defends!" << std::endl;
                
            } else if (action == "Heal") {
                enemyHp += 20;
                std::cout << monster.name << " heals itself!" << std::endl;
                
            } else if (action == "Special") {
                int specialDmg = rollDice(monster.minDmg + 5, monster.maxDmg + 10);
                player.hp -= specialDmg;
                std::cout << monster.name << " uses special attack for " 
                          << specialDmg << " damage!" << std::endl;
            }
            
            // Reset temp buff
            if (choice != "3" || (choice == "3" && player.tempBuff > 0)) {
                player.tempBuff = 0;
            }
        }
        
        return false; // Player died
    }
    
    // Save/Load System
    static void saveGame(const Witcher& player) {
        std::ofstream file(SAVE_FILE);
        if (!file.is_open()) {
            std::cout << "Error: Could not save game!" << std::endl;
            return;
        }
        
        auto data = player.toMap();
        for (const auto& pair : data) {
            file << pair.first << "=" << pair.second << std::endl;
        }
        
        file.close();
        std::cout << "Game saved successfully!" << std::endl;
    }
    
    static std::unique_ptr<Witcher> loadGame() {
        std::ifstream file(SAVE_FILE);
        if (!file.is_open()) {
            return nullptr;
        }
        
        std::map<std::string, std::string> data;
        std::string line;
        
        while (std::getline(file, line)) {
            size_t eqPos = line.find('=');
            if (eqPos != std::string::npos) {
                std::string key = line.substr(0, eqPos);
                std::string value = line.substr(eqPos + 1);
                data[key] = value;
            }
        }
        
        file.close();
        
        if (data.empty()) {
            return nullptr;
        }
        
        return std::make_unique<Witcher>(Witcher::fromMap(data));
    }
    
    // Main Menu
    static void mainMenu(Witcher& player) {
        while (true) {
            clearScreen();
            player.displayStatus();
            
            std::cout << "1. Go Hunting" << std::endl;
            std::cout << "2. Skill Tree" << std::endl;
            std::cout << "3. Meditate (Heal)" << std::endl;
            std::cout << "4. Save Game" << std::endl;
            std::cout << "5. Quit Game" << std::endl;
            
            std::string choice;
            std::cout << "Choose: ";
            std::getline(std::cin, choice);
            
            if (choice == "1") {
                auto monsters = getMonsterKeys();
                if (!monsters.empty()) {
                    std::string target = monsters[rollDice(0, monsters.size() - 1)];
                    
                    bool conjuction = (rollDice(1, 100) > 90); // 10% chance
                    if (!combat(player, target, conjuction)) {
                        std::cout << Colors::RED << "\n=== YOU DIED ===" << Colors::END << std::endl;
                        std::cout << "Press Enter to respawn (or type 'quit' to exit): ";
                        
                        std::string resp;
                        std::getline(std::cin, resp);
                        
                        if (resp == "quit") break;
                        
                        player.hp = player.maxHp;
                        player.tempBuff = 0;
                    }
                }
                waitForEnter();
                
            } else if (choice == "2") {
                skillTreeMenu(player);
                
            } else if (choice == "3") {
                player.hp = player.maxHp;
                std::cout << "HP fully restored..." << std::endl;
                waitForEnter();
                
            } else if (choice == "4") {
                saveGame(player);
                waitForEnter();
                
            } else if (choice == "5") {
                std::cout << "Farewell, Witcher!" << std::endl;
                break;
            }
        }
    }
    
    // Start Game
    static void startGame() {
        Colors::init();
        clearScreen();
        
        std::cout << Colors::BOLD << Colors::PURPLE 
                  << "=== WITCHER TEXT RPG (C++ VERSION) ===" 
                  << Colors::END << std::endl;
        std::cout << "1. Continue (Load Game)" << std::endl;
        std::cout << "2. New Game / NG+" << std::endl;
        
        std::string choice;
        std::cout << "Choose: ";
        std::getline(std::cin, choice);
        
        if (choice == "1") {
            auto player = loadGame();
            if (player) {
                mainMenu(*player);
                return;
            } else {
                std::cout << "No saved game found!" << std::endl;
                waitForEnter();
            }
        }
        
        // New Game / NG+
        auto oldSave = loadGame();
        if (oldSave) {
            printSeparator();
            std::cout << "Found previous save data. Continue with NG+?" << std::endl;
            std::cout << "1. New Game (Fresh start)" << std::endl;
            std::cout << "2. New Game+ (Continue from level " << oldSave->level << ")" << std::endl;
            
            std::string ngChoice;
            std::cout << "Choose: ";
            std::getline(std::cin, ngChoice);
            
            if (ngChoice == "2") {
                Witcher newPlayer(oldSave->name, oldSave->school, oldSave->difficulty);
                newPlayer.level = oldSave->level;
                newPlayer.skillPoints = oldSave->skillPoints;
                newPlayer.skillsLearned = oldSave->skillsLearned;
                newPlayer.ngPlus = oldSave->ngPlus + 1;
                newPlayer.gold = oldSave->gold;
                newPlayer.maxHp += (newPlayer.ngPlus * 20);
                newPlayer.baseDmg += (newPlayer.ngPlus * 5);
                newPlayer.hp = newPlayer.maxHp;
                
                std::cout << Colors::CYAN << "--- Starting New Game+ Round " 
                          << newPlayer.ngPlus << " ---" << Colors::END << std::endl;
                waitForEnter();
                
                mainMenu(newPlayer);
                return;
            }
        }
        
        // Create new character
        std::string name;
        std::cout << "Witcher's name: ";
        std::getline(std::cin, name);
        
        if (name.empty()) name = "Geralt";
        
        std::cout << "School: 1.Wolf 2.Griffin 3.Bear 4.Cat" << std::endl;
        std::string schoolChoice;
        std::cout << "Choose: ";
        std::getline(std::cin, schoolChoice);
        
        std::map<std::string, std::string> schoolMap = {
            {"1", "Wolf"}, {"2", "Griffin"}, {"3", "Bear"}, {"4", "Cat"}
        };
        
        std::string school = schoolMap.count(schoolChoice) ? 
                             schoolMap[schoolChoice] : "Wolf";
        
        // Choose difficulty
        std::cout << "\nDifficulty:" << std::endl;
        std::cout << "1. Just the Story (Easy)" << std::endl;
        std::cout << "2. Story and Swords (Normal)" << std::endl;
        std::cout << "3. Blood and Broken Bones (Hard)" << std::endl;
        std::cout << "4. Death March! (Very Hard)" << std::endl;
        
        std::string diffChoice;
        std::cout << "Choose: ";
        std::getline(std::cin, diffChoice);
        
        std::map<std::string, std::string> diffMap = {
            {"1", "Just the Story"},
            {"2", "Story and Swords"},
            {"3", "Blood and Broken Bones"},
            {"4", "Death March!"}
        };
        
        std::string difficulty = diffMap.count(diffChoice) ? 
                                 diffMap[diffChoice] : "Story and Swords";
        
        Witcher player(name, school, difficulty);
        std::cout << "\nWelcome, " << player.name << " of the " << player.school 
                  << " School!" << std::endl;
        waitForEnter();
        
        mainMenu(player);
    }
};

const std::string GameManager::SAVE_FILE = "witcher_save.txt";

// ===== Main Function =====
int main() {
    srand(static_cast<unsigned int>(time(nullptr)));
    
    try {
        GameManager::startGame();
    } catch (const std::exception& e) {
        std::cerr << Colors::RED << "Error: " << e.what() << Colors::END << std::endl;
        waitForEnter();
        return 1;
    }
    
    return 0;
}
