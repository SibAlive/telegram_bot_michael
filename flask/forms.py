"""Формы для редактирования"""
from flask_wtf import FlaskForm
from wtforms import (StringField, DecimalField, BooleanField, SelectField, SubmitField)
from wtforms.validators import DataRequired, NumberRange


class CategoryForm(FlaskForm):
    name = StringField('Название категории', validators=[DataRequired()])
    slug = StringField('Slug (URL-имя)', validators=[DataRequired()])
    is_active = BooleanField('Активна', default=True)
    submit = SubmitField('Сохранить')


class ProductForm(FlaskForm):
    name = StringField('Название товара', validators=[DataRequired()])
    price = DecimalField('Цена', validators=[DataRequired(), NumberRange(min=0)], places=2)
    photo_url = StringField('File_id фото (для получения File_id - необходимо отправить фото боту)')
    category_id = SelectField('Категория', coerce=int, validators=[DataRequired()])
    is_available = BooleanField('Доступен для покупки', default=True)
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        from models import Category
        from .extensions import db
        # Заполняем SelectField категориями из БД
        self.category_id.choices = [(0, 'Без категории')] + [
            (c.id, c.name) for c in db.session.query(Category).filter_by(is_active=True).all()
        ]