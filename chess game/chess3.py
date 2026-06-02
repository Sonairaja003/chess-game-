import tkinter as tk
from tkinter import messagebox
import chess
import random

# ==============================
# CHESS GAME CONFIGURATION
# ==============================

BOARD_SIZE = 8
CELL_SIZE = 60

LIGHT_TILE = "#EEEED2"
DARK_TILE = "#769656"

PIECE_SYMBOLS = {
    'r': '♜', 'n': '♞', 'b': '♝',
    'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♖', 'N': '♘', 'B': '♗',
    'Q': '♕', 'K': '♔', 'P': '♙'
}


# ==============================
# MAIN APPLICATION
# ==============================

class ChessApplication:

    def __init__(self, master):

        self.master = master
        self.master.title("Professional Chess")
        self.master.geometry("920x560")
        self.master.resizable(False, False)

        # Game Data
        self.board = chess.Board()
        self.selected_square = None
        self.move_markers = []

        self.game_mode = "CPU"

        self.captured_white = []
        self.captured_black = []

        # ==============================
        # CHESS BOARD
        # ==============================

        self.canvas = tk.Canvas(
            self.master,
            width=480,
            height=480,
            highlightthickness=0
        )
        self.canvas.place(x=20, y=40)

        # ==============================
        # SIDE PANEL
        # ==============================

        self.sidebar = tk.Frame(
            self.master,
            width=360,
            height=520,
            bg="#1F1F1F"
        )
        self.sidebar.place(x=530, y=20)

        self.turn_label = tk.Label(
            self.sidebar,
            text="White Turn",
            fg="#FFD700",
            bg="#1F1F1F",
            font=("Segoe UI", 15, "bold")
        )
        self.turn_label.pack(pady=15)

        # Captured Pieces Section
        tk.Label(
            self.sidebar,
            text="Captured By Black",
            fg="white",
            bg="#1F1F1F",
            font=("Segoe UI", 11)
        ).pack()

        self.white_capture_label = tk.Label(
            self.sidebar,
            text="",
            fg="#FF5C5C",
            bg="#1F1F1F",
            font=("Arial", 16)
        )
        self.white_capture_label.pack(pady=5)

        tk.Label(
            self.sidebar,
            text="Captured By White",
            fg="white",
            bg="#1F1F1F",
            font=("Segoe UI", 11)
        ).pack()

        self.black_capture_label = tk.Label(
            self.sidebar,
            text="",
            fg="#66D9EF",
            bg="#1F1F1F",
            font=("Arial", 16)
        )
        self.black_capture_label.pack(pady=5)

        # Buttons
        self.create_buttons()

        # Mouse Binding
        self.canvas.bind("<Button-1>", self.handle_click)

        # Initial Draw
        self.draw_board()

    # ==============================
    # BUTTONS
    # ==============================

    def create_buttons(self):

        button_style = {
            "width": 22,
            "font": ("Segoe UI", 10, "bold"),
            "bg": "#333",
            "fg": "white",
            "activebackground": "#555",
            "activeforeground": "white",
            "bd": 0,
            "pady": 8
        }

        tk.Button(
            self.sidebar,
            text="Restart Game",
            command=self.restart_game,
            **button_style
        ).pack(pady=8)

        tk.Button(
            self.sidebar,
            text="Change Board Theme",
            command=self.change_theme,
            **button_style
        ).pack(pady=8)

        tk.Button(
            self.sidebar,
            text="Toggle CPU / Player",
            command=self.toggle_mode,
            **button_style
        ).pack(pady=8)

        tk.Button(
            self.sidebar,
            text="Exit Game",
            command=self.master.quit,
            bg="#A93226",
            fg="white",
            width=22,
            font=("Segoe UI", 10, "bold"),
            bd=0,
            pady=8
        ).pack(pady=8)

    # ==============================
    # BOARD DRAWING
    # ==============================

    def draw_board(self):

        self.canvas.delete("all")

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                color = (
                    LIGHT_TILE
                    if (row + col) % 2 == 0
                    else DARK_TILE
                )

                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE

                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=color
                )

        self.draw_pieces()

    def draw_pieces(self):

        for square in chess.SQUARES:

            piece = self.board.piece_at(square)

            if piece:

                row = 7 - chess.square_rank(square)
                col = chess.square_file(square)

                self.canvas.create_text(
                    col * CELL_SIZE + 30,
                    row * CELL_SIZE + 30,
                    text=PIECE_SYMBOLS[str(piece)],
                    font=("Arial", 32)
                )

    # ==============================
    # GAME HELPERS
    # ==============================

    def get_square_from_mouse(self, x, y):

        file = x // CELL_SIZE
        rank = 7 - (y // CELL_SIZE)

        return chess.square(file, rank)

    def update_capture_display(self):

        self.white_capture_label.config(
            text=" ".join(self.captured_white)
        )

        self.black_capture_label.config(
            text=" ".join(self.captured_black)
        )

    def show_legal_moves(self, square):

        self.move_markers.clear()

        for move in self.board.legal_moves:

            if move.from_square == square:

                target = move.to_square

                row = 7 - chess.square_rank(target)
                col = chess.square_file(target)

                marker_color = (
                    "#FF4C4C"
                    if self.board.piece_at(target)
                    else "#3498DB"
                )

                marker = self.canvas.create_oval(
                    col * CELL_SIZE + 18,
                    row * CELL_SIZE + 18,
                    col * CELL_SIZE + 42,
                    row * CELL_SIZE + 42,
                    fill=marker_color,
                    outline=""
                )

                self.move_markers.append((marker, move))

    # ==============================
    # GAME EVENTS
    # ==============================

    def handle_click(self, event):

        if self.board.is_game_over():
            return

        x, y = event.x, event.y
        clicked_square = self.get_square_from_mouse(x, y)

        # Move Selection
        for item in self.canvas.find_overlapping(x, y, x, y):

            for marker, move in self.move_markers:

                if item == marker:

                    self.execute_move(move)
                    return

        # Piece Selection
        piece = self.board.piece_at(clicked_square)

        if piece and piece.color == self.board.turn:

            self.selected_square = clicked_square

            self.draw_board()
            self.show_legal_moves(clicked_square)

    # ==============================
    # MOVE EXECUTION
    # ==============================

    def execute_move(self, move):

        if self.board.is_capture(move):

            captured_piece = self.board.piece_at(move.to_square)

            if captured_piece:

                if captured_piece.color == chess.WHITE:
                    self.captured_white.append(
                        PIECE_SYMBOLS[str(captured_piece)]
                    )
                else:
                    self.captured_black.append(
                        PIECE_SYMBOLS[str(captured_piece)]
                    )

                self.update_capture_display()

        self.board.push(move)

        self.draw_board()

        self.turn_label.config(
            text="White Turn"
            if self.board.turn == chess.WHITE
            else "Black Turn"
        )

        if self.board.is_game_over():
            self.show_game_over()
            return

        # CPU Move
        if self.game_mode == "CPU" and self.board.turn == chess.BLACK:
            self.master.after(500, self.cpu_move)

    # ==============================
    # CPU LOGIC
    # ==============================

    def cpu_move(self):

        if self.board.is_game_over():
            self.show_game_over()
            return

        move = random.choice(list(self.board.legal_moves))

        self.execute_move(move)

    # ==============================
    # GAME OVER
    # ==============================

    def show_game_over(self):

        result = self.board.result()

        popup = tk.Toplevel(self.master)
        popup.title("Game Over")
        popup.geometry("420x220")
        popup.configure(bg="#111")
        popup.grab_set()

        tk.Label(
            popup,
            text="GAME OVER",
            fg="#FF3B30",
            bg="#111",
            font=("Segoe UI", 28, "bold")
        ).pack(pady=25)

        tk.Label(
            popup,
            text=f"Match Result : {result}",
            fg="white",
            bg="#111",
            font=("Segoe UI", 15)
        ).pack()

    # ==============================
    # OPTIONS
    # ==============================

    def restart_game(self):

        self.board.reset()

        self.captured_white.clear()
        self.captured_black.clear()

        self.update_capture_display()

        self.turn_label.config(text="White Turn")

        self.draw_board()

    def toggle_mode(self):

        self.game_mode = (
            "PVP"
            if self.game_mode == "CPU"
            else "CPU"
        )

        messagebox.showinfo(
            "Game Mode",
            f"Current Mode : {self.game_mode}"
        )

    def change_theme(self):

        global LIGHT_TILE, DARK_TILE

        LIGHT_TILE = "#F8F8F8"
        DARK_TILE = "#404040"

        self.draw_board()


# ==============================
# START APPLICATION
# ==============================

if __name__ == "__main__":

    root = tk.Tk()

    app = ChessApplication(root)

    root.mainloop()