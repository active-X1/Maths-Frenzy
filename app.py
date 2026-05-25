import time
import tkinter as tk
from random import randint

class MathGame:
    T = 20  # timer in seconds
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("SIMPLE CALCULATOR AND MATHS GAME FRENZY!")
        self.window.geometry("600x400")
        self.window.configure(bg="#f2f2f2")
        self.main_menu() 
    
    def main_menu(self):
        self.clear_screen()
        tk.Label(self.window, text="Follow my instagram page @abc_apps_official, or facebook page at ABC apps").pack()
        tk.Label(self.window, text="ABC apps").pack()
        tk.Label(self.window, text="MAIN MENU", width=30).pack(pady=10)
        tk.Button(self.window, text="CALCULATOR", width=20, command=lambda: self.calculator_choice()).pack(pady=5)
        tk.Button(self.window, text="GAME", width=20, command=lambda: self.game()).pack(pady=5)     
        tk.Button(self.window, text="HOW TO PLAY", width=20, command=lambda: self.help()).pack(pady=5)
        tk.Button(self.window, text="EXIT APP", width=20, command=lambda: self.exit_ask_first()).pack(pady=40)
        
        
    def help(self):
        self.clear_screen()
        tk.Button(self.window, text="GAME PLAY KNOW_HOW", width=30, command=lambda: self.how_to_play()).pack()
        tk.Button(self.window, text="GAME TUTORIAL", width=20, command=lambda: self.tutorial_screen()).pack(pady=5)
        tk.Button(self.window, text="<<<", width=20, command=lambda: self.main_menu()).pack(pady=10)
        
    def tutorial_screen(self):
        self.clear_screen()
        tk.Label(self.window, text="Lets have a little tutorial champ...").pack()
        tk.Label(self.window, text="1. 4 + 4 = ?", width=25).pack(pady=20)
        tk.Label(self.window, text="\nHere the right answer is 8, therefore lets enter 8 and click on >>> to take us to the next question").pack()
        self.answer_entry = tk.Entry(self.window)
        self.answer_entry.pack()
        tk.Button(self.window, text=">>>", width=20, command=lambda: self.message_user()).pack(pady=5)
        tk.Button(self.window, text="MAIN MENU", width=20, command=lambda: self.main_menu()).pack(pady=10)
        
    def message_user(self):
        self.clear_screen()
        tk.Label(self.window, text="Why dont we try it in the real game(Maths Frenzy)").pack()
        tk.Button(self.window, text="OK", width=10, command=lambda: self.welcom_screen()).pack()
        tk.Button(self.window, text="Cancel", width=10, command=lambda: self.help()).pack()

    def how_to_play(self):
        self.clear_screen()
        tk.Label(self.window, text="There are three LEVELS in your game BEGINNER, ADVANCED or MASTER level, \nEach level simultaneously come with its own difficulty \nYou can choose either of the level based on your capability").pack()
        tk.Label(self.window, text="\nAfter choosing your level, you then choose the OPERATION you want to play on, \ni.e. Addition, Subtraction, Division or Multiplication, then you follow the levels gradually").pack(pady=10)
        tk.Button(self.window, text="Exit gameplay-know-how", command=lambda: self.help()).pack()
        
    def exit_ask_first(self):
        self.clear_screen()
        tk.Button(self.window, text="Are you sure you want to exit?").pack()
        tk.Button(self.window, text="YES", width=10, command=lambda: self.window.destroy()).pack(pady=5)
        tk.Button(self.window, text="NO", width=10, command=lambda: self.main_menu()).pack(pady=10) 

    def calculator_choice(self):
        self.clear_screen()
        tk.Button(self.window, text="TWO NUMBER CAL.", command=lambda: self.calculator2()).pack()
        tk.Button(self.window, text="0 - 9 digit CAL.", command=lambda: self.calculator1()).pack(pady=5)
        tk.Button(self.window, text="<<<", command=lambda: self.main_menu()).pack(pady=10)    
    
    def calculator2(self):
        self.clear_screen()
        tk.Label(self.window, text="Choose the operation you want to solve on:").pack()
        tk.Button(self.window, text="Addition", width=20, command=lambda: self.Add()).pack()
        tk.Button(self.window, text="Subtraction", width=20, command=lambda: self.Minus()).pack(pady=5)    
        tk.Button(self.window, text="Multiplication", width=20, command=lambda: self.Multiply()).pack(pady=5)
        tk.Button(self.window, text="Division", width=20, command=lambda: self.Divide()).pack(pady=5)
        tk.Button(self.window, text="<<<", command=lambda: self.calculator_choice()).pack(pady=20)    
    
    def calculator1(self):
        class Calculator:
            def __init__(self, master):
                self.master = master
                self.entry = tk.Entry(master, width=40, borderwidth=10)
                self.entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
                self.create_buttons()

            def create_buttons(self):
                buttons = [
                    '7', '8', '9', '/',
                    '4', '5', '6', '*',
                    '1', '2', '3', '-',
                    '0', '.', '=', '+'
                ]

                row_val = 1
                col_val = 0

                for button in buttons:
                    tk.Button(self.master, text=button, width=10, command=lambda button=button: self.click_button(button)).grid(row=row_val, column=col_val)
                    col_val += 1
                    if col_val > 3:
                        col_val = 0
                        row_val += 1

                tk.Button(self.master, text="Clear", width=21, command=self.clear_entry).grid(row=row_val, column=0, columnspan=2)
                tk.Button(self.master, text="Delete", width=22, command=self.delete_char).grid(row=row_val, column=2, columnspan=2)

            def click_button(self, button):
                if button == '=':
                    try:
                        result = eval(self.entry.get())
                        self.entry.delete(0, tk.END)
                        self.entry.insert(tk.END, str(result))
                    except:
                        self.entry.delete(0, tk.END)
                        self.entry.insert(tk.END, "Error")
                else:
                    self.entry.insert(tk.END, button)

            def clear_entry(self):
                self.entry.delete(0, tk.END)

            def delete_char(self):
                current = self.entry.get()
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, current[:-1])

        root = tk.Tk()
        root.title("Calculator")
        calc = Calculator(root)
        root.mainloop()


    def Add(self):
        self.clear_screen()
        tk.Label(self.window, text="First number:").pack()
        self.xadd = tk.Entry(self.window)
        self.xadd.pack()    
        tk.Label(self.window, text="Second number").pack()
        self.yadd = tk.Entry(self.window)
        self.yadd.pack()
        tk.Button(self.window, text="ADD", command=lambda: self.calculate_add()).pack(pady=10)
        tk.Button(self.window, text="<<<", command=lambda: self.calculator2()).pack(pady=10)
        self.result_label = tk.Label(self.window, text="")
        self.result_label.pack()

    def calculate_add(self):
        try:
            num1=float(self.xadd.get())
            num2=float(self.yadd.get())
            result=num1+num2
            self.clear_screen()
            tk.Label(self.window, text=f"{num1} + {num2} = {result}").pack()
            tk.Button(self.window, text="<<<", command=lambda: self.Add()).pack(pady=10)
        except ValueError:
            self.clear_screen()
            tk.Label(self.window, text="invalid input").pack()

    def Minus(self):
        self.clear_screen()
        tk.Label(self.window, text="First number:").pack()
        self.xsub = tk.Entry(self.window)
        self.xsub.pack()    
        tk.Label(self.window, text="Second number").pack()
        self.ysub = tk.Entry(self.window)
        self.ysub.pack()
        tk.Button(self.window, text="SUBTRACT", command=lambda: self.calculate_sub()).pack(pady=10)
        tk.Button(self.window, text="<<<", command=lambda: self.calculator2()).pack(pady=10)
        self.result_label = tk.Label(self.window, text="")
        self.result_label.pack()

    def calculate_sub(self):
        try:
            num1=float(self.xsub.get())
            num2=float(self.ysub.get())
            result=num1-num2
            self.clear_screen()
            tk.Label(self.window, text=f"{num1} - {num2} = {result}").pack()
            tk.Button(self.window, text="<<<", command=lambda: self.Minus()).pack(pady=10)
        except ValueError:
            self.clear_screen()
            tk.Label(self.window, text="invalid input").pack()


    def Multiply(self):        
        self.clear_screen()
        tk.Label(self.window, text="First number:").pack()
        self.xmultiply = tk.Entry(self.window)
        self.xmultiply.pack()    
        tk.Label(self.window, text="Second number").pack()
        self.ymultiply = tk.Entry(self.window)
        self.ymultiply.pack()
        tk.Button(self.window, text="MULTIPLY", command=lambda: self.calculate_multiply()).pack(pady=10)
        tk.Button(self.window, text="<<<", command=lambda: self.calculator2()).pack(pady=10)
        self.result_label = tk.Label(self.window, text="")
        self.result_label.pack()

    def calculate_multiply(self):
        try:
            num1=float(self.xmultiply.get())
            num2=float(self.ymultiply.get())
            result=num1*num2
            self.clear_screen()
            tk.Label(self.window, text=f"{num1} × {num2} = {result}").pack()
            tk.Button(self.window, text="<<<", command=lambda: self.Multiply()).pack(pady=10)
        except ValueError:
            self.clear_screen()
            tk.Label(self.window, text="Invalid input").pack()

    def Divide(self):
        self.clear_screen()
        tk.Label(self.window, text="First number:").pack()
        self.xdivide = tk.Entry(self.window)
        self.xdivide.pack()    
        tk.Label(self.window, text="Second number").pack()
        self.ydivide = tk.Entry(self.window)
        self.ydivide.pack()
        tk.Button(self.window, text="DIVIDE", command=lambda: self.calculate_divide()).pack(pady=10)
        tk.Button(self.window, text="<<<", command=lambda: self.calculator2()).pack(pady=10)
        self.result_label = tk.Label(self.window, text="")
        self.result_label.pack()

    def calculate_divide(self):
        try:
            num1=float(self.xdivide.get())
            num2=float(self.ydivide.get())
            result=num1/num2
            self.clear_screen()
            tk.Label(self.window, text=f"{num1} ÷ {num2} = {result}").pack()
            tk.Button(self.window, text="<<<", command=lambda: self.Divide()).pack(pady=10)
        except ValueError:
            self.clear_screen()
            tk.Label(self.window, text="Invalid input").pack()


    def game(self):        
        self.scores = {"addition": 0, "subtraction": 0, "division": 0, "multiplication": 0}
        self.mode = None
        self.operation = None
        self.score = 0
        self.question_number = 0
        self.num1 = None
        self.num2 = None
        self.answer = None
        self.timer_label = None
        self.time_left = self.T
        self.timer_id = None
        tk.Button(self.window, text="BACK", command=self.main_menu).pack()
        self.welcom_screen()

    def welcom_screen(self):
        self.clear_screen()
        tk.Button(self.window, text="MATHS FRENZY").pack()
        tk.Label(self.window, text="\n\nBefore we proceed, \nYou must agree that you will be consistent in learning maths").pack(pady=10)
        tk.Button(self.window, text="I AGREE", width=21, command=lambda: self.register_screen()).pack(pady=10)
        tk.Button(self.window, text="NO I DON'T", width=21, command=lambda: self.prompt_user()).pack(pady=5)
        tk.Button(self.window, text="<<<", width=21, command=lambda: self.main_menu()).pack(pady=50)

    def prompt_user(self):
        self.clear_screen()
        tk.Label(self.window, text="You have to agree that you will be consistent in learning maths, for you to play game").pack()
        tk.Button(self.window, text="I AGREE", width=21, command=lambda: self.register_screen()).pack(pady=10)
        tk.Button(self.window, text="QUIT", width=21, command=lambda: self.main_menu()).pack(pady=5)

    def register_screen(self):
        self.clear_screen()
        tk.Label(self.window, text="First name:", width=25).pack()
        self.first_name_entry = tk.Entry(self.window)
        self.first_name_entry.pack()
        tk.Label(self.window, text="Surname:", width=25).pack(pady=5)
        self.sur_name_entry = tk.Entry(self.window)
        self.sur_name_entry.pack()
        tk.Label(self.window, text="Nickname:" , width=25).pack(pady=5)
        self.nick_name_entry = tk.Entry(self.window)
        self.nick_name_entry.pack()
        tk.Button(self.window, text="Register", width=20, command=lambda: self.select_screen()).pack(pady=15)
        tk.Button(self.window, text="MAIN MENU", width=20, command=lambda: self.main_menu()).pack(pady=40)


    def select_screen(self):
        self.clear_screen()
        tk.Label(self.window, text="LEVEL", width=10).pack()
        tk.Button(self.window, text="Beginner", width=20, command=lambda: self.set_mode("beginner")).pack()
        tk.Button(self.window, text="Advanced", width=20, command=lambda: self.set_mode("advanced")).pack(pady=5)
        tk.Button(self.window, text="Master", width=20, command=lambda: self.set_mode("master")).pack(pady=5)
        tk.Button(self.window, text="<<<", width=10, command=lambda: self.register_screen()).pack(pady=20)
        tk.Button(self.window, text="MENU", width=10, command=lambda: self.main_menu()).pack(pady=10)


    def set_mode(self, mode):
        self.mode = mode
        self.select_operation_screen()

    def select_operation_screen(self):
        self.clear_screen()
        tk.Label(self.window, text="SELECT OPERATION", width=50).pack()
        tk.Button(self.window, text="Addition", width=20, command=lambda: self.set_operation("addition")).pack(pady=10)
        tk.Button(self.window, text="Subtraction", width=20, command=lambda: self.set_operation("subtraction")).pack(pady=5)
        tk.Button(self.window, text="Multiplication", width=20, command=lambda: self.set_operation("multiplication")).pack(pady=5)
        tk.Button(self.window, text="Division", width=20, command=lambda: self.set_operation("division")).pack(pady=5)
        tk.Button(self.window, text="<<<", width=10, command=lambda: self.select_screen()).pack(pady=10)
    
    def set_operation(self, operation):
        self.operation = operation
        self.play_game()

    def play_game(self):
        self.clear_screen()
        self.score = 0
        self.question_number = 0
        self.time_left = self.T
        self.generate_question()
        self.display_question()
        self.timer_label = tk.Label(self.window, text=f"Time left: {self.time_left} seconds")
        self.timer_label.pack()
        self.update_timer()

    def generate_question(self):
        if self.mode == "beginner":
            self.num1 = randint(-20, 20)
            self.num2 = randint(-20, 20)
        elif self.mode == "advanced":
            self.num1 = randint(-50, 50)
            self.num2 = randint(-50, 50)
        elif self.mode == "master":
            self.num1 = randint(-100, 100)
            self.num2 = randint(-100, 100)

        if self.operation == "addition":
            self.answer = self.num1 + self.num2
            self.question = f"What is {self.num1} + {self.num2}?\n"
        elif self.operation == "subtraction":
            self.answer = self.num1 - self.num2
            self.question = f"What is {self.num1} - {self.num2}?\n"
        elif self.operation == "multiplication":
            self.answer = self.num1 * self.num2
            self.question = f"What is {self.num1} * {self.num2}?\n"
        elif self.operation == "division":
            self.answer = round(self.num1 / self.num2, 2)
            self.question = f"What is {self.num1} ÷ {self.num2}?\n"

    def display_question(self):
        self.clear_screen()
        self.timer_label = tk.Label(self.window, text=f"{self.time_left} seconds\n", width=15)
        self.timer_label.pack()
        tk.Label(self.window, text=self.question, width=30).pack(pady=10)
        self.answer_entry = tk.Entry(self.window)
        self.answer_entry.pack()
        tk.Button(self.window, text=">>>", width=15, command=self.check_answer).pack(pady=5)
        tk.Button(self.window, text="CALCULATOR", width=15, command=self.calculator1).pack(pady=20)
        tk.Button(self.window, text="QUIT GAME", width=15, command=lambda: self.main_menu()).pack(pady=70)
    def check_answer(self):
        try:
            self.answer_entry = float(self.answer_entry.get())
            if self.answer_entry == self.answer:
                self.score += 1
                tk.Label(self.window, text="Correct Answer!").pack()
            else:
                self.clear_screen()
                tk.Label(self.window, text=f"Sorry, the correct answer was {self.answer}").pack()
        except ValueError:
            tk.Label(self.window, text="Invalid input").pack()
        self.question_number += 1
        if self.question_number < 20:
            self.time_left = self.T
            self.generate_question()
            self.display_question()
            self.update_timer()
        else:
            self.game_over_screen()

    def update_timer(self):
        if hasattr(self, 'timer_id'):
            self.window.after_cancel(self.timer_id)
        if self.time_left > 0:
            self.timer_label['text'] = f"Time left: {self.time_left} seconds"
            self.time_left -= 1
            self.timer_id = self.window.after(1000, self.update_timer)
        else:
            self.check_answer()

    def game_over_screen(self):
        self.clear_screen()
        tk.Label(self.window, text=f"Game Over! Your final score is {self.score}", width=50).pack()
        tk.Button(self.window, text="Play Again", width=20, command=self.select_screen).pack(pady=10)
        tk.Button(self.window, text="MAIN MENU", width=20, command=lambda: self.main_menu()).pack(pady=10)
        tk.Button(self.window, text="EXIT APP", width=20, command=lambda: self.exit_ask()).pack(pady=30)
    def exit_ask(self):
        self.clear_screen()
        tk.Button(self.window, text="Are you sure you want to exit the app?", width=70,).pack()
        tk.Button(self.window, text="YES", width=20, command= self.window.destroy).pack()
        tk.Button(self.window, text="NO", width=20, command=lambda: self.game_over_screen()).pack(pady=10)
        
    def clear_screen(self):
        for widget in self.window.winfo_children():
            widget.destroy()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    game = MathGame()
    game.run()