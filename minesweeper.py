import random
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import math
from PIL import ImageTk, Image

TASK_ONE = 'TASK_ONE'
TASK_TWO = 'TASK_TWO'
POKEMON = "☺"
FLAG = "f"
UNEXPOSED = "~"
UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"
DIRECTIONS = (UP, DOWN, LEFT, RIGHT,
              f"{UP}-{LEFT}", f"{UP}-{RIGHT}",
              f"{DOWN}-{LEFT}", f"{DOWN}-{RIGHT}")
class BoardModel:
    """Model class that updates game string and other informations"""

    def __init__(self, grid_size, num_pokemon):
        """
        Construct a game string. 

        Parameters:
            grid_size (int): size of grid(game board will always be square)
            num_pokemon (int):number of pokemons in game.
        """
        self._grid_size = grid_size
        self._num_pokemon = num_pokemon
        self._game = UNEXPOSED * grid_size ** 2
        self._pokemon_locations = self.generate_pokemons()

    def generate_pokemons(self):
        """Generates new pokemon locations

            Returns:
                (tuple<int>): Returns a tuple containing indexes of generated pokemons for game string"""
        cell_count = self._grid_size ** 2
        pokemon_locations = ()

        for _ in range(self._num_pokemon):
            if len(pokemon_locations) >= cell_count:
                break
            index = random.randint(0, cell_count-1)

            while index in pokemon_locations:
                index = random.randint(0, cell_count-1)

            pokemon_locations += (index,)

        return pokemon_locations

    def position_to_index(self, position):
        """Converts row, column coordinate in grid to game strings index.

        Parameters:
            position (tuple<int, int>): Row, column position of cell on grid.

        Returns:
            (int): Index of cell on game string.
        """
        x, y = position
        return x * self._grid_size + y

    def replace_character_at_index(self, index, character):
        """Replace the character at specified index with new specified character in game string
        
        Parameters:
            index (int): Index position in game string where character will be replaced.
            character (str): New character that will replace old character.
        """
        self._game = self._game[:index] + character + self._game[index + 1:]

    def flag_cell(self, index):
        """Toggle flag on if character at index is a unexposed. Toggle flag off if character at 
        index is flag.

        Parameters: 
            index (int): Index in game string where flag is toggled. 
        """
        if self._game[index] == FLAG:
            self.replace_character_at_index(index, UNEXPOSED)

        elif self._game[index] == UNEXPOSED:
            self.replace_character_at_index(index, FLAG)

    def index_in_direction(self, index, direction):
        """The specified index position in game string is used with direction to calculate the
        new position index of an adjacent cell.

        For example:
          | 1 | 2 | 3 |
        A | i | j | k |
        B | l | m | n |
        C | o | p | q |

        The index of m is 4 in the game string.
        if the direction specified is "up" then:
        the updated position corresponds with j which has the index of 1 in the game string.

        Parameters:
            index (int): The index on game string.
            direction (str): Direction of adjacent cell.

        Returns:
            (int): New index of one adjacent cell to cell at specified index in game string.
            
            None for invalid direction.
        """
        col = index % self._grid_size
        row = index // self._grid_size
        if RIGHT in direction:
            col += 1
        elif LEFT in direction:
            col -= 1
        # Notice the use of if, not elif here
        if UP in direction:
            row -= 1
        elif DOWN in direction:
            row += 1
        if not (0 <= col < self._grid_size and 0 <= row < self._grid_size):
            return None

        return self.position_to_index((row,col))
        
    def neighbour_directions(self, index):
        """Seek out all directions that has a neighbouring cell.

        Parameters:
            index (int): Index in game string.
        
        Returns:
            (list<int>): A list of index that has a neighouring cells.
        """
        neighbours = []
        for direction in DIRECTIONS:
            neighbour = self.index_in_direction(index, direction)
            if neighbour is not None:
                neighbours.append(neighbour)
        return neighbours

    def number_at_cell(self, index):
        """Calculates the number that should be displayed on a cell at specified index based
        on pokemon locations.

        Parameters: 
            index (int): Index of currently selected cell in game string.
        
        Returns:
            (int): Number to be displayed at given index in game string.
        """
        if self._game[index] != UNEXPOSED:
            return int(self._game[index])

        number = 0
        for neighbour in self.neighbour_directions(index):
            if neighbour in self._pokemon_locations:
                number += 1
        return number
        # Alternatively
        # return len(set(pokemon_locations) & set(neighbour_directions(index, grid_size)))

    def check_win(self):
        """Checking if game has been won.

        Returns:
            (bool): True if player has won the game, false if not.
        """
        return UNEXPOSED not in self._game and self._game.count(FLAG) == len(self._pokemon_locations)

    def check_loss(self):
        """Checking if game has been lost.

        Returns:
            (bool): True if player has lost the game, false if not.
        """
        return POKEMON in self._game

    def reveal_Cells(self, index):
        """Reveals all neighouring cells at specified index and repeats for all cells that 
        had 0 adjacent pokemon.

        Parameters:
            index (int): index of selected cell to have its neighbours revealed.
        """
        number = self.number_at_cell(index)
        self.replace_character_at_index(index, str(number))
        clear = self.big_fun_search(index)
        for i in clear:
            if self._game[i] != FLAG:
                number = self.number_at_cell(i)
                self.replace_character_at_index(i, str(number))
        
    def big_fun_search(self, index):
        """Searching adjacent cells to see if there any Pokemon's present.
        Find all cells which should be revealed when a cell is selected.

        For cells which have a zero value (i.e. no neighbouring pokemons) all the cell"s
        neighbours are revealed. If one of the neighbouring cells is also zero then
        all of that cell"s neighbours are also revealed. This repeats until no
        zero value neighbours exist.

        For cells which have a non-zero value (i.e. cells with neighbour pokemons), only
        the cell itself is revealed.

        Parameters:
            index (int): Index of currently selected cell.
        
        Returns:
            (list<int>): List of cells to turn visible.
    """
        queue = [index]
        discovered = [index]
        visible = []

        if self._game[index] == FLAG:
            return queue

        number = self.number_at_cell(index)
        if number != 0:
            return queue

        while queue:
            node = queue.pop()
            for neighbour in self.neighbour_directions(node):
                if neighbour in discovered:
                    continue

                discovered.append(neighbour)
                if self._game[neighbour] != FLAG:
                    number = self.number_at_cell(neighbour)
                    if number == 0:
                        queue.append(neighbour)
                visible.append(neighbour)
        return visible

    def get_game(self):
        """Returns current game string.

        Returns:
            (str): updated game string.
        """
        return self._game
    
    def get_num_attempted_catches(self):
        """Search for the number of flags placed in game string.

        Returns:
            (int): Number of flags placed.
        """
        ball = 0
        for b in self.get_game():
            if b == FLAG:
                ball += 1
        return ball
                
