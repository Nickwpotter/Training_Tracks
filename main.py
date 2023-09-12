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

this will not run from the codio terminal.
"""

from db_utils import initialize_database, get_session, engine
from sqlalchemy import inspect
from models import ExerciseType, Exercise, Category, Workout, Set, workout_exercise
from workout_UI import MyApp, DAOManager
from DAO import CategoryDAO, ExerciseDAO, ExerciseTypeDAO

#check if it is the first run and print table names in database
def is_first_run(session):
    inspector = inspect(engine)
    is_database_created = inspector.has_table('exercise') and inspector.has_table('category')
    if not is_database_created:
        initialize_database()
        APP_DEFAULT_VALUES = {'Chest':['Barbell Bench Press', 'Incline Barbell Bench Press', 'Machine fly', 'Cable_fly', 'Push ups'],
                              'Back':['Barbell Row', 'Lat Pulldown', 'pull ups', 'Seated Cable Row', 'Back Extension Machine'],
                              'Legs':['Barbell Squat', 'Barbell Deadlift', "Bulgarian Split Squat", 'Kettelbell lunges', 'Hamstring curls', 'Leg Extensions', 'Box Jumps'],
                              'Biceps':['Dumbell Curl', 'Dumbell Hammer Curl', 'EZ bar Curl', 'EZ bar Preacher Curl', 'Cable Curls']}
        for category_name, exercises in APP_DEFAULT_VALUES.items():
            category_dao = CategoryDAO(session)
            category = category_dao.create_category(name=category_name)
            for exercise_name in exercises:
                exercise_dao = ExerciseDAO(session)
                exercise_obj = exercise_dao.create_exercise(name=exercise_name, category=category)
                exercise_type_dao = ExerciseTypeDAO(session)
                exercise_type_dao.create_exercise_type(metric_1= 0, metric_2= 0,metric_label_1='lbs', metric_label_2='reps', exercise=exercise_obj)


    
def main():

    session = get_session()
    is_first_run(session)
    app = MyApp(daoManager=DAOManager(session))
    app.mainloop()


    session.close()

if __name__ == '__main__':
    main()