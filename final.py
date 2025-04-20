import tkinter as tk
from tkinter import font, ttk
import time
import threading
import random
from tkinter import messagebox
import numpy as np
import tensorflow as tf
from collections import deque
import json
import os

tf.compat.v1.enable_eager_execution()
tf.config.run_functions_eagerly(True)  # Ensure eager execution for debugging
tf.data.experimental.enable_debug_mode()  # Enable debug mode for tf.data functions

class MainPage(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Typing Master")
        self.geometry("750x615")
        self.resizable(False, False)
        
        # Custom color scheme
        self.bg_color = "#F5F7FA"           # Very light grayish-blue background
        self.primary_color = "#1F2937"      # Deep navy/charcoal for main text (great contrast)
        self.secondary_color = "#3B82F6"    # Button background (blue, vibrant and inviting)
        self.accent_color = "#2563EB"       # Button hover (slightly darker blue)
        self.text_color = "#111827"         # Darker text color for strong readability

        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TButton", 
                             font=("Helvetica", 12),
                             padding=10,
                             background=self.secondary_color,
                             foreground=self.primary_color)  # Black button text
        self.style.map("TButton",
                       background=[("active", self.accent_color)],
                       foreground=[("active", self.primary_color)])  # Black text on hover
        
        self.titlefont = font.Font(family="Helvetica", size=24, weight="bold")
        self.subtitlefont = font.Font(family="Helvetica", size=16)
        
        container = ttk.Frame(self, style="TFrame")
        container.pack(fill="both", expand=True)
        
        self.frames = {}
        for F in (WelcomePage, TypingTestPageShort, TypingTestPageMedium, TypingTestPageLong, StatsPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("WelcomePage")
    
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class WelcomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(style="TFrame")
        
        # Header
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.pack(pady=20, expand=True)
        
        tk.Label(header_frame, 
                text="Typing Master", 
                font=controller.titlefont,
                foreground=controller.primary_color,
                background=controller.bg_color,
                justify="center").pack(anchor="center")  # Centered
        
        tk.Label(header_frame, 
                text="Improve your typing speed and accuracy.\nBy Mahdi and Karim", 
                font=controller.subtitlefont,
                foreground=controller.primary_color,
                background=controller.bg_color,
                justify="center").pack(pady=10, anchor="center")  # Centered
        
        # Options frame
        options_frame = ttk.Frame(self, style="TFrame")
        options_frame.pack(pady=30, expand=True)
        
        tk.Label(options_frame, 
                text="Choose text length:", 
                font=controller.subtitlefont,
                foreground=controller.primary_color,
                background=controller.bg_color,
                justify="center").pack(pady=10, anchor="center")  # Centered
        
        # Horizontal layout for word length buttons
        button_frame = ttk.Frame(options_frame, style="TFrame")
        button_frame.pack(pady=10, expand=True)
        
        button_short = ttk.Button(button_frame, 
                                text="Short Texts", 
                                command=lambda: controller.show_frame("TypingTestPageShort"))
        button_short.pack(side="left", padx=10, ipadx=20, ipady=10)
        
        button_medium = ttk.Button(button_frame, 
                                 text="Medium Texts", 
                                 command=lambda: controller.show_frame("TypingTestPageMedium"))
        button_medium.pack(side="left", padx=10, ipadx=20, ipady=10)
        
        button_long = ttk.Button(button_frame, 
                               text="Long Texts", 
                               command=lambda: controller.show_frame("TypingTestPageLong"))
        button_long.pack(side="left", padx=10, ipadx=20, ipady=10)
        
        # Stats button below the word length buttons
        stats_button = ttk.Button(options_frame,
                                text="View Stats",
                                command=lambda: controller.show_frame("StatsPage"))
        stats_button.pack(pady=20, ipadx=20, ipady=10, anchor="center")
        
        # Footer
        footer_frame = ttk.Frame(self, style="TFrame")
        footer_frame.pack(side="bottom", pady=20, expand=True)
        tk.Label(footer_frame, 
                text="All rights reserved © 2025", 
                font=("Helvetica", 10),
                foreground=controller.primary_color,
                background=controller.bg_color,
                justify="center").pack(anchor="center")  # Centered

class TypingTestBase(ttk.Frame):
    def __init__(self, parent, controller, text_type):
        super().__init__(parent)
        self.controller = controller
        self.configure(style="TFrame")
        
        # Header
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.pack(fill="x", pady=10)
        
        self.back_button = ttk.Button(header_frame, 
                                    text="← Back", 
                                    command=lambda: controller.show_frame("WelcomePage"))
        self.back_button.pack(side="left", padx=10)
        
        self.title_label = tk.Label(header_frame, 
                                  text=f"Typing Test - {text_type.capitalize()}", 
                                  font=controller.titlefont,
                                  foreground=controller.primary_color,
                                  background=controller.bg_color,
                                  justify="center")
        self.title_label.pack(side="left", expand=True)
        
        # Progress bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(pady=5)
        
        # Main content
        self.typing_test = TypeSpeedGUI(self, text_type, self.progress)  # Pass progress bar
        self.typing_test.pack(pady=20)

class TypingTestPageShort(TypingTestBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "short")

class TypingTestPageMedium(TypingTestBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "medium")

class TypingTestPageLong(TypingTestBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "long")

class StatsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(style="TFrame")
        
        # Header
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.pack(pady=10)  # Reduced padding
        
        tk.Label(header_frame, 
                text="Your Performance Stats", 
                font=controller.titlefont,
                foreground=controller.primary_color,
                background=controller.bg_color,
                justify="center").pack(anchor="center")
        
        # Stats display
        self.stats_text = tk.Text(self, height=8, width=50, wrap=tk.WORD,  # Reduced height and width
                                font=("Helvetica", 12),
                                background=controller.bg_color,
                                foreground=controller.primary_color)
        self.stats_text.pack(pady=10, padx=10)  # Reduced padding
        self.stats_text.config(state=tk.DISABLED)
        
        self.update_stats()
        
        # Buttons
        button_frame = ttk.Frame(self, style="TFrame")
        button_frame.pack(pady=5)  # Reduced padding
        
        back_button = ttk.Button(button_frame, 
                               text="Back to Welcome Page", 
                               command=lambda: controller.show_frame("WelcomePage"))
        back_button.pack(side="left", padx=5)
        
        reset_button = ttk.Button(button_frame,
                                text="Reset Stats",
                                command=self.reset_stats)
        reset_button.pack(side="left", padx=5)
    
    def update_stats(self):
        try:
            with open('typing_stats.json', 'r') as f:
                stats = json.load(f)
            
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            
            # Calculate averages
            total_sessions = len(stats['sessions'])
            if total_sessions > 0:
                avg_wpm = sum(s['wpm'] for s in stats['sessions']) / total_sessions
                avg_accuracy = sum(s['accuracy'] for s in stats['sessions']) / total_sessions
                avg_reaction = sum(s['avg_reaction_time'] for s in stats['sessions']) / total_sessions
                
                self.stats_text.insert(tk.END, f"Total Sessions: {total_sessions}\n")
                self.stats_text.insert(tk.END, f"Average WPM: {avg_wpm:.2f}\n")
                self.stats_text.insert(tk.END, f"Average Accuracy: {avg_accuracy:.2f}%\n")
                self.stats_text.insert(tk.END, f"Average Reaction Time: {avg_reaction:.2f} sec\n\n")
                
                # AI recommendations
                if avg_wpm < 30:
                    self.stats_text.insert(tk.END, "AI Suggestion: Focus on accuracy first, then gradually increase speed.\n")
                elif avg_wpm < 50:
                    self.stats_text.insert(tk.END, "AI Suggestion: Practice with medium-length texts to build consistency.\n")
                else:
                    self.stats_text.insert(tk.END, "AI Suggestion: Challenge yourself with long texts and complex vocabulary.\n")
                
                if avg_accuracy < 90:
                    self.stats_text.insert(tk.END, "AI Suggestion: Slow down to improve accuracy. Speed will come naturally.\n")
                
                # Recent sessions
                self.stats_text.insert(tk.END, "\nRecent Sessions:\n")
                for session in stats['sessions'][-5:]:
                    self.stats_text.insert(tk.END, 
                        f"{session['date']}: {session['wpm']:.1f} WPM, {session['accuracy']:.1f}% accuracy\n")
            else:
                self.stats_text.insert(tk.END, "No data available yet. Complete some typing tests first!")
            
            self.stats_text.config(state=tk.DISABLED)
        except FileNotFoundError:
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "No data available yet. Complete some typing tests first!")
            self.stats_text.config(state=tk.DISABLED)

    def reset_stats(self):
        """Reset the stats by clearing the typing_stats.json file."""
        try:
            with open('typing_stats.json', 'w') as f:
                json.dump({'sessions': [], 'performance_history': [], 'user_level': 1}, f, indent=2)
            messagebox.showinfo("Reset Stats", "All stats have been reset successfully!")
            self.update_stats()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset stats: {e}")