class BoardView(tk.Canvas):
    """View and GUI of the 2D pokemon game board"""

    def __init__(self, master, grid_size, board_width=600, *args, **kwargs):
        """Construct a board view from updated game string
        
        Parameters:
            master (tk.Widget): Widget within which the game board is placed.
            grid_size (int): size of game grid(always square, so length and width are the same)
            board_width (int): Size of the board canvas.
        """
        super().__init__(master, *args, **kwargs)
        self._master = master
        self._board_width = board_width
        self._grid_size = grid_size
        self._width = self._board_width//self._grid_size
    
    def draw_board(self, board):
        """Construct the game board canvas using squares and text based on the current game 
        string. If game character is unexposed, then square will be dark green. If character 
        is a digit, then square is light green with digit placed insise. If the character is
        a flag, square will be red and if character is pokemon, square will be yellow at that
        cell location.

        Parameters:
            board (str): Current game string.
        """
        self.delete("all")
        for row in range(0, self._grid_size):
            for col in range(0, self._grid_size):
                x1=(col* self._width) #Top left x of square
                y1=(row * self._width) #Top left y of square
                x2=(x1 + self._width) #Bottom right x of square
                y2=(y1 + self._width) #Bottom right y of square
                index = self._grid_size * row + col 
                if board[index] == UNEXPOSED:
                    self.create_rectangle(x1,y1,x2,y2,fill='dark green')
                elif board[index].isdigit():
                    self.create_rectangle(x1,y1,x2,y2,fill='light green')
                    self.create_text(self.position_to_pixel((index// self._grid_size, index % self._grid_size)),
                    font="Arial", text = str(board[index]))
                elif board[index] == FLAG:
                    self.create_rectangle(x1,y1,x2,y2,fill='red')
                elif board[index] == POKEMON:
                    self.create_rectangle(x1,y1,x2,y2,fill='yellow')  

    def win_message_task1(self):
        """Message to be displayed after winning(task 1)."""
        messagebox.showinfo(title="You Won", message= "Congrats! You've won the game")

    def lose_message_task1(self):
        """Message to be displayed after losing(task1)."""
        messagebox.showinfo(title="Game over", message = "You lost! Better luck next time")

    def win_message_task2(self):
        """A yes/no message box to be displayed after winning(task2).

        Returns:
            (bool): True if response is yes, False if else.
        """
        yes_no = messagebox.askyesno(title="You Won", message = "You Won, Do you want to play again?")
        response = None
        if yes_no:
            response = True
        else:
            response = False
        return response

    def lose_message_task2(self):
        """A yes/no message box to be displayed after losing(task2).

        Returns:
            (bool): True if response is yes, False if else.
        """
        yes_no = messagebox.askyesno(title="Game over", message = "You lost, Do you want to play again?")
        response = None
        if yes_no:
            response = True
        else:
            response = False
        return response

    def position_to_pixel(self, position):
        """Converts the row, column of a cell on gameboard to the center pixel coordinates
        of that cell.

        Parameters:
            position (tuple<int, int>): Row, column position of cell on 2D game board.

        Returns:
            (tuple<int, int>): Pixel coordinates of center position of cell.
        """
        pixel = ()
        row,col = position
        x = col * self._width + (self._width/2)
        y = row * self._width + (self._width/2)
        pixel = x,y
        return pixel

    def pixel_to_positions(self, pixel):
        """Converts the pixel coordinates at any location within the cell to row, column
        position on game board for that cell.

        Parameters:
            pixel (tuple<int, int>): Pixel coordinates within a cell.
        
        Returns:
            (tuple<int, int): Row, column of a cell on 2D game board.
        """
        position = ()
        x, y = pixel
        col= x//self._width
        row= y//self._width
        position = row,col 
        return position

class ImageBoardView(BoardView):
    """Images view of 2D game board. A subclass to the Boardview class"""
    def __init__(self, master, grid_size, board_width=600, *args, **kwargs):
        """Construct a board view with images displayed instead of rectangles.

        Parameters(same as BoardView class):
            master (tk.Widget): Widget within which the game board is placed.
            grid_size (int): size of game grid(always square, so length and width are the same)
            board_width (int): Size of the board canvas.
        """
        super().__init__(master, grid_size, board_width=board_width, *args, **kwargs)
        
        self.all_pokemon = []
        path = os.path.dirname(os.path.abspath(__file__)) + '\\images\\pokemon_sprites\\' 
        for filepath in os.listdir(path): #add pokemons to list
            image = Image.open(path + filepath).resize((self._width, self._width)) 
            pokemon_image = ImageTk.PhotoImage(image)
            self.all_pokemon.append(pokemon_image)

        adj_nums = ['zero_adjacent.png', 'one_adjacent.png', 'two_adjacent.png', 'three_adjacent.png', 'four_adjacent.png', 'five_adjacent.png', 'six_adjacent.png', 'seven_adjacent.png', 'eight_adjacent.png']
        self.adjacent_numbers = []
        path2 = os.path.dirname(os.path.abspath(__file__)) + '\\images\\'
        for f in range (0, 9): #Add 9 images to list
            image = Image.open(path2 + adj_nums[f]).resize((self._width, self._width)) 
            adjacent = ImageTk.PhotoImage(image)
            self.adjacent_numbers.append(adjacent)

        pokeball = Image.open(os.path.dirname(os.path.abspath(__file__)) + '\\images\pokeball.png').resize((self._width, self._width))
        self._pokeball = ImageTk.PhotoImage(pokeball)

        unrevealed = Image.open(os.path.dirname(os.path.abspath(__file__)) + '\\images\\unrevealed.png').resize((self._width, self._width))
        self._unrevealed = ImageTk.PhotoImage(unrevealed)

    def draw_board(self, board):
        """Overriding draw_board method in BoardView class. Fills up the 2D game board with images. 
        If game character is unexposed, 'unrevealed' is displayed. If game character is a digit, 
        the appropriate digit image is displayed. If the game character is a flag, 
        a pokeball image is displayed and if the game character is a pokemon, 
        a randomised pokemon image is displayed at that cell location.

        Parameters:
            board (str): Current game string.
        """
        self.delete("all")
        for row in range(0, self._grid_size):
            for col in range(0, self._grid_size):
                x,y = self.position_to_pixel((row, col)) 
                index = self._grid_size * row + col 
                if board[index] == UNEXPOSED:
                    self.create_image(x,y, image = self._unrevealed)
                elif board[index].isdigit():
                    self.create_image(x,y, image=self.adjacent_numbers[int(board[index])])   
                elif board[index] == FLAG:
                    self.create_image(x,y, image=self._pokeball)
                elif board[index] == POKEMON:
                    self.create_image(x,y, image = random.choice(self.all_pokemon))
    
class StatusBar(tk.Frame):
    """Displays the status bar at the bottom of the game, including new game and restart button
    and also showing numbers of attempted catches, pokeballs left and how long game has been
    going for."""
    def __init__(self, master, *args, **kwargs):
        """Construct a new status bar frame.

        Parameters:
            master (tk.Widget): Widget within which to place the status bar.
        """
        super().__init__(master, *args, **kwargs)
        self._master = master
        self.full_pokeball = ImageTk.PhotoImage(Image.open(os.path.dirname(os.path.abspath(__file__)) + '\\images\\full_pokeball.png'))
        self.clock_image = ImageTk.PhotoImage(Image.open(os.path.dirname(os.path.abspath(__file__)) + '\\images\\clock.png'))

        self.button_frame = tk.Frame(self._master)
        self.button_frame.pack(side=tk.RIGHT)
        self.new_game_button = tk.Button(self.button_frame, text='New Game')
        self.new_game_button.pack(padx=56, pady=5)
        self.restart_game_button = tk.Button(self.button_frame,text='Restart Game')
        self.restart_game_button.pack(padx=50, pady=5)
        
        self.time_clock_frame = tk.Frame(self._master)
        self.time_clock_frame.pack(side=tk.RIGHT)
        self.time_clock = tk.Label(self.time_clock_frame)
        self.time_clock.pack(side=tk.RIGHT)
        self.clock = tk.Label(self.time_clock_frame, image=self.clock_image)
        self.clock.pack()
    
        self.pokeball_and_catches = tk.Frame(self._master)
        self.pokeball_and_catches.pack(side=tk.RIGHT, padx=50)
        self.attempted_catch = tk.Label(self.pokeball_and_catches)
        self.pokeball = tk.Label(self.pokeball_and_catches)
        self.pokeball_image = tk.Label(self.pokeball_and_catches, image=self.full_pokeball)
        self.pokeball_image.pack(side=tk.LEFT)


    def time(self, second):
        """Adding time elapsed to the status bar.
        
        Parameters:
            second (int): Time elapsed in second since the game begun.
        """
        minute = second//60
        seconds = second % 60
        self.time_clock.config(text='Time elapsed\n' + str(minute) + 'm ' + str(seconds)+'s', font=("Arial", 9))

class PokemonGame:
    """Pokemon game application that manages the communication between board model, board view,
    image board view and status bar. A file menu with following features was also implemented
    here:
        Save game: Saves the game to a file.
        Load game: Loads the appropriate game file.
        Restart game: Restarts the game, keeping the same pokemon locations.
        New game: New game with new pokemon locations.
        Quit game: Exits the game.
    """
    def __init__(self, master, grid_size=10, num_pokemon=15, task=TASK_ONE):
        """Construct a pokemon game app based on grid size and number of pokemon.

        Parameters:
            master (tk.Widget): The root window widget.
            grid_size (int): Size of the 2D game board grid.
            num_pokemon (int): Number of pokemons in the game.
            task (str): Task to have the appropriate features displayed.
        """
        self._master = master
        self._gridsize = grid_size
        self._num_pokemon = num_pokemon
        self._task = task
        self.label_and_root_config()
        self._BoardModel = BoardModel(self._gridsize,self._num_pokemon)
        
        if self._task == TASK_ONE:
            self._BoardView = BoardView(self._master, grid_size = self._gridsize, board_width=600)
            self.boardview_config()
        if self._task == TASK_TWO:
            self._BoardView = ImageBoardView(self._master, self._gridsize, board_width=600)
            self.boardview_config()

            self._StatusBar = StatusBar(self._master)
            self._StatusBar.pack(expand=1, fill=tk.BOTH)
            self._StatusBar.restart_game_button.bind("<Button-1>", self.restart_game)
            self._StatusBar.new_game_button.bind("<Button-1>", self.new_game)
            self.attempted_catches_and_pokeballs_left()
            self._timer = None
            self._time = 0
            self.update_clock()
           
            menu_bar = tk.Menu(self._master)
            self._master.config(menu = menu_bar)

            file_menu = tk.Menu(menu_bar, tearoff=False)
            menu_bar.add_cascade(label="File", menu=file_menu)

            file_menu.add_command(label="Save game", command = self.file_save_game)
            file_menu.add_command(label="Load game", command = self.file_load_game)
            file_menu.add_command(label="Restart game", command = self.reset)
            file_menu.add_command(label="New game", command = self.file_new_game)
            file_menu.add_command(label="Quit", command= self.file_quit_game)

        self.bind_mouse()
        self.game_display()

    def file_save_game(self):
        """Save the game as a text file.
        
        Returns None if no files were selected.
        """
        try:
            game_string = self._BoardModel.get_game()
            game_time = str(self._time) + '\n'
            p = self._BoardModel._pokemon_locations
            pokemon_locations = ','.join(map(str, p)) #Convert tuple to string of digits
            filename = filedialog.asksaveasfile(mode='w', defaultextension='.txt', filetypes=(("Text file", "*.txt"),("All files", "*.*")))
            if not filename:
                return

            filename.write(game_string)
            filename.write(game_time)
            filename.write(pokemon_locations)
            filename.close()
        except Exception as e:
            messagebox.showerror(title='Error', message=str(e)) 
            
    def file_load_game(self):
        """Loading up the saved game(text file only).
        
        Returns None if no file were selected."""
        try:
            filename = filedialog.askopenfilename()
            if not filename:
                return
            saved_game = open(filename, "r")
            line = saved_game.readlines()
            saved_game.close()

            pokemon_locations = tuple(list(map(int, line[1].split(',')))) #converts string of digits to one tuple
            self._num_pokemon = len(pokemon_locations)
            self._BoardModel._pokemon_locations = pokemon_locations

            num_character = len(line[0])
            grid_size=math.floor(math.sqrt(num_character))
            self._gridsize = grid_size

            time_character_count = num_character - grid_size**2 
            game_string = line[0][0:-time_character_count]
            time = int(line[0][-time_character_count:])

            self._BoardModel._game = game_string
            self._time = time
            self.game_display()
            self.attempted_catches_and_pokeballs_left()
         
        except PermissionError:
            messagebox.showerror(title='Permission error', message='You do not have permission') 
        except Exception as e:
            messagebox.showerror(title='Error', message=str(e))     

    def file_new_game(self):
        """Start a new game"""
        self._BoardModel._pokemon_locations = self._BoardModel.generate_pokemons()
        self.reset()
    def file_quit_game(self):
        """Quit the game. If yes, terminate. If no, do nothing"""
        response = messagebox.askyesno(title="Quit game", message="Are you sure you want to quit?")
        if response:
            self._master.destroy()
        else:
            pass

    def bind_mouse(self):
        """Binds mouse to game board"""
        self._BoardView.bind("<Button-1>", self.left_click)
        self._BoardView.bind("<Button-2>", self.right_click)
        self._BoardView.bind("<Button-3>", self.right_click)

    def reset(self):
        """resets the game, same pokemon locations"""
        if self._timer is not None:
                self._master.after_cancel(self._timer)
        for i in range(0, self._gridsize**2):
            self._BoardModel.replace_character_at_index(i, UNEXPOSED)
        self._time = 0
        self._timer = None
        self.update_clock()
        self.bind_mouse()
        self.game_display()
        self.attempted_catches_and_pokeballs_left()

    def restart_game(self, event):
        """Restart the game.

        Parameters:
            event (tk.event): Left mouse click.
        """
        self.reset()

    def new_game(self, event):
        """Restarts the game, new pokemon locations.
        
        Parameters:
            event (tk.event): Left mouse click.
        """
        self._BoardModel._pokemon_locations = self._BoardModel.generate_pokemons()
        self.reset()

    def update_clock(self):
        """Updates the time elapsed on status bar every second."""
        self._StatusBar.time(self._time)
        self._time += 1
        self._timer = self._master.after(1000, self.update_clock)
    
    def label_and_root_config(self):
        """Configures the PokemonGame label: "Pokemon: Got 2 Find Them All!" and packing it on
        root window.
        Configures the root window.
        """
        self._master.title("Pokemon: Got 2 Find Them All!")
        self._label = tk.Label(self._master, text = "Pokemon: Got 2 Find Them All!", bg='IndianRed2', fg='white', borderwidth=2.5, relief = "raised")
        self._label.config(font=("Arial", 20))
        self._label.pack(fill=tk.BOTH)
        
    def boardview_config(self):
        """Configures the 2D gameboard and attaching it to root window."""
        self._BoardView.config(width=self._BoardView._board_width, height=self._BoardView._board_width)
        self._BoardView.pack(expand=True, side=tk.TOP)

    def attempted_catches_and_pokeballs_left(self):
        """Calculates the number of pokeballs left. Places both number of attempted catches
        and pokeballs left on status bar."""
        pokeball_left = self._num_pokemon - self._BoardModel.get_num_attempted_catches()
        self._StatusBar.attempted_catch.config(text= str(self._BoardModel.get_num_attempted_catches()) +' attempted catches', font=("Arial", 9))
        self._StatusBar.attempted_catch.pack()
        self._StatusBar.pokeball.config(text= str(pokeball_left) + ' pokeballs left', font=("Arial", 9))
        self._StatusBar.pokeball.pack(side=tk.LEFT)

    def game_display(self):
        """Draws up the 2D game board based on current game string."""     
        self._BoardView.draw_board(self._BoardModel.get_game())

    def unbind_mouse(self):
        """Unbinds mouse from game board."""
        self._BoardView.unbind("<Button-1>")
        self._BoardView.unbind("<Button-2>")
        self._BoardView.unbind("<Button-3>")

    def win_or_lose_task1(self):
        """Displays win message if game is won, lose message if game is lost(task1). Also,
        unbinds mouse on either condition."""
        if self._BoardModel.check_win():
            self._BoardView.win_message_task1()
            self.unbind_mouse()

        if self._BoardModel.check_loss():
            self._BoardView.lose_message_task1()
            self.unbind_mouse()    

    def win_or_lose_task2(self):
        """Displays the win message and lose message appropriately. Unbinds mouse and stops
        all elements on status bar. If player wants to play again, initialise new game, if
        not, terminate."""
        if self._BoardModel.check_win():
            self.unbind_mouse()
            if self._timer is not None:
                self._master.after_cancel(self._timer)
            if self._BoardView.win_message_task2():
                self._BoardModel._pokemon_locations = self._BoardModel.generate_pokemons()
                self.reset()
            else:
                self._master.destroy()
                
        if self._BoardModel.check_loss():
            self.unbind_mouse()
            if self._timer is not None:
                self._master.after_cancel(self._timer)
            if self._BoardView.lose_message_task2():
                self._BoardModel._pokemon_locations = self._BoardModel.generate_pokemons()
                self.reset()
            else:
                self._master.destroy()
                
    def left_click(self, event):
        """Mouse left click 

        Parameters:
            event (tk.event): left clicking
        """
        x, y = event.x, event.y
        row, col = self._BoardView.pixel_to_positions((x, y))
        index = self._gridsize * row + col
        if index in self._BoardModel._pokemon_locations:
            for i in self._BoardModel._pokemon_locations:    
                self._BoardModel.replace_character_at_index(i, POKEMON)
                self.game_display()
        else:
            try:
                self._BoardModel.reveal_Cells(index)
                self.game_display()
            except:
                pass
        if self._task == TASK_ONE:
            self.win_or_lose_task1()
        elif self._task == TASK_TWO:
            self.win_or_lose_task2()

    def right_click(self, event):
        """Mouse left click 

        Parameters:
            event (tk.event): right clicking
        """
        pokeball_left = self._num_pokemon - self._BoardModel.get_num_attempted_catches()
        x, y = event.x, event.y
        row, col = self._BoardView.pixel_to_positions((x, y))
        index = self._gridsize * row + col
        if self._task == TASK_TWO:
            self.win_or_lose_task2() 
            if pokeball_left > 0 or self._BoardModel.get_game()[index] != UNEXPOSED:
                self._BoardModel.flag_cell(index)
                self.attempted_catches_and_pokeballs_left()
        elif self._task == TASK_ONE:
            self.win_or_lose_task1()
            self._BoardModel.flag_cell(index)
        self.game_display()
            
def main():
    """Main function"""
    root = tk.Tk()
    PokemonGame(root)
    root.update()
    root.mainloop()
    
if __name__ == '__main__':
    main()

