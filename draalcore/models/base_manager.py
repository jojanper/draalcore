#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Manager implementations for application models"""

# System imports
import logging
import inspect
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet

# Project imports
from draalcore.models.fields import AppModelFieldParserIterator, get_related_model
from draalcore.middleware.current_user import get_current_user
from draalcore.exceptions import DataParsingError, ModelManagerError

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2014-2015,2021"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"

logger = logging.getLogger(__name__)


class SearchMixin(object):
    """
    This will be subclassed by both the Object Manager and the QuerySet. By doing it this way,
    you can chain these functions, along with filter(). A simpler approach would define these
    in MyClassManager(models.Manager), but won't let you chain them, as the result of each is
    a QuerySet, not a Manager.

    See http://stackoverflow.com/questions/7461038/how-to-use-custom-managers-in-chain-queries#answer-13434174
    """

    search_fields = []

    def q_for_search_field(self, search_key, search_fields):
        """
        Given a search key from the search text, return the Q object which you
        can filter on, to show only objects containing this key.
        """
        q = Q()
        for field in search_fields:
            kwargs = {
                field: search_key
            }
            q = q | Q(**kwargs)

        return q

    def q_for_search(self, search, search_fields):
        """
        Given the text from the search box, search on each word in this text.
        Return a Q object which you can filter on.
        """
        q = Q()
        if search:
            searches = search.split()
            for search_key in searches:
                q = q & self.q_for_search_field(search_key, search_fields)

        return q

    def filter_on_search(self, search, base_query, search_fields=None):
        """Return the objects containing the search terms."""
        if not search_fields:
            search_fields = getattr(self.model, 'SEARCH_FIELDS', self.search_fields)

        return base_query.filter(self.q_for_search(search, search_fields))


class SearchQuerySet(QuerySet, SearchMixin):
    pass


