import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk
import os

class Character:
    def __init__(self, name, hp, attack_power):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack_power = attack_power

    def Is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)

class Hero(Character):
    def __init__(self, name, hp, attack_power):
        super().__init__(name, hp, attack_power)
        self.turn = False  # Tracks who turn it is 

class Monster(Character):
    def act(self, target_list):
        #picks a random living hero to attack 
        living_heroes = [h for h in target_list if h.Is_alive()]
        if living_heroes:
            target = random.choice(living_heroes)
            damage = random.randint(self.attack_power - 4, self.attack_power + 4)
            target.take_damage(damage)
            return f"{self.name} attacked {target.name} for {damage} damage!"
        return ""

#UI Class

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Battle Quest")
        self.root.geometry("1400x900")
        
        # Initialize Data
        self.heroes = [Hero("Knight", 250, 42), Hero("Archer", 180, 50),]
        self.monsters = [Monster("Goblin", 80, 20), Monster("Orc", 200, 30)]
        self.selected_hero = None
        
        # Image setup
        # Use a relative images/ folder by default (safer for other machines)
        self.image_folder = os.path.join(os.path.dirname(__file__), "images")
        self.hero_images = {}
        self.monster_images = {}
        self.image_map = {
            "Knight": "Knight.png",
            "Archer": "Archer.png",
            "Goblin": "Goblin.jpeg",
            "Orc": "ORC.png",
        }
        
        #Creates the visuals and updates changes/refreshs on the display
        self.setup_ui()
        self.update_display()

    def setup_ui(self):
        # Top Display: Health Bars/code below creates a text label with font and pixels 
        self.info_label = tk.Label(self.root, text="Select a Hero to start your turn", font=("BJCree", 12))
        self.info_label.pack(pady=10)
        # Battle Frame: Contains hero and monster butttons 
        self.battle_frame = tk.Frame(self.root)
        self.battle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Hero Buttons
        self.hero_buttons = []
        for i, hero in enumerate(self.heroes):
            btn = tk.Button(self.battle_frame, text=f"{hero.name}\nHP: {hero.hp}", 
                            command=lambda h=hero: self.select_hero(h))
            btn.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            self.hero_buttons.append(btn)
        
        # Configure grid weights for expansion
        for i in range(len(self.heroes)):
            self.battle_frame.grid_columnconfigure(i, weight=1)
        self.battle_frame.grid_rowconfigure(0, weight=1)
        self.battle_frame.grid_rowconfigure(1, weight=1)

        # Load hero images
        for i, hero in enumerate(self.heroes):
            if hero.name in self.image_map:
                img_path = os.path.join(self.image_folder, self.image_map[hero.name])
                try:
                    img = Image.open(img_path)
                    img.thumbnail((200, 200)) 
                    self.hero_images[hero.name] = ImageTk.PhotoImage(img) # Store the image reference to prevent garbage collection
                    self.hero_buttons[i].config(image=self.hero_images[hero.name], compound='top')
                except Exception as e:
                    print(f"Error loading image for {hero.name}: {e}")

        # Monster Buttons
        self.monster_buttons = []
        for i, monster in enumerate(self.monsters):
            btn = tk.Button(self.battle_frame, text=f"{monster.name}\nHP: {monster.hp}", 
                            bg="mistyrose",
                            command=lambda m=monster: self.attack_monster(m))
            btn.grid(row=1, column=i, padx=10, pady=20, sticky='nsew')
            self.monster_buttons.append(btn)

        # Load monster images
        for i, monster in enumerate(self.monsters):
            if monster.name in self.image_map:
                img_path = os.path.join(self.image_folder, self.image_map[monster.name])
                try:
                    img = Image.open(img_path)
                    img.thumbnail((200, 200))
                    self.monster_images[monster.name] = ImageTk.PhotoImage(img)
                    self.monster_buttons[i].config(image=self.monster_images[monster.name], compound='top')
                except Exception as e:
                    print(f"Error loading image for {monster.name}: {e}")

    def select_hero(self, hero):
        # If the hero is not alive or it is not their turn, they cannot be selected.
        if not hero.Is_alive() or hero.turn:
            return
        self.selected_hero = hero
        self.info_label.config(text=f"Selected {hero.name}. Now pick a target!")

    def attack_monster(self, monster):
        if not self.selected_hero or not monster.Is_alive():
            return
        
        # Hero Attacks
        damage = random.randint(self.selected_hero.attack_power - 5, self.selected_hero.attack_power + 5)
        monster.take_damage(damage)
        self.selected_hero.turn = True # Marks that the hero has taken their turn
        self.selected_hero = None # Resets selected hero after attack so they can attack when its their turn again
        
        self.update_display()
        if self.check_game_over():
            return
        
        # Check if all heroes have taken their turn or are defeated, its pretty much the monsters turn.
        if all(h.turn or not h.Is_alive() for h in self.heroes):
            self.root.after(1000, self.monster_turn)
        # Keeps log of the monsters attack and displays it in the message box.
    def monster_turn(self):
        log = []
        for monster in self.monsters:
            if monster.Is_alive():
                msg = monster.act(self.heroes)
                log.append(msg)
        
        # Reset hero turns
        for h in self.heroes:
            h.turn = False
            
        messagebox.showinfo("Monster Turn", "\n".join(log)) 
        self.update_display()
        self.check_game_over()
        # Updates the display after each action, showing current HP and disabling the buttons for dead characters 
    def update_display(self):
        for i, h in enumerate(self.heroes):
            if not h.Is_alive():
                color = "gray"
                state = "disabled"
            elif h.turn:
                color = "lightgray"
                state = "disabled"
            else:
                color = "lightgreen"
                state = "normal"
            self.hero_buttons[i].config(text=f"{h.name}\nHP: {h.hp}", bg=color, state=state) 
            
        for i, m in enumerate(self.monsters):
            state = "disabled" if not m.Is_alive() else "normal"
            self.monster_buttons[i].config(text=f"{m.name}\nHP: {m.hp}", state=state)

    def check_game_over(self):
        if all(not m.Is_alive() for m in self.monsters):
            messagebox.showinfo("Victory!", "All monsters defeated!")
            self.root.destroy()
            return True
        if all(not h.Is_alive() for h in self.heroes):
            messagebox.showerror("Defeat", "Your team has fallen...")
            self.root.destroy()
            return True
        return False

# This starts the game and it creates the main window, initializes the GameApp, and starts the Tkinter loop.
if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.configure(bg="Red")
    root.mainloop()
