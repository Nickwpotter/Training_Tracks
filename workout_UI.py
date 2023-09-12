"""
Author: Nicholas Potter
Date: 8/11/23
Description: This app is built to track exercises, you can build new categories which are 
containers for exercises. The exercises each have sets that are linked to them. 
The Workout Page will load exercises and sets, it also has a selector which will load the date and search the database.
The database will return a workout object with sets and exercises linked to it. On the Exercise Page and Workout Page
we can delete or add (categories, exercises, sets).

To run my program enter the following in the command line:
python "main.py"
"""

from DAO import ExerciseDAO, ExerciseTypeDAO, WorkoutDAO, SetDAO, CategoryDAO
import tkinter as tk
from tkinter import ttk
from models import Category, ExerciseType, Exercise
from datetime import date, datetime, timedelta  
from db_utils import get_session


LARGE_FONT= ("Helvetica", 12)
LARGE_FONT_BOLD= ("Helvetica", 12, 'bold')

class DAOManager:
    _instances = {}
    session = get_session()
    def __init__(self, session) -> None:
        self.session = session

    def get_instance(self, dao_class):
        if dao_class not in self._instances:
            self._instances[dao_class] = dao_class(self.session)
        return self._instances[dao_class]
    
#Create main window MyApp
class MyApp(tk.Tk):
    def __init__(self, daoManager, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Muscle Maps")
        self.geometry('400x680')
        self.resizable(False,False)

        #Main Container Frame
        frame_container = tk.Frame(self)
        frame_container.pack(side="top", fill="both", expand=True)
        frame_container.grid_rowconfigure(0, weight=1)
        frame_container.grid_columnconfigure(0, weight=1)

        #DAO Manager
        self.dao_manager = daoManager

        #Build Frames
        self.frames = {}

        for F in (AddExercisePage, WorkoutPage, CategoryPage, ExercisePage,):
            frame = F(frame_container, self, self.dao_manager)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        #run is_first_run() on the workout page
        self.frames[WorkoutPage].is_new_workout()

        # Show the initial frame
        self.show_frame(WorkoutPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()# Bring the desired frame to the front
    
    def get_frame_object(self, class_frame):
        return self.frames[class_frame]

class WorkoutPage(tk.Frame):
    def __init__(self, parent, controller, dao_manager):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.dao_manager = dao_manager
        self.selected_checkbuttons = []

        self.label = tk.Label(self, text="Workout Page", font=LARGE_FONT_BOLD)
        self.label.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

        self.date_label = tk.Label(self, text="Date:", font=LARGE_FONT_BOLD)
        self.date_label.grid(row=1, column=0, padx=10, sticky="e")
        
        self.date_spinbox = tk.Spinbox(self, font=LARGE_FONT, command=self.is_new_workout)
        self.date_spinbox.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Set the range of dates for the Spinbox
        today = date.today()
        start_date = today - timedelta(days=365)  # Display dates from the last year
        end_date = today + timedelta(days=365)
        self.date_spinbox.config(values=[(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)])

        # Set the initial value of the Spinbox to the current date
        initial_date = today.strftime('%Y-%m-%d')
        self.date_spinbox.delete(0, "end")
        self.date_spinbox.insert(0, initial_date)

        # Create frame for exercises
        self.info_frame = tk.LabelFrame(self, text='Workout Stats', font=LARGE_FONT_BOLD)
        self.info_frame.grid(row=2, column=0, rowspan=9, columnspan=2, padx=55, pady=10, sticky="nesw")

        self.new_workout_label = tk.Label(self.info_frame, text='No Exercises in this workout', font=LARGE_FONT)
        self.new_workout_label.grid(row=0, column=0, padx=10, pady=50, sticky='ew')

        self.button = tk.Button(self, text="Add Exercise", font=LARGE_FONT_BOLD, width=20, height=3,
                                command=lambda: self.controller.show_frame(CategoryPage))
        self.button.grid(row=11, column=0, columnspan=2, pady=10, padx=10, sticky="s")

        self.delete_select_btn = tk.Button(self, text="Delete/Select", font=LARGE_FONT_BOLD,
                                command=self.create_selection)
        self.delete_select_btn.grid(row=12, column= 0, columnspan=2, pady=10, padx=10, sticky="s" )
        
        # Configure the bottom row to expand with weight
        self.grid_rowconfigure(11, weight=1)  # Expand the bottom row
        self.grid_columnconfigure(0, weight=1)  
        self.grid_columnconfigure(1, weight=1)
        
        self.is_new_workout()

    def is_new_workout(self) ->bool:
        self.spinbox_value = self.date_spinbox.get()
        self.workout_doa: WorkoutDAO = self.dao_manager.get_instance(WorkoutDAO)
        self.workout_obj = self.workout_doa.get_workout_by_date(self.spinbox_value)
        self.add_exercise_page:AddExercisePage= self.controller.get_frame_object(AddExercisePage)
        if self.workout_obj is None:
            self.delete_select_btn.config(state='disabled')
            self.current_workout = self.workout_doa.create_workout(date=self.spinbox_value)
            self.add_exercise_page.selected_workout = self.current_workout
            # self.new_workout_label = tk.Label(self.info_frame, text='No Exercises in this workout', font=LARGE_FONT)
            # self.new_workout_label.grid(row=0, column=0, padx=10, pady=50, sticky='ew' )
            self.populate_exercises_sets(self.current_workout)
            print("\n\n\nis_new_workout\n\n\n")
        else:
            self.add_exercise_page.selected_workout = self.workout_obj
            self.populate_exercises_sets(self.workout_obj)
            print("\n\n\nnot_new_workout\n\n\n")
    
    def populate_exercises_sets(self, workout_obj):
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        workout_dao: WorkoutDAO = self.dao_manager.get_instance(WorkoutDAO)
        workout_sets = workout_dao.get_workout_sets(workout_obj)
        print(workout_sets)
        if workout_sets == []:
            self.delete_select_btn.config(state='disabled')
            self.new_workout_label = tk.Label(self.info_frame, text='No Exercises in this workout', font=LARGE_FONT)
            self.new_workout_label.grid(row=0, column=0, padx=10, pady=50, sticky='ew')
            pass
        else:
            self.delete_select_btn.config(state='active', command=self.create_selection)
            self.exercise_dict = self.sets_and_exercises(workout_dao, workout_obj)
            self.row = 0
            for key, value in self.exercise_dict.items():
                self.exercise_frame = tk.LabelFrame(self.info_frame, text=f'{key.name}',font=LARGE_FONT_BOLD)
                self.exercise_frame.grid(row = self.row, column=0, padx=5, pady=5, sticky='ew')
                self.exercise_button = tk.Button(self.exercise_frame, text=value, font=LARGE_FONT, command = lambda exercise = key, workout = workout_obj: self.go_to_AddExercisePage(exercise, workout))
                self.exercise_button.grid(row= self.row, column=0, padx=10, pady=5, sticky='ew')
                self.row += 1

    def sets_and_exercises(self, workout_dao: WorkoutDAO, workout_obj):
        self.string_dict = {}
        self.workout_sets = workout_dao.get_workout_sets_dict(workout_obj)
        for key, value in self.workout_sets.items():
            self.set_lyst = []
            for set in value:
                exercise_type_dao : ExerciseTypeDAO = self.dao_manager.get_instance(ExerciseTypeDAO)
                exercise_type_obj = exercise_type_dao.get_exercise_type_by_exercise_id(key.id)
                self.set_lyst.append(f'\t{set.metric_1} {exercise_type_obj.metric_label_1}\t{set.metric_2} {exercise_type_obj.metric_label_2}')
            set_string = '\n'.join(self.set_lyst)
            self.string_dict[key] = set_string
        return self.string_dict
     
    def go_to_AddExercisePage(self, exercise, workout):
        add_exercise_page: AddExercisePage= self.controller.get_frame_object(AddExercisePage)
        add_exercise_page.selected_exercise = exercise
        add_exercise_page.selected_workout = workout
        add_exercise_page.update_page()
        self.controller.show_frame(AddExercisePage)
    
    def create_selection(self):
        self.delete_select_btn.config(state='active', command=lambda: self.delete_selected_exercises())
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        self.delete_label = tk.Label(
            self.info_frame, 
            text='select the exercises you would like to delete\nthen click delete again')
        self.delete_label.pack(padx=5, pady=5)
        spinbox_value = self.date_spinbox.get()
        workout_dao: WorkoutDAO = self.dao_manager.get_instance(WorkoutDAO)
        workout_obj = workout_dao.get_workout_by_date(spinbox_value)
        workout_sets = workout_dao.get_workout_sets(workout_obj)
        if workout_sets == []:
            self.is_new_workout()
        else:
            self.sets_and_exercises_dict = self.sets_and_exercises(workout_dao, workout_obj)
            self.row=0
            for key, value in self.sets_and_exercises_dict.items():
                self.check_var = tk.BooleanVar(value=False)  # Create a BooleanVar for each checkbutton
                self.checkbutton = tk.Checkbutton(self.info_frame, text=value, variable=self.check_var)
                self.checkbutton.pack(padx=5, pady=5)

                # Create a lambda function to capture the current key and check_var value
                self.checkbutton.config(command=lambda exercise=key, check_var=self.check_var: self.checkbutton_clicked(exercise, check_var))

                self.row += 1

    def checkbutton_clicked(self, exercise: Exercise, check_var):
        if check_var.get():
            self.selected_checkbuttons.append(exercise)
        elif exercise in self.selected_checkbuttons:
            self.selected_checkbuttons.remove(exercise)


    def delete_selected_exercises(self):
        exercise_dao : ExerciseDAO = self.dao_manager.get_instance(ExerciseDAO)
        spinbox_value = self.date_spinbox.get()
        workout_dao: WorkoutDAO = self.dao_manager.get_instance(WorkoutDAO)
        workout_obj = workout_dao.get_workout_by_date(spinbox_value)
        for exercise in self.selected_checkbuttons:
            exercise_dao.delete_sets_in_workout(workout_obj.id, exercise.id)
        
        self.populate_exercises_sets(workout_obj)
            

class CategoryPage(tk.Frame):
    def __init__(self, parent, controller: MyApp, dao_manager):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.dao_manager = dao_manager

        self.current_categories = None
        self.selected_checkbuttons = []


        self.page_label = tk.Label(self, text='Category Page', font=LARGE_FONT_BOLD)
        self.page_label.pack(padx=10, pady=10, side="top")

        self.category_btn_frame = tk.Frame(self)
        self.category_btn_frame.pack(padx=10, pady=10, side="top")

        self.add_btn = tk.Button(self.category_btn_frame, text="Add Category", font=LARGE_FONT,
                           command=lambda: self.add_category())
        self.add_btn.grid(row=0, column= 1, pady=15, padx=10, )

        self.delete_btn = tk.Button(self.category_btn_frame, text="Delete/Select", font=LARGE_FONT,
                           command=self.delete_select)
        self.delete_btn.grid(row=0, column= 2, pady=15, padx=10, )

        self.categories_frame = tk.LabelFrame(self, text="Categories", width=200 ,font=LARGE_FONT_BOLD)
        self.categories_frame.pack(pady=10, padx=15)

        self.home_btn = tk.Button(self, text="Home", font=LARGE_FONT_BOLD, width= 25, height=3,
                           command=self.go_home)
        self.home_btn.pack(pady=20, padx=10, side="bottom")
 
        self.load_categories()

    def load_categories(self):
        self.category_dao = self.dao_manager.get_instance(CategoryDAO)
        self.categories = self.category_dao.get_all()
        self.current_categories = self.categories
        self.delete_btn.config(command=self.delete_select)
        # Clear the existing category buttons
        for widget in self.categories_frame.winfo_children():
            widget.destroy()

        # Set a fixed width and height for category buttons
        button_width = 20
        button_height = 1
        
        # Create category buttons dynamically
        self.describe_action_lbl = tk.Label(self.categories_frame, text='Click on a category to see exercises', font=LARGE_FONT)
        self.describe_action_lbl.pack(padx=10, pady=10, side="top")
        for category in self.categories:
            category_button = tk.Button(self.categories_frame, text=category.name,
                                        width=button_width, height=button_height,
                                         command=lambda c=category: self.category_button_clicked(c))
            category_button.pack(padx=5, pady=5)
    
    def go_home(self):
        self.controller.show_frame(WorkoutPage)

    def category_button_clicked(self, category):
        # Show the ExercisePage
        exercise_frame = self.controller.get_frame_object(ExercisePage)

        exercise_frame.selected_category = category
        exercise_frame.load_exercises()
        self.controller.show_frame(ExercisePage)

    def add_category(self):
        def save_category():
            new_category_name = new_category_entry.get()
            if new_category_name:
                category_dao = self.dao_manager.get_instance(CategoryDAO)
                category_dao.create_category(name = new_category_name)

                # Update the category list and refresh the view
                self.load_categories()

                new_window.destroy()

        new_window = tk.Toplevel(self.parent)
        new_window.geometry('200x150')
        new_window.title("Add New Category")

        new_category_label = tk.Label(new_window, text="Category Name:")
        new_category_label.pack(padx= 10, pady= 5, expand=True)

        new_category_entry = tk.Entry(new_window)
        new_category_entry.pack(side='top', padx= 10, pady= 5, expand=True)
        new_category_entry.focus_set()

        save_button = tk.Button(new_window, text="Save", width= 10, height= 2, command=save_category)
        save_button.pack(side='top', padx= 10, pady= 5, expand=True)

    def delete_select(self):
        self.delete_btn.config(text='Delete', command=self.delete_selected_categories)
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        self.delete_label = tk.Label(self.categories_frame, 
                                     text='select the sets you would like to delete\nthen click delete again')
        self.delete_label.pack(padx=20, pady=10)
        if self.current_categories is not None:
            for category in self.current_categories:
                
                self.check_var = tk.BooleanVar(value=False)                

                self.check_button = tk.Checkbutton(self.categories_frame, text= category.name, variable= self.check_var)
                self.check_button.pack(padx=35, pady=5, anchor='w')
                self.check_button.config(command=lambda c=category, v=self.check_var: self.checkbutton_clicked(c, v))
    
    def checkbutton_clicked(self, category_obj, check_var):
        if check_var.get():
            self.selected_checkbuttons.append(category_obj)
        elif category_obj in self.selected_checkbuttons:
            self.selected_checkbuttons.remove(category_obj)

    def delete_selected_categories(self):
        category_dao : CategoryDAO = self.dao_manager.get_instance(CategoryDAO)
        for category in self.selected_checkbuttons:
            category_dao.delete_category(category)
        self.selected_checkbuttons.clear()
        self.load_categories()

class ExercisePage(tk.Frame):
    def __init__(self, parent, controller: MyApp, dao_manager: DAOManager):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.dao_manager = dao_manager
        self.selected_category = None

        self.current_exercises = None
        self.selected_exercises = []

        self.page_label = tk.Label(self, text='Exercise Page', font=LARGE_FONT_BOLD)
        self.page_label.pack(padx=10, pady=10, side="top")

        self.exercise_options_frame = tk.Frame(self)
        self.exercise_options_frame.pack(padx=10, pady=10)

        self.new_exercise_btn = tk.Button(self.exercise_options_frame, text="Add Exercise",font=LARGE_FONT, command=self.add_exercise)
        self.new_exercise_btn.grid(row=0, column=0, padx=10 , pady=10)

        self.delete_exercise_btn = tk.Button(self.exercise_options_frame, text="Delete", font=LARGE_FONT, command=self.delete_select)
        self.delete_exercise_btn.grid(row=0, column=1, padx=10 , pady=10)

        self.exercises_frame = tk.LabelFrame(self, text= f'Exercises', width= 200, font=LARGE_FONT)
        self.exercises_frame.pack( pady=10, padx=15)

        self.load_exercises()

        self.home_btn = tk.Button(self, text="Home",  width= 25, height=3, font=LARGE_FONT_BOLD, command=self.home)
        self.home_btn.pack(padx=10 , pady=10, side="bottom")

    def load_exercises(self):
        if self.selected_category != None:
            # Clear the existing exercise buttons
            for widget in self.exercises_frame.winfo_children():
                widget.destroy()
            self.exercises_frame.destroy()
            self.home_btn.destroy()
            self.delete_exercise_btn.config(command=self.delete_select)
            self.exercises_frame = tk.LabelFrame(self, text= f'{self.selected_category.name} Exercises', font=LARGE_FONT)
            self.exercises_frame.pack( pady=10, padx=15)            
            exercise_dao : ExerciseDAO = self.dao_manager.get_instance(ExerciseDAO)
            exercises = exercise_dao.get_exercise_by_category(self.selected_category)
            self.current_exercises = exercises
            # Set a fixed width and height for category buttons
            button_width = 20
            button_height = 1

            # Create exercise buttons dynamically
            for exercise in exercises:
                exercise_button = tk.Button(self.exercises_frame, text=exercise.name, 
                                            width=button_width, height=button_height,
                                            command=lambda e=exercise: self.exercise_button_clicked(e))
                exercise_button.pack(padx=5, pady= 5)
            
            self.home_btn = tk.Button(self, text="Home",  width= 25, height=3, font=LARGE_FONT_BOLD, command=self.home)
            self.home_btn.pack(padx=10 , pady=10, side="bottom")


    def exercise_button_clicked(self, exercise):
        # Create an instance of ExercisePage with the selected category
        self.add_sets_to_workout: AddExercisePage = self.controller.get_frame_object(AddExercisePage)

        # Show the ExercisePage
        self.add_sets_to_workout.selected_exercise = exercise
        self.add_sets_to_workout.update_page()
        self.controller.show_frame(AddExercisePage)
    
    def add_exercise(self):
        def save_exercise():
            new_exercise_name = new_exercise_entry.get()
            measurement_type = measurement_combobox.get()  # Get the selected measurement type

            exercise_type_dao : ExerciseTypeDAO = self.dao_manager.get_instance(ExerciseTypeDAO)
            if new_exercise_name and measurement_type:
                exercise_dao: ExerciseDAO = self.dao_manager.get_instance(ExerciseDAO)
                new_exercise = exercise_dao.create_exercise(name=new_exercise_name, category=self.selected_category)
            if measurement_type == "Distance and Time":
                exercise_type = exercise_type_dao.create_exercise_type(metric_1=0, metric_2=0, metric_label_1='mi', metric_label_2='mins', exercise=new_exercise)
            else:
                exercise_type = exercise_type_dao.create_exercise_type(metric_1=0, metric_2=0, metric_label_1='lbs', metric_label_2='reps', exercise=new_exercise)


                # Update the exercise list and refresh the view
            self.load_exercises()

            new_window.destroy()

        new_window = tk.Toplevel(self.parent)
        new_window.title("Add New Exercise")
        
        # Create a frame to center widgets
        center_frame = tk.Frame(new_window)
        center_frame.pack(expand=True)

        new_exercise_label = tk.Label(center_frame, text="Exercise Name:")
        new_exercise_label.pack()

        new_exercise_entry = tk.Entry(center_frame)
        new_exercise_entry.pack()

        measurement_label = tk.Label(center_frame, text="Measurement Type:")
        measurement_label.pack()

        # Create a Combobox for measurement type selection
        measurement_combobox = ttk.Combobox(center_frame, values=["Distance and Time", "Weight and Reps"])
        measurement_combobox.pack()

        save_button = tk.Button(center_frame, text="Save", command=save_exercise)
        save_button.pack()

        # Center the center_frame using expand and anchor options
        center_frame.pack(expand=True, anchor=tk.CENTER)
    
    def home(self):
        self.controller.show_frame(WorkoutPage)
    
    def delete_select(self):
        self.delete_exercise_btn.config(text='Delete', command=self.delete_selected_exercises)
        for widget in self.exercises_frame.winfo_children():
            widget.destroy()
        self.delete_label = tk.Label(self.exercises_frame, 
                                     text='select the exercises you would like to delete\nthen click delete again')
        self.delete_label.pack(padx=20, pady=10)
        if self.current_exercises is not None:
            for exercise in self.current_exercises:
                
                self.check_var = tk.BooleanVar(value=False)                

                self.check_button = tk.Checkbutton(self.exercises_frame, text= exercise.name, variable= self.check_var)
                self.check_button.pack(padx=35, pady=5, anchor='w')
                self.check_button.config(command=lambda e=exercise, v=self.check_var: self.checkbutton_clicked(e, v))
    
    def checkbutton_clicked(self, exercise_obj, check_var):
        if check_var.get():
            self.selected_exercises.append(exercise_obj)
        elif exercise_obj in self.selected_exercises:
            self.selected_exercises.remove(exercise_obj)

    def delete_selected_exercises(self):
        exercise_dao : ExerciseDAO = self.dao_manager.get_instance(ExerciseDAO)
        for exercise in self.selected_exercises:
            exercise_dao.delete_exercise(exercise)
        self.selected_exercises.clear()
        self.load_exercises()

class AddExercisePage(tk.Frame):
    def __init__(self, parent, controller, dao_manager):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.dao_manager = dao_manager
        self.selected_exercise = None
        self.selected_workout = None

        self.selected_checkbuttons = []

        self.metrics_label_frame = tk.LabelFrame(self, text='Metrics', font=LARGE_FONT_BOLD)
        self.metrics_label_frame.pack(padx=10, pady=10)

        self.numeric_validator = self.metrics_label_frame.register(self.validate_numeric_input)

        self.metric_1_entry = tk.Entry(self.metrics_label_frame,justify='center', validatecommand=(self.numeric_validator, '%d', '%P'), font=LARGE_FONT)
        self.metric_1_entry.grid(row=0, column=0, padx=10, pady=10)

        self.metric_label_1 = tk.Label(self.metrics_label_frame, text='Metric 1', font=LARGE_FONT)
        self.metric_label_1.grid(row=0, column=1, padx=10, pady=10)

        self.metric_2_entry = tk.Entry(self.metrics_label_frame , justify='center',validatecommand=(self.numeric_validator, '%d', '%P'), font=LARGE_FONT)
        self.metric_2_entry.grid(row=1, column=0, padx=10, pady=10)

        self.metric_label_2 = tk.Label(self.metrics_label_frame, text='Metric 2',font=LARGE_FONT)
        self.metric_label_2.grid(row=1, column=1, padx=10, pady=10)

        self.save_button = tk.Button(self.metrics_label_frame, text="Save Set", font=LARGE_FONT,
                            command=lambda: self.save_new_set())
        self.save_button.grid(row=2, column=0, padx=10, pady=10)

        self.delete_set_button = tk.Button(self.metrics_label_frame, text='Delete/Select', font=LARGE_FONT, command=self.delete_select)
        self.delete_set_button.grid(row = 2, column=1, columnspan=2, padx=10, pady=5)

        self.exercise_sets_frame = tk.LabelFrame(self, text=f'Sets', font=LARGE_FONT_BOLD)
        self.exercise_sets_frame.pack(padx=5, pady=10)

        self.home_button = tk.Button(self, text="Home", font=LARGE_FONT_BOLD, width=20, height=3,
                            command=lambda: self.home_screen())
        self.home_button.pack(padx=10, pady=30, side='bottom')

    def update_page(self):
        self.delete_set_button.config(text='Delete/Select', command=self.delete_select)
        if self.selected_exercise is None or self.selected_workout is None:
            if self.selected_exercise is None:
                print("\n\n\n\n\n\nexercise\n\n\n\n\n\n")
            if self.selected_workout is None:
                print("\n\n\n\n\n\nworkout\n\n\n\n\n\n")
                
        else:
            self.metrics_label_frame.config(text=f'{self.selected_exercise.name} Metrics')
            exercise_type_dao : ExerciseTypeDAO = self.dao_manager.get_instance(ExerciseTypeDAO)
            exercise_type_obj:ExerciseType = exercise_type_dao.get_exercise_type_by_exercise_id(self.selected_exercise.id)
            self.metric_label_1.config(text=f'{exercise_type_obj.metric_label_1}')
            self.metric_label_2.config(text=f'{exercise_type_obj.metric_label_2}')

            self.show_sets()
            print("\n\n\nupdated\n\n\n")

    def show_sets(self):
        exercise_dao: ExerciseDAO = self.dao_manager.get_instance(ExerciseDAO)
        sets = exercise_dao.get_sets_for_workout_and_exercise(self.selected_workout.id, self.selected_exercise.id)
        for widget in self.exercise_sets_frame.winfo_children():
            widget.destroy()
        if sets == [] or sets == None:
            self.no_sets_label = tk.Label(self.exercise_sets_frame, text='Add a set to your workout', font= LARGE_FONT)
            self.no_sets_label.pack(padx=5, pady=5)
        else:
            for set in sets:
                exercise_type_dao : ExerciseTypeDAO = self.dao_manager.get_instance(ExerciseTypeDAO)
                exercise_type_obj:ExerciseType = exercise_type_dao.get_exercise_type_by_exercise_id(self.selected_exercise.id)
                self.set_button = tk.Button(self.exercise_sets_frame, text=f'\t{set.metric_1} {exercise_type_obj.metric_label_1}\t{set.metric_2} {exercise_type_obj.metric_label_2}')
                self.set_button.pack(padx=50, pady=5)

    def save_new_set(self):
        metric_1_value = self.metric_1_entry.get()
        metric_2_value = self.metric_2_entry.get()

        # Validate that the values can be converted to floats
        try:
            metric_1_value = float(metric_1_value)
            metric_2_value = float(metric_2_value)
        except ValueError:
            error_message = "Invalid input. Please enter valid numeric values."
            tk.messagebox.showerror("Input Error", error_message)
            return
        set_dao: SetDAO = self.dao_manager.get_instance(SetDAO)
        new_set = set_dao.create_set(
            metric_1=self.metric_1_entry.get(), 
            metric_2=self.metric_2_entry.get(), 
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
            workout=self.selected_workout,
            exercise=self.selected_exercise
                                    )
        self.show_sets()
        return new_set
    
    def home_screen(self):
        workout_page_obj = self.controller.get_frame_object(WorkoutPage)
        workout_page_obj.is_new_workout()
        self.controller.show_frame(WorkoutPage)
    
    def validate_numeric_input(action, value_if_allowed):
        if action == '1':  # '1' means a key press
            if value_if_allowed.isdigit() or value_if_allowed == "":
                return True
            else:
                return False
        return True

    def delete_select(self):
        self.delete_set_button.config(text='Delete', command=lambda :self.delete_selected_sets())
        for widget in self.exercise_sets_frame.winfo_children():
            widget.destroy()
        self.delete_label = tk.Label(self.exercise_sets_frame, 
                                     text='select the sets you would like to delete\nthen click delete again'
                                     )
        self.delete_label.pack(padx=20, pady=10)
        exercise_dao: ExerciseDAO = self.dao_manager.get_instance(ExerciseDAO)
        sets = exercise_dao.get_sets_for_workout_and_exercise(self.selected_workout.id, self.selected_exercise.id)
        if sets == [] or sets == None:
            self.no_sets_label = tk.Label(self.exercise_sets_frame, text='Add a set to your workout', font= LARGE_FONT)
            self.no_sets_label.pack(padx=5, pady=5)
        else:

            for set in sets:
                exercise_type_dao : ExerciseTypeDAO = self.dao_manager.get_instance(ExerciseTypeDAO)
                exercise_type_obj:ExerciseType = exercise_type_dao.get_exercise_type_by_exercise_id(self.selected_exercise.id)
                self.check_var = tk.BooleanVar(value=False)
                self.checkbutton_text = f'\t{set.metric_1} {exercise_type_obj.metric_label_1}\t{set.metric_2} {exercise_type_obj.metric_label_2}'
                

                self.check_button = tk.Checkbutton(self.exercise_sets_frame, text= self.checkbutton_text, variable= self.check_var)
                self.check_button.pack(padx=35, pady=5)
                self.check_button.config(command=lambda set=set, check_var= self.check_var: self.checkbutton_clicked(set, check_var))
    
    def checkbutton_clicked(self, set_obj, check_var):
        if check_var.get():
            self.selected_checkbuttons.append(set_obj)
        elif set_obj in self.selected_checkbuttons:
            self.selected_checkbuttons.remove(set_obj)

    def delete_selected_sets(self):
        set_dao : SetDAO = self.dao_manager.get_instance(SetDAO)
        for set in self.selected_checkbuttons:
            set_dao.delete_set(set)
        self.update_page()