class BaseManager(models.Manager, SearchMixin):
    """Base manager for application models"""

    class Meta:
        abstract = True

    def get_queryset(self):
        if hasattr(self.model, 'STATUS_ACTIVE'):
            return SearchQuerySet(self.model, using=self._db).filter(status=self.model.STATUS_ACTIVE)

        return SearchQuerySet(self.model, using=self._db).all()

    def prepare_model_field(self, field_name, field, value):
        """
        Map the field value into model object(s).

        Parameters
        ----------
        field_name
           Model field name.
        field
           Model field object.
        value
           Field value.

        Returns
        -------
        str | int | list | object | dict
           Mapped value if field is foreign key or related model, otherwise the input value is returned unmodified.
        """

        # Foreign key, read the reference object
        if field.fk:
            if not isinstance(value, models.Model):
                value = self.fetch_fk_data(field_name, value)

        # Related field, read the objects(s)
        elif field.related and value:
            objs = []
            for item in value:
                try:
                    objs.append(self.model.objects.get(id=item))
                except self.model.DoesNotExist:
                    msg = 'ID {} does not exist for field {}'.format(item, field.name)
                    raise DataParsingError(msg)
            value = objs

        # Return final field value
        return value

    def fetch_fk_data(self, field_name, field_kwargs, only_fields=[]):
        """
        Fetch foreign key model object for specified data.

        Parameters
        ----------
        field_name
           Model field name.
        field_kwargs
           Parameters for field fetching.
        only_fields
           Fields to fetch for the model object.

        Returns
        -------
        Object
           Model object.

        Raises
        ------
        DataParsingError
           Model data could not be fetched for the given parameters.
        """

        try:
            # Object value should be None
            if field_kwargs is None:
                return None

            # Read the model data for specified field within the model definition
            cls = get_related_model(self.model._meta.get_field(field_name))
            return self.get_model(model=cls, model_kwargs=field_kwargs, only_fields=only_fields)

        except ModelManagerError:
            msg = "Value %s for item '%s' does not exist" % (field_name, field_kwargs)
            raise DataParsingError(msg)

    def get_sql_select_fields(self, model, iteration):
        """
        Determine related and prefetch fields for specified model.

        Parameters
        ----------
        model
           Model class
        iteration: int
           Iteration counter (to limit the recursion).

        Returns
        -------
        set
           Related and prefetch fields, updated iteration counter.
        """
        select = []
        prefetch = []

        iteration += 1
        if iteration > 10:
            return select, prefetch, iteration

        # Only application models are analyzed
        if 'draalcore.' in inspect.getmodule(model).__name__:
            for field in AppModelFieldParserIterator.create(model._meta):
                if field.fk or field.related:
                    add_name = True
                    name = field.name
                    target = select if field.fk else prefetch
                    fk_related, fk_prefetch, iteration = self.get_sql_select_fields(field.related_model, iteration)
                    for related in [fk_related, fk_prefetch]:
                        for fld in related:
                            add_name = False
                            target.append('{}__{}'.format(name, fld))

                    if add_name:
                        target.append(name)

        return select, prefetch, iteration

    def get_data_listing(self, kwargs):
        """Return queryset containing all model items."""
        iteration = 0
        select, prefetch, iteration = self.get_sql_select_fields(self.model, iteration)
        query = self.select_related(*select).prefetch_related(*prefetch).all()

        # Call to custom manager method that is exposed to public use
        if 'call' in kwargs:
            call = 'public_{}'.format(kwargs.get('call'))
            if (hasattr(self, call)):
                query = getattr(self, call)(query, kwargs)
            else:
                raise ModelManagerError('Unsupported call value to {}'.format(kwargs.get('call')))

        return query.order_by('id')

    def get_model(self, model_kwargs, model=None, only_fields=[]):
        """
        Get model object for specified data.

        Parameters
        ----------
        model_kwargs
           Model query parameters.
        model
           Model class used to be used. Value None indicates that manager's model should be used.
        only_fields
           Fields to fetch for the model object.

        Returns
        -------
        Object
           Model object.

        Raises
        ------
        ModelManagerError
           Model could not read from database.
        """

        try:
            # Model parameter is actually the model ID
            if not isinstance(model_kwargs, dict):
                model_kwargs = {'id': int(model_kwargs)}

            model = self.model if model is None else model
            select, prefetch, iteration = self.get_sql_select_fields(model, 0)

            # Fetch the actual data
            return model.objects.only(*only_fields).select_related(*select).prefetch_related(*prefetch).get(**model_kwargs)

        except model.DoesNotExist as e:
            msg = '%s Query params: %s' % (e.args[0], model_kwargs)
            raise ModelManagerError(msg)

    def parse_data(self, related_fields_parser, **kwargs):
        """
        Parse and validate input data for model creation and/or editing.

        Parameters
        ----------
        related_fields_parser
           True if model's related fields are parsed, False for traditional fields.
        kwargs
           Model field parameters.

        Returns
        -------
        dict
           Model creation/editing parameters.

        Raises
        ------
        DataParsingError
           Parameter validation failed.
        """

        params = {}

        # Errors related to missing fields
        missing_fields = []

        # Loop the model fields, validate data
        for field in self.model.field_parser(related_fields_parser=related_fields_parser):
            read_data = False
            field_name = field.name
            if field.mandatory:
                # Mandatory field must be present
                if not (field_name in kwargs):
                    missing_fields.append(field_name)
                else:
                    read_data = True
            elif field.optional and field_name in kwargs:
                read_data = True

            # Read field data
            if read_data:
                value = kwargs[field_name]

                # Validate data type, raises error if not valid
                field.validate_type(field_name, value)

                mgr = field.related_model.objects if related_fields_parser else self
                params[field_name] = mgr.prepare_model_field(field_name, field, value)

        if missing_fields:
            msg = 'Following data fields are required: %s' % (', '.join(missing_fields))
            raise DataParsingError(msg)

        return params

    def create_model(self, **kwargs):
        """
        Create new model item.

        Parameters
        ----------
        kwargs
           Model creation parameters.

        Returns
        -------
        Object
           Created model.
        """

        # Validate field parameters
        create_params = self.parse_data(False, **kwargs)
        related_params = self.parse_data(True, **kwargs)

        # Create the model
        obj = self.create(**create_params)

        # Create related fields
        for field, value in related_params.items():
            if value:
                getattr(obj, field).add(*value)
                obj.create_related_event(field, value)

        return obj

    def edit_model(self, model_obj, **kwargs):
        """
        Edit model item.

        Parameters
        ----------
        model_obj
           Model object under editing.
        kwargs
           Model edit parameters.

        Returns
        -------
        Object
           Edited model.
        """

        # Validate field parameters
        edit_params = self.parse_data(False, **kwargs)
        related_params = self.parse_data(True, **kwargs)

        # Edit the model
        model_obj.set_values(**edit_params)

        # Edit related fields
        for field, value in related_params.items():
            rel_obj = getattr(model_obj, field)

            # Determine if data is changed
            objs = rel_obj.all()
            edit_ids = list(set([item.id for item in value]))
            obj_ids = [obj.id for obj in objs]
            is_changed = not (set(edit_ids) == set(obj_ids))

            # Update the changed data
            if is_changed:
                rel_obj.clear()
                model_obj.create_event(get_current_user(), 'Clear data from field {}'.format(field))
                if value:
                    rel_obj.add(*value)
                    model_obj.create_related_event(field, value)

        return model_obj

    def history(self, model_id):
        """
        Return history for specified model ID.

        Parameters
        ----------
        model_id
           Model ID.

        Returns
        -------
        QuerySet | list
           History as queryset or empty list if no history items found.
        """
        data = []
        obj = self.filter(id=model_id)
        if obj and hasattr(obj[0], 'get_events'):
            data = obj[0].get_events()

        return data
