from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class CargoForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    length = FloatField('Длина (м)', validators=[DataRequired(), NumberRange(min=0.01)])
    width = FloatField('Ширина (м)', validators=[DataRequired(), NumberRange(min=0.01)])
    height = FloatField('Высота (м)', validators=[DataRequired(), NumberRange(min=0.01)])
    weight = FloatField('Вес (кг)', validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField('Количество', validators=[DataRequired(), NumberRange(min=1)])
    is_stackable = BooleanField('Можно ставить сверху')
    fragile = BooleanField('Хрупкий')
    submit = SubmitField('Сохранить')

class TransportForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    max_length = FloatField('Длина кузова (м)', validators=[DataRequired(), NumberRange(min=0.01)])
    max_width = FloatField('Ширина кузова (м)', validators=[DataRequired(), NumberRange(min=0.01)])
    max_height = FloatField('Высота кузова (м)', validators=[DataRequired(), NumberRange(min=0.01)])
    max_weight = FloatField('Грузоподъёмность (кг)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Сохранить')

class TaskForm(FlaskForm):
    transport = SelectField('Транспорт', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Создать задачу')