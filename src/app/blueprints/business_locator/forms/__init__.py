"""
This module contains the form definitions for the business locator application.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional


class SearchForm(FlaskForm):
    """
    A form for searching business locations using various criteria.

    Attributes:
        location (StringField): The location to search in. This field is required.
        search_by (SelectField): The method to search by. Choices are 'Radius', 'Drive Time', or 'Both'.
            This field is required.
        radius (IntegerField): The search radius in miles. This field is optional.
        max_drive_time (IntegerField): The maximum drive time in minutes. This field is optional.
        search_terms (StringField): The search terms, separated by commas. This field is optional.
        submit (SubmitField): The submit button for the form.
    """

    location = StringField('Location', validators=[DataRequired()])
    search_by = SelectField('Search by', choices=[('r', 'Radius'), ('d', 'Drive Time'), ('b', 'Both')],
                            validators=[DataRequired()])
    radius = IntegerField('Radius (in miles)', validators=[Optional()])
    max_drive_time = IntegerField('Maximum drive time (in minutes)', validators=[Optional()])
    search_terms = StringField('Search terms', validators=[Optional()],
                               description="Separate multiple search terms with commas")
    submit = SubmitField('Download')
