from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional

class SearchForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()])
    search_by = SelectField('Search by', choices=[('r', 'Radius'), ('d', 'Drive Time'), ('b', 'Both')], validators=[DataRequired()])
    radius = IntegerField('Radius (in miles)', validators=[Optional()])
    max_drive_time = IntegerField('Maximum drive time (in minutes)', validators=[Optional()])
    search_terms = StringField('Additional search terms', validators=[Optional()], description="Separate multiple search terms with commas")
    submit = SubmitField('Download')