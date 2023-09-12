from models import ExerciseType, Exercise, Category, Workout, Set
from db_utils import get_session
from models import ExerciseType, Exercise  # Import your model classes

class ExerciseTypeDAO:
    def __init__(self, session):
        self.session = session

    def create_exercise_type(self, metric_1, metric_2, metric_label_1, metric_label_2, exercise):
        exercise_type = ExerciseType(
            metric_1=metric_1,
            metric_2=metric_2,
            metric_label_1=metric_label_1,
            metric_label_2=metric_label_2,
            exercise = exercise
        )
        self.session.add(exercise_type)
        self.session.commit()
        return exercise_type

    def get_exercise_type_by_id(self, exercise_type_id):
        return self.session.query(ExerciseType).filter_by(id=exercise_type_id).first()

    def get_exercise_type_by_exercise_id(self, exercise_id):
        return self.session.query(ExerciseType).filter_by(exercise_id=exercise_id).first()
    
    def update_exercise_type_by_id(self, exercise_type_id, metric_1, metric_2, metric_label_1, metric_label_2):
        # Get the ExerciseType object by its ID
        exercise_type = self.get_exercise_type_by_id(exercise_type_id)
        
        # Update the attributes
        exercise_type.metric_1 = metric_1
        exercise_type.metric_2 = metric_2
        exercise_type.metric_label_1 = metric_label_1
        exercise_type.metric_label_2 = metric_label_2
        
        # Commit the changes to the session
        self.session.commit()
        
        return exercise_type

class ExerciseDAO:
    def __init__(self, session):
        self.session = session

    def create_exercise(self, name, category):
        exercise = Exercise(
            name=name,
            category = category
        )
        self.session.add(exercise)
        self.session.commit()
        return exercise

    def get_exercise_by_id(self, exercise_id):
        return self.session.query(Exercise).filter_by(id=exercise_id).one_or_none()

    def get_exercise_sets(self, exercise):
        return exercise.sets
    

    def get_sets_for_workout_and_exercise(self, workout_id, exercise_id):
        workout = self.session.query(Workout).get(workout_id)
        exercise = self.session.query(Exercise).get(exercise_id)
        if workout is None or exercise is None:
            return None

        sets = self.session.query(Set).filter(
            Set.workout == workout,
            Set.exercise == exercise
        ).all()

        return sets

    
    def get_exercise_by_category(self, category):
        return self.session.query(Exercise).filter_by(category_id=category.id).all()
    
    def get_exercise_type(self, exercise):
        return exercise.exercise_type
    
    def get_exercise_workouts(self, exercise):
        return exercise.workouts

    def update_exercise_name(self, exercise, new_name):        
        exercise.name = new_name
        self.session.commit()
        return exercise
    
    def delete_exercise(self, exercise):
        self.session.delete(exercise)
        self.session.commit()

    def delete_sets_in_workout(self, workout_id, exercise_id):
        workout = self.session.query(Workout).get(workout_id)
        exercise = self.session.query(Exercise).get(exercise_id)
        if workout is None or exercise is None:
            return None
        self.sets = self.session.query(Set).filter(
            Set.workout == workout,
            Set.exercise == exercise
        ).all()

        for set in self.sets:
            self.session.delete(set)
            self.session.commit()
    
class CategoryDAO:
    def __init__(self, session):
        self.session = session

    def create_category(self, name):
        new_category = Category(name=name)
        self.session.add(new_category)
        self.session.commit()
        return new_category
    
    def get_category_by_id(self, category_id):
        return self.session.query(Category).filter_by(id=category_id).one_or_none()
    
    def get_category_exercises(self, category):
        return category.exercises
    
    def get_all(self):
        return self.session.query(Category).all()
    
    def update_category_name(self, category, name):
        category.name = name
        self.session.commit()
        return category
    
    def delete_category(self, category):
        self.session.delete(category)
        self.session.commit()

class SetDAO:
    def __init__(self, session):
        self.session = session

    def create_set(self, metric_1, metric_2, timestamp, workout, exercise):
        new_set = Set(
            metric_1=metric_1,
            metric_2=metric_2,
            timestamp=timestamp,
            workout=workout,
            exercise=exercise
            )
        self.session.add(new_set)
        self.session.commit()
    
    def get_set_by_id(self, set_id):
        return self.session.query(Set).filter_by(id=set_id).one_or_none()

    def get_set_by_workout(self, workout):
        return self.session.query(Set).filter_by(workout_id=workout.id).all()
    
    def get_set_by_exercise(self, exercise):
        return self.session.query(Set).filter(exercise_id=exercise.id).all()
    
    def update_set(self, set, metric_1, metric_2):
        set.metric_1 = metric_1
        set.metric_2 = metric_2
        self.session.commit()
        return set

    def delete_set(self, set):
        self.session.delete(set)
        self.session.commit()

class WorkoutDAO:
    def __init__(self, session):
        self.session = session

    def create_workout(self, date):
        new_workout = Workout(date = date)
        self.session.add(new_workout)
        self.session.commit()
        return new_workout
    
    def get_workout_by_id(self, workout_id):
        return self.session.query(Workout).filter_by(id=workout_id).one_or_none()
    
    def get_workout_by_date(self, workout_date):
        return self.session.query(Workout).filter_by(date=workout_date).one_or_none()
   
    def get_workout_sets_dict(self, workout) ->dict:
        sets_dict = {}
        for set in workout.sets:
            if set.exercise not in sets_dict.keys():
                sets_dict[set.exercise] = [set]
            else:
                sets_dict[set.exercise].append(set)
        return sets_dict
    
    def get_workout_sets(self, workout):
        return self.session.query(Set).filter_by(workout_id = workout.id).all()
    
    def reset_workout(self, workout):
        date = workout.date
        self.delete_workout(workout)
        reset_workout = self.create_workout(date=date)
        return reset_workout

    def delete_workout(self, workout):
        self.session.delete(workout)
        self.session.commit()

