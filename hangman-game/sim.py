import sys
import pandas as pd
import streamlit as st
from collections import defaultdict

df = pd.read_csv("Database.csv")
word_database = df['Word'].tolist()
word_database = [word.lower() for word in df['Word'].tolist()]

def compute_letter_weights(word_database):
    total_letters = 0
    letter_counts = {char: 0 for char in 'abcdefghijklmnopqrstuvwxyz'}

    for word in word_database:
        word = word.lower()
        for letter in word:
            if letter in letter_counts:
                letter_counts[letter] += 1
                total_letters += 1

    letter_frequencies = {letter: (count / total_letters) * 100 for letter, count in letter_counts.items()}
    return letter_frequencies

letter_weights = compute_letter_weights(word_database)

class HangmanGame:
    def __init__(self, word_length):
        self.word_length = word_length
        self.state = "_" * word_length
        self.guesses = []

    def get_state(self):
        return self.state

    def guess(self, letter):
        self.guesses.append(letter)
        if letter in self.state:
            return True
        return False

    def update_state(self, letter):
        self.state = self.state.replace("_", letter, 1)

class EntropyBasedPlayer:
    def __init__(self, word_database):
        self.word_database = word_database
        self.already_guessed = []
        self.wrong_guesses = []

    def filter_words(self, current_state):
        word_length = len(current_state)
        potential_matches = [word for word in self.word_database if len(word) == word_length]
        #for i in potential_matches:
            #st.write(i)
        filtered_words = [word for word in potential_matches if self.matches_state(word, current_state)]
        #for i in filtered_words:
            #st.write(i)
        return filtered_words

    def next_guess(self, current_state):
        potential_matches = self.filter_words(current_state)
        if not potential_matches:
            return None

        position_to_guess = current_state.index("_")
        frequency_distribution = defaultdict(int)
        for word in potential_matches:
            letter = word[position_to_guess]
            if letter not in self.already_guessed:
                frequency_distribution[letter] += 1

        if not frequency_distribution:
            return None

        guess = max(frequency_distribution, key=lambda k: (frequency_distribution[k], letter_weights.get(k, 0)))
        self.already_guessed.append(guess)
        return guess

    def matches_state(self, word, state):
    
        for w, s in zip(word, state):
            if s != '_' and w.lower() != s.lower():
                return False
    
        position = state.index('_')

        if word[position] in self.wrong_guesses:
            return False
        
        return True

    def reset_guessed(self):
        self.already_guessed = []
        self.wrong_guesses = []

class CowHangman:
    def __init__(self):
        self.lives = 6
        self.cow_parts = [
            '''
        ^__^

        (oo)


        ''',
            '''
        ^__^

        (oo)\\_______


        ''',
            '''
        ^__^

        (oo)\\_______

        (__)\\       


        ''',
            '''
        ^__^

        (oo)\\_______

        (__)\\       )\\/\\


        ''',
            '''
        ^__^

        (oo)\\_______

        (__)\\       )\\/\\

            ||----w |
            

        ''',
            '''
        ^__^

        (oo)\\_______

        (__)\\       )\\/\\

            ||----w |
            ||     ||

        '''
        ]



    def display_cow(self):
        parts_to_display = min(5, 6 - self.lives)
        for line in self.cow_parts[parts_to_display].split('\n'):
            st.write(line)


    def lose_life(self):
        if self.lives > 0:
            self.lives -= 1
            self.display_cow()
        else:
            st.write("No more lives!")

    def is_game_over(self):
        return self.lives <= 0

    def display(self):
        return f"Lives left: {self.lives}"

def play_game(target_word):
    hangman = HangmanGame(len(target_word))
    player = EntropyBasedPlayer(word_database)
    cow_game = CowHangman()

    while "_" in hangman.get_state() and not cow_game.is_game_over():
        col1, col2 = st.columns(2)

        col1.write(f"Current state: {hangman.get_state()}")
        col2.write(cow_game.display())

        ai_guess = player.next_guess(hangman.get_state())
        if ai_guess:
            st.write(f"AI's guess is: {ai_guess}")

            current_pos = hangman.get_state().index("_")
            if target_word[current_pos].lower() == ai_guess:
                st.write("Right guess!")
                hangman.update_state(ai_guess.upper())
                player.reset_guessed()
            else:
                st.write("Wrong guess!")
                player.wrong_guesses.append(ai_guess)
                cow_game.lose_life()
        else:
            st.write("AI is out of guesses.")
            break
    
    if "_" not in hangman.get_state():
        st.write("Congratulations! The AI successfully guessed the word!")
    elif cow_game.is_game_over():
        st.write("Game Over. The AI couldn't guess the word.")