class TypeSpeedGUI(ttk.Frame):
    TEXT_SAMPLES = {
        "short": [
            "The quick brown fox jumps over the lazy dog.",
            "Python is an interpreted, high-level programming language.",
            "Practice makes perfect when learning to type quickly.",
            "Coding requires both logic and creativity to solve problems.",
            "Keyboard proficiency improves overall computer efficiency.",
            "Typing speed is measured in words per minute (WPM).",
            "The QWERTY keyboard layout was designed in the 1870s.",
            "Regular practice is key to improving typing skills.",
            "Accuracy is more important than speed when starting out.",
            "Most programmers type between 40 and 70 words per minute."
        ],
        "medium": [
            "The quick brown fox jumps over the lazy dog. This classic pangram contains every letter in the English alphabet and is perfect for typing practice. Consistent practice can help you develop muscle memory for faster typing.",
            "Python programming emphasizes code readability with its clean syntax and significant whitespace. The language's design philosophy focuses on simplicity and consistency, making it ideal for beginners and experts alike.",
            "Touch typing involves typing without looking at the keyboard, using all ten fingers. This method increases speed and reduces errors. The home row keys (ASDF for left hand, JKL; for right hand) serve as the base position.",
            "Ergonomic keyboards are designed to minimize strain and reduce the risk of repetitive stress injuries. Proper typing posture includes keeping your wrists straight, elbows at 90 degrees, and feet flat on the floor.",
            "The average typing speed is about 40 words per minute, while professional typists often reach 65-75 WPM. Some advanced typists can exceed 120 WPM with high accuracy through dedicated practice."
        ],
        "long": [
            "The quick brown fox jumps over the lazy dog. This well-known pangram has been used for typing practice since the early days of typewriters. Mastering typing is an essential skill in today's digital world where much of our communication and work happens through written text. Professionals who can type quickly and accurately have a significant advantage in many careers, especially in fields like programming, data entry, journalism, and content creation. The benefits of touch typing extend beyond speed - it reduces cognitive load, minimizes errors, and allows you to focus on content rather than the mechanics of typing.",
            "Python was created by Guido van Rossum and first released in 1991. It has grown to become one of the most popular programming languages worldwide due to its simplicity and versatility. Python's extensive standard library and vibrant ecosystem of third-party packages make it suitable for web development, scientific computing, data analysis, artificial intelligence, and more. The language's design philosophy emphasizes code readability through significant whitespace and a clean syntax that almost resembles pseudocode. Python's community is known for being welcoming to beginners while still offering powerful features for advanced users. The annual Stack Overflow developer survey consistently ranks Python among the most loved and wanted programming languages."
        ]
    }

    # Difficulty levels (word complexity multipliers)
    DIFFICULTY_LEVELS = {
        1: 0.8,  # Easier - shorter words, more common vocabulary
        2: 1.0,  # Normal
        3: 1.2,  # Harder - longer words, more complex vocabulary
        4: 1.5,  # Expert - technical terms, complex sentences
        5: 2.0   # Challenge - very long words, specialized vocabulary
    }

    def __init__(self, parent, text_type, progress):
        super().__init__(parent)
        self.controller = parent.controller
        self.progress = progress  # Store the progress bar reference
        self.text_type = text_type
        self.configure(style="TFrame")
        
        # Initialize performance tracking
        self.reaction_times = deque(maxlen=10)  # Track last 10 reaction times
        self.accuracy_history = deque(maxlen=10)  # Track last 10 accuracy values
        self.current_difficulty = 2  # Start with normal difficulty
        self.session_count = 0
        
        # Load or create neural network model
        self.model = self.load_or_create_model()
        
        # Load or initialize stats
        self.stats = self.load_stats()
        
        # UI Elements
        self.create_ui()
        
        # AI Feedback timer
        self.ai_feedback_timer = None
        self.last_feedback_time = 0
        
        self.running = False
        self.completed = False
        self.start_time = None
        self.last_key_time = None
        self.correct_chars = 0
        self.total_chars = 0
    
    def create_ui(self):
        # Define custom styles for LabelFrames
        self.controller.style.configure("Custom.TLabelframe", background="#ffffff")
        self.controller.style.configure("Custom.TLabelframe.Label", foreground="#000000", font=("Helvetica", 12, "bold"))
        
        # Difficulty and feedback labels
        self.difficulty_frame = ttk.Frame(self)
        self.difficulty_frame.pack(fill="x", pady=5)
        
        self.difficulty_label = tk.Label(self.difficulty_frame, 
                                       text=f"Difficulty Level: {self.current_difficulty}/5", 
                                       font=("Helvetica", 14),
                                       foreground=self.controller.primary_color,
                                       background=self.controller.bg_color)
        self.difficulty_label.pack(side="left", padx=10)
        
        self.feedback_label = tk.Label(self.difficulty_frame, 
                                     text="AI Feedback: Ready when you are!", 
                                     font=("Helvetica", 12), 
                                     wraplength=500,
                                     foreground="blue",
                                     background=self.controller.bg_color)
        self.feedback_label.pack(side="right", padx=10, fill="x", expand=True)
        
        # Sample text display
        self.sample_frame = ttk.Frame(self)
        self.sample_frame.pack(fill="x", pady=10)
        
        self.sample_label = tk.Label(self.sample_frame, 
                                     font=("Helvetica", 16), 
                                     wraplength=700,
                                     justify="center",  # Center text
                                     background="#ffffff",  # White background
                                     foreground="#000000",  # Black text
                                     relief="solid",
                                     padx=10,
                                     pady=10,
                                     borderwidth=1)
        self.sample_label.pack(fill="x", anchor="center")  # Centered
        self.sample_label.config(text=self.select_text_based_on_difficulty())
        
        # Input area
        self.input_frame = ttk.Frame(self)
        self.input_frame.pack(fill="x", pady=10)
        
        self.input_entry = tk.Entry(self.input_frame, 
                                    font=("Helvetica", 18), 
                                    width=50,
                                    relief="solid",
                                    borderwidth=1,
                                    justify="center")  # Center text in the entry
        self.input_entry.pack(fill="x", anchor="center")  # Centered
        self.input_entry.bind("<KeyRelease>", self.start)
        self.input_entry.focus_set()
        
        # Stats frame
        self.stats_frame = ttk.Frame(self)
        self.stats_frame.pack(fill="x", pady=20)
        
        # Speed display
        self.speed_frame = ttk.LabelFrame(self.stats_frame, text="Typing Speed", style="Custom.TLabelframe")
        self.speed_frame.pack(side="left", padx=10, fill="both", expand=True)
        
        self.wpm_label = tk.Label(self.speed_frame, 
                                  text="0.00", 
                                  font=("Helvetica", 24, "bold"),
                                  foreground="#000000",  # Black text
                                  background="#ffffff")  # White background
        self.wpm_label.pack(anchor="center")  # Centered
        
        tk.Label(self.speed_frame, 
                 text="Words Per Minute", 
                 font=("Helvetica", 10),
                 foreground="#000000",  # Black text
                 background="#ffffff").pack(anchor="center")  # Centered
        
        # Accuracy display
        self.accuracy_frame = ttk.LabelFrame(self.stats_frame, text="Accuracy", style="Custom.TLabelframe")
        self.accuracy_frame.pack(side="left", padx=10, fill="both", expand=True)
        
        self.accuracy_label = tk.Label(self.accuracy_frame, 
                                       text="100%", 
                                       font=("Helvetica", 24, "bold"),
                                       foreground="#000000",  # Black text
                                       background="#ffffff")  # White background
        self.accuracy_label.pack(anchor="center")  # Centered
        
        tk.Label(self.accuracy_frame, 
                 text="Keystroke Accuracy", 
                 font=("Helvetica", 10),
                 foreground="#000000",  # Black text
                 background="#ffffff").pack(anchor="center")  # Centered
        
        # Time display
        self.time_frame = ttk.LabelFrame(self.stats_frame, text="Time", style="Custom.TLabelframe")
        self.time_frame.pack(side="left", padx=10, fill="both", expand=True)
        
        self.time_label = tk.Label(self.time_frame, 
                                   text="0.00s", 
                                   font=("Helvetica", 24, "bold"),
                                   foreground="#000000",  # Black text
                                   background="#ffffff")  # White background
        self.time_label.pack(anchor="center")  # Centered
        
        tk.Label(self.time_frame, 
                 text="Elapsed Time", 
                 font=("Helvetica", 10),
                 foreground="#000000",  # Black text
                 background="#ffffff").pack(anchor="center")  # Centered
        
        # Reaction time display
        self.reaction_frame = ttk.LabelFrame(self.stats_frame, text="Reaction", style="Custom.TLabelframe")
        self.reaction_frame.pack(side="left", padx=10, fill="both", expand=True)
        
        self.reaction_label = tk.Label(self.reaction_frame, 
                                       text="0.00s", 
                                       font=("Helvetica", 24, "bold"),
                                       foreground="#000000",  # Black text
                                       background="#ffffff")  # White background
        self.reaction_label.pack(anchor="center")  # Centered
        
        tk.Label(self.reaction_frame, 
                 text="Avg. Reaction Time", 
                 font=("Helvetica", 10),
                 foreground="#000000",  # Black text
                 background="#ffffff").pack(anchor="center")  # Centered
        
        # Control buttons
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(fill="x", pady=10)
        
        self.reset_button = ttk.Button(self.button_frame, 
                                       text="New Text", 
                                       command=self.reset)
        self.reset_button.pack(side="left", padx=5, anchor="center")  # Centered
    
    def load_text_samples(self, text_type):
        """Load text samples and preprocess them for difficulty levels"""
        base_texts = self.TEXT_SAMPLES[text_type]
        enhanced_texts = []
        
        # Create multiple difficulty versions of each text
        for text in base_texts:
            words = text.split()
            for diff_level in range(1, 6):
                # Adjust text based on difficulty level
                modified_words = []
                for word in words:
                    if diff_level >= 4 and len(word) < 5 and random.random() > 0.7:
                        # For higher difficulties, sometimes replace short words with longer ones
                        modified_words.append(self.get_complex_word())
                    else:
                        modified_words.append(word)
                
                # For highest difficulty, make sentences more complex
                if diff_level == 5:
                    modified_text = " ".join(modified_words)
                    if not any(p in modified_text for p in [",", ";", ":"]):
                        parts = modified_text.split(". ")
                        if len(parts) > 1:
                            modified_text = ", ".join(parts[:-1]) + "; " + parts[-1]
                    enhanced_texts.append(modified_text)
                else:
                    enhanced_texts.append(" ".join(modified_words))
        
        return enhanced_texts
    
    def get_complex_word(self):
        """Get a more complex word from a predefined list"""
        complex_words = [
            "algorithm", "binary", "compiler", "debugging", "encapsulation",
            "framework", "inheritance", "javascript", "kernel", "lambda",
            "multithreading", "namespace", "object", "polymorphism", "query",
            "recursion", "syntax", "template", "utility", "variable"
        ]
        return random.choice(complex_words)
    
    def load_or_create_model(self):
        """Load existing model or create a new one"""
        try:
            if os.path.exists('typing_model.keras'):
                # Load the model
                model = tf.keras.models.load_model('typing_model.keras')
                print("Loaded existing model")
                
                # Recompile the model to reset the optimizer
                model.compile(optimizer='adam', loss=tf.keras.losses.MeanSquaredError())
            else:
                model = self.create_new_model()
                print("Created new model")
            return model
        except Exception as e:
            print(f"Error loading/creating model: {e}")
            return self.create_new_model()

    def create_new_model(self):
        """Create a new neural network model"""
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(3,)),  # Explicitly define the input shape
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(8, activation='relu'),
            tf.keras.layers.Dense(1, activation='linear')
        ])
        model.compile(optimizer='adam', loss=tf.keras.losses.MeanSquaredError())  # Use the class explicitly
        return model
    
    def load_stats(self):
        """Load or initialize statistics"""
        try:
            if os.path.exists('typing_stats.json'):
                with open('typing_stats.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        
        # Return default stats if file doesn't exist or error
        return {
            'sessions': [],
            'performance_history': [],
            'user_level': 1
        }
    
    def save_stats(self):
        """Save statistics to file"""
        try:
            with open('typing_stats.json', 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def select_text_based_on_difficulty(self):
        """Select text based on current difficulty level"""
        # Filter texts that match current difficulty profile
        suitable_texts = []
        for text in self.TEXT_SAMPLES[self.text_type]:
            avg_word_len = sum(len(word) for word in text.split()) / len(text.split())
            complexity = avg_word_len * len([c for c in text if c in ',;:'])
            
            # Simple heuristic to match text to difficulty level
            text_diff = min(5, max(1, int(complexity / 5 + 1)))
            
            if text_diff == self.current_difficulty:
                suitable_texts.append(text)
        
        if suitable_texts:
            return random.choice(suitable_texts)
        return random.choice(self.TEXT_SAMPLES[self.text_type])  # Fallback
    
    def start(self, event):
        if self.completed:
            return

        # Track reaction time (time between key presses)
        current_time = time.time()
        if self.last_key_time is not None and event.keycode not in [16, 17, 18]:  # Ignore modifier keys
            reaction_time = current_time - self.last_key_time
            self.reaction_times.append(reaction_time)
            self.reaction_label.config(text=f"{np.mean(self.reaction_times):.2f}s" if self.reaction_times else "0.00s")
        self.last_key_time = current_time

        if not self.running:
            if event.keycode not in [16, 17, 18]:  # Ignore Shift, Ctrl, Alt keys
                self.running = True
                self.start_time = time.time()
                self.thread = threading.Thread(target=self.time_thread, daemon=True)
                self.thread.start()
                self.schedule_ai_feedback()

        # Calculate accuracy
        sample_text = self.sample_label.cget("text")
        input_text = self.input_entry.get()
        self.total_chars = len(sample_text)
        
        correct = 0
        for i, (s, t) in enumerate(zip(sample_text, input_text)):
            if s == t:
                correct += 1
        self.correct_chars = correct
        
        accuracy = (correct / len(input_text)) * 100 if input_text else 0
        self.accuracy_history.append(accuracy)
        self.accuracy_label.config(text=f"{accuracy:.1f}%")

        # Update progress
        progress = (len(input_text) / len(sample_text)) * 100
        progress = min(progress, 100)  # Clamp progress to 100%
        self.progress["value"] = progress

        # Visual feedback
        if not sample_text.startswith(input_text):
            self.input_entry.config(fg="red")
        else:
            self.input_entry.config(fg="black")

        # Check for completion
        if input_text == sample_text:
            self.complete_test()
    
    def complete_test(self):
        """Handle test completion"""
        self.running = False
        self.completed = True
        self.input_entry.config(fg="green")
        self.input_entry.config(state="readonly")
        
        # Calculate final stats
        elapsed_time = time.time() - self.start_time
        wps = len(self.input_entry.get().split()) / elapsed_time
        wpm = wps * 60
        accuracy = (self.correct_chars / self.total_chars) * 100
        
        # Update session stats
        session_data = {
            'date': time.strftime("%Y-%m-%d %H:%M:%S"),
            'wpm': wpm,
            'accuracy': accuracy,
            'difficulty': self.current_difficulty,
            'text_type': self.text_type,
            'elapsed_time': elapsed_time,
            'avg_reaction_time': np.mean(self.reaction_times) if self.reaction_times else 0
        }
        
        self.stats['sessions'].append(session_data)
        self.stats['performance_history'].append({
            'wpm': wpm,
            'accuracy': accuracy,
            'reaction_time': session_data['avg_reaction_time'],
            'difficulty': self.current_difficulty
        })
        
        # Save stats
        self.save_stats()
        
        # Update AI model with this session's data
        self.update_ai_model(wpm, accuracy, np.mean(self.reaction_times) if self.reaction_times else 0)
        
        # Determine next difficulty level
        self.adjust_difficulty(wpm, accuracy, session_data['avg_reaction_time'])
        
        # Show completion message with stats
        messagebox.showinfo("Test Complete", 
                           f"Your results:\n"
                           f"Speed: {wpm:.1f} WPM\n"
                           f"Accuracy: {accuracy:.1f}%\n"
                           f"Difficulty: {self.current_difficulty}/5\n\n"
                           f"Next test will be at difficulty level {self.current_difficulty}")
    
    def update_ai_model(self, wpm, accuracy, reaction_time):
        """Update the AI model with new training data"""
        try:
            # Prepare data
            X = np.array([[wpm, accuracy, reaction_time]])
            y = np.array([[self.current_difficulty]])
            
            # Train the model with this single example
            self.model.fit(X, y, epochs=1, verbose=0)
            
            # Save the updated model in the recommended format
            self.model.save('typing_model.keras')  # Use .keras format
        except Exception as e:
            print(f"Error updating model: {e}")
    
    def adjust_difficulty(self, wpm, accuracy, reaction_time):
        """Adjust difficulty based on performance"""
        try:
            # Use the model to predict appropriate difficulty
            input_data = np.array([[wpm, accuracy, reaction_time]])
            predicted_diff = self.model.predict(input_data)[0][0]
            
            # Clamp between 1 and 5
            new_diff = min(5, max(1, int(round(predicted_diff))))
            
            # Apply some smoothing based on history
            if len(self.stats['sessions']) > 3:
                last_diff = self.stats['sessions'][-2]['difficulty']
                if abs(new_diff - last_diff) > 1:  # Don't change too drastically
                    new_diff = last_diff + (1 if new_diff > last_diff else -1)
            
            self.current_difficulty = new_diff
            self.difficulty_label.config(text=f"Difficulty Level: {self.current_difficulty}/5")
            
            # Provide feedback based on performance
            if wpm < 30 and accuracy < 90:
                self.show_ai_feedback("Try to focus on accuracy first. Speed will come with practice!")
            elif wpm > 60 and accuracy > 95:
                self.show_ai_feedback("Great job! You're ready for more challenging texts.")
            elif accuracy < 85:
                self.show_ai_feedback("Focus on typing accurately. Try to reduce errors.")
            elif reaction_time > 0.5:
                self.show_ai_feedback("Your reaction time is a bit slow. Try to maintain a steady rhythm.")
        except Exception as e:
            print(f"Error adjusting difficulty: {e}")
            # Fallback rules if model fails
            if accuracy > 95 and wpm > 50:
                self.current_difficulty = min(5, self.current_difficulty + 1)
            elif accuracy < 85 or wpm < 30:
                self.current_difficulty = max(1, self.current_difficulty - 1)
            self.difficulty_label.config(text=f"Difficulty Level: {self.current_difficulty}/5")
    
    def schedule_ai_feedback(self):
        """Schedule periodic AI feedback during the test"""
        if self.ai_feedback_timer is not None:
            self.after_cancel(self.ai_feedback_timer)
        
        # Give feedback every 15 seconds
        self.ai_feedback_timer = self.after(15000, self.provide_ai_feedback)
    
    def provide_ai_feedback(self):
        """Provide real-time feedback during the test"""
        if not self.running or self.completed:
            return
        
        current_time = time.time()
        if current_time - self.last_feedback_time < 10:  # Don't spam feedback
            self.schedule_ai_feedback()
            return
        
        elapsed = time.time() - self.start_time
        if elapsed < 5:  # Don't give feedback in first 5 seconds
            self.schedule_ai_feedback()
            return
        
        # Calculate current metrics
        input_text = self.input_entry.get()
        sample_text = self.sample_label.cget("text")
        accuracy = (self.correct_chars / len(input_text)) * 100 if input_text else 0
        wps = len(input_text.split()) / elapsed
        wpm = wps * 60
        avg_reaction = np.mean(self.reaction_times) if self.reaction_times else 0
        
        # Generate feedback
        feedback = ""
        if accuracy < 70:
            feedback = "You're making many errors. Slow down and focus on accuracy."
        elif accuracy < 85:
            feedback = "Good effort! Try to reduce errors by typing more carefully."
        elif wpm < 30:
            feedback = "Your speed is improving. Try to maintain a steady pace."
        elif avg_reaction > 0.5:
            feedback = "Your typing rhythm is irregular. Try to maintain consistent timing between keystrokes."
        else:
            feedback = "You're doing well! Keep up the good work."
        
        self.show_ai_feedback(feedback)
        self.last_feedback_time = current_time
        self.schedule_ai_feedback()
    
    def show_ai_feedback(self, message):
        """Display AI feedback with animation"""
        self.feedback_label.config(text=f"AI Feedback: {message}", fg="blue")
        self.feedback_label.after(100, lambda: self.feedback_label.config(fg="dark blue"))
    
    def time_thread(self):
        while self.running:
            time.sleep(0.1)
            if self.start_time is None:  # Ensure start_time is initialized
                continue
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 0:
                wps = len(self.input_entry.get().split()) / elapsed_time
                wpm = wps * 60
            else:
                wps = 0
                wpm = 0
            self.wpm_label.config(text=f"{wpm:.1f}")
            self.time_label.config(text=f"{elapsed_time:.1f}s")
    
    def reset(self):
        self.running = False
        self.completed = False
        self.start_time = None
        self.last_key_time = None
        self.input_entry.config(state="normal")
        self.input_entry.delete(0, tk.END)
        self.input_entry.config(fg="black")
        self.input_entry.focus_set()
        
        # Select a new sample text based on current difficulty
        self.sample_label.config(text=self.select_text_based_on_difficulty())
        
        # Reset stats displays
        self.wpm_label.config(text="0.00")
        self.accuracy_label.config(text="100%")
        self.time_label.config(text="0.00s")
        self.reaction_label.config(text="0.00s")
        self.progress["value"] = 0
        
        # Reset tracking variables
        self.correct_chars = 0
        self.total_chars = 0
        self.reaction_times.clear()
        self.accuracy_history.clear()
        
        # Cancel any pending feedback
        if self.ai_feedback_timer is not None:
            self.after_cancel(self.ai_feedback_timer)
            self.ai_feedback_timer = None

if __name__ == "__main__":
    app = MainPage()
    app.mainloop()