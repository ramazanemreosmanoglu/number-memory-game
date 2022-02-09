import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
import random
import threading
from time import sleep
from gi.repository import Gdk

UI_PATH = "window.ui"
STATUS_WAITING = "STATUS_WAITING"
STATUS_INGAME = "STATUS_INGAME"
STATUS_INPUT = "STATUS_INPUT"
STATUS_LOSE = "STATUS_LOSE"
STEP_DEFAULT = 4
DELAY = 1
NUMBERS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
KEYS = [Gdk.KEY_0, Gdk.KEY_1, Gdk.KEY_2, Gdk.KEY_3, Gdk.KEY_4, Gdk.KEY_5, Gdk.KEY_6, Gdk.KEY_7, Gdk.KEY_8, Gdk.KEY_9]


score = 0
step = STEP_DEFAULT
game_status = STATUS_WAITING
entered_numbers = None
final_number = None
enumerated_numbers = None

def show_numbers():	
	global entered_numbers
	global final_number, enumerated_numbers
	
	numbers = []
	while True:
		for _ in range(step):
			numbers.append(random.choice(NUMBERS))
		
		if len(numbers) == len(set(numbers)):
			break
		else:
			numbers = []
	
	print(numbers)
	
	label = get_obj("numberlabel")
	
	for number in numbers:
		label.set_text(str(number))
		sleep(DELAY)
	
	get_obj("main_stack_widget").set_visible_child(get_obj("input_box"))
	entered_numbers = iter(numbers)
	final_number = numbers[-1]
	enumerated_numbers = dict(enumerate(numbers))
	
	set_game_status(STATUS_INPUT)

def set_game_status(status):
	global game_status
	startbutton = get_obj("startbutton")
	stack = get_obj("main_stack_widget")
	
	if status == STATUS_INGAME:
		startbutton.set_sensitive(False)
		stack.set_visible_child(get_obj("showcase_box"))
	
	if status == STATUS_INPUT:
		startbutton.set_sensitive(False)
		stack.set_visible_child(get_obj("input_box"))

	if status == STATUS_LOSE:
		startbutton.set_sensitive(True)
		stack.set_visible_child(get_obj("lost_screen"))

	if status == STATUS_WAITING:
		startbutton.set_sensitive(True)
		get_obj("numberlabel").set_text("Click Start")
		stack.set_visible_child(get_obj("showcase_box"))
	
	game_status = status

def set_score(newscore):
	global score
	
	score = newscore
	label = get_obj("score_label")
	label.set_text(f"Score: {score}")

class Handler:
	def start_button_pressed(self, button):
		if button is not None: # Set the score zero if user is starting a new game.
			set_score(0)

		set_game_status(STATUS_INGAME)
		threading.Thread(target=show_numbers).start()
		
	
	def on_key_press(self, widget, event):
		global step
		if game_status != STATUS_INPUT:
			return
		
		keys_and_numbers = dict(zip(KEYS, NUMBERS))
		progressbar = get_obj("scoreprogress")
		
		if event.keyval in KEYS:
			num = keys_and_numbers[event.keyval]
			
			if num != next(entered_numbers):
				step = STEP_DEFAULT
				set_game_status(STATUS_LOSE)
			
			current_index = dict([(value, key) for key, value in enumerated_numbers.items()])[num]
			print(current_index/step)
			progressbar.set_fraction(progressbar.get_fraction() + current_index/step)
			progressbar.set_text(f"{current_index}/{step+1}")
			
			if num == final_number:
				set_score(score+step)
				step += 1
				self.start_button_pressed(None)
				progressbar.set_fraction(0)
				return
			

	def close_window(self, window):
		Gtk.main_quit()

builder = Gtk.Builder()
builder.add_from_file(UI_PATH)
builder.connect_signals(Handler())

get_obj = builder.get_object

window = get_obj("main_window")

window.show_all()
Gtk.main()
