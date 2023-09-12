from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Date, Table
from sqlalchemy.orm import relationship
from db_utils import Base


# Define the association table for workout_exercise
workout_exercise = Table(
    'workout_exercise',
    Base.metadata,
    Column('workout_id', Integer, ForeignKey('workout.id')),
    Column('exercise_id', Integer, ForeignKey('exercise.id'))
)

#Define the ExerciseType class
class ExerciseType(Base):
    __tablename__ = 'type'
    id = Column(Integer, primary_key=True)
    metric_1 = Column(Integer)
    metric_2 = Column(Integer)
    metric_label_1 = Column(String)
    metric_label_2 = Column(String)

    #Define Foreign key for exercise id
    exercise_id = Column(Integer, ForeignKey('exercise.id'))  

    #Define relationship with Exercise
    exercise = relationship('Exercise', back_populates='exercise_type')

    def __repr__(self):
        return f'ExerciseType({self.id}, {self.metric_1} {self.metric_label_1}, {self.metric_2} {self.metric_label_2}, Exercise_id: {self.exercise_id})'

#Define the Exercise class
class Exercise(Base):
    __tablename__ = 'exercise'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    #Define foreign key for Category
    category_id = Column(Integer, ForeignKey('category.id'))


    #Define relationships with Category and sets
    exercise_type = relationship('ExerciseType', back_populates='exercise')
    category = relationship('Category', back_populates='exercises')
    sets = relationship('Set', back_populates= 'exercise')
    workouts = relationship('Workout', secondary= 'workout_exercise', back_populates= 'exercises')

    def __repr__(self):
        exercise_type_id = ', '.join([et.metric_label_1 and et.metric_label_2 for et in self.exercise_type])
        return f'Exercise(ID: {self.id}, Name: {self.name}, Category: {self.category.name}, ExerciseTypes: {exercise_type_id})'

# Define the Category class
class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    #Define relationship with exercise
    exercises = relationship('Exercise', cascade='all', back_populates='category')

    def __repr__(self):
        return f'Category(ID: {self.id}, Name: {self.name}, Exercise List: {[exercise.name for exercise in self.exercises]})'

#Define the Set Class
class Set(Base):
    __tablename__ = 'set'
    id = Column(Integer, primary_key=True)
    metric_1 = Column(Float)
    metric_2 = Column(Integer)
    timestamp = Column(String)

    #Define Foreign Key for Exercise and Workout
    exercise_id = Column(Integer, ForeignKey('exercise.id'))
    workout_id = Column(Integer, ForeignKey('workout.id'))

    #Define relationship with workout and exercise
    workout = relationship('Workout', back_populates= 'sets')
    exercise = relationship('Exercise',  back_populates='sets')

    def __repr__(self):
        return f'Set(ID: {self.id}, timestamp: {self.timestamp}, metric_1: {self.metric_1}, metric_2: {self.metric_2}, exercise_name: {self.exercise.name})'

#Define the Workout Class
class Workout(Base):
    __tablename__ = 'workout'
    id = Column(Integer, primary_key=True)
    date = Column(String)

    #Define relationship with sets
    sets = relationship('Set', cascade= 'delete', back_populates= 'workout')
    exercises = relationship('Exercise', secondary= 'workout_exercise', back_populates= 'workouts')

    def __repr__(self):
        return f'Workout(ID: {self.id}, date: {self.date}, exercises: {[exercise.name for exercise in self.exercises]})'