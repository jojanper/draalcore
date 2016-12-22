#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base serializer object class with paging and search support"""

# System imports
import time
import logging
from math import floor
from django.db.models.query import QuerySet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, Page

# Project imports
from .req_query import QueryRequest
from draalcore.factory import Factory
from .response_data import ResponseData
from draalcore.rest.model import ModelContainer, SerializerFinder
from draalcore.exceptions import RestApiException, ModelManagerError


logger = logging.getLogger(__name__)


class SerializerPaginatorMixin(object):
    """
    Manage queryset data by either providing paginated data where data is
    split across several pages or limiting the data by proving only certain
    data items from specified range interval.

    Supports DataTables v1.9 and v1.10 server side pagination formats.
    """

    echo_tag = None
    start_tag = None
    length_tag = None
    echo_format = None

    page_formats = [
        # DataTables v1.9 or earlier
        {
            'echo_tag': 'sEcho',
            'start_tag': 'iDisplayStart',
            'length_tag': 'iDisplayLength',
            'echo_format': {
                'total': 'iTotalRecords',
                'filtered': 'iTotalDisplayRecords'
            }
        },

        # DataTables v1.10 or later
        {
            'echo_tag': 'draw',
            'start_tag': 'start',
            'length_tag': 'length',
            'echo_format': {
                'total': 'recordsTotal',
                'filtered': 'recordsFiltered'
            }
        }
    ]

    def _decode_page_format(self):
        """Determine pagination format for the request"""

        params = self.params
        for page_format in self.page_formats:
            self.start_tag = page_format['start_tag']
            self.length_tag = page_format['length_tag']
            self.echo_tag = page_format['echo_tag']
            self.echo_format = page_format['echo_format']
            if self.start_tag in params and self.length_tag in params:
                return

    @property
    def display_length(self):
        """Return length of the output data"""
        return int(self.params[self.length_tag])

    @property
    def display_start(self):
        """Return start offset for the output data"""
        return int(self.params[self.start_tag])

    @property
    def _is_limiting(self):
        """Return True if output data need to be limited in range"""
        params = self.params
        if self.start_tag in params and self.length_tag in params:
            try:
                if self.display_start >= 0 and self.display_length > 0:
                    return True
            except ValueError:
                return False

        return False

    @property
    def _is_paging(self):
        """Return True if data need to be paginated"""
        if self._is_limiting and self.echo_tag in self.params:
            return True

        return False

    @property
    def _page_number(self):
        """Return current page number for the data"""
        page = int(floor(self.display_start / self.display_length) + 1)
        return page

    def serialize(self):
        """Serialize data"""
        self._decode_page_format()
        super(SerializerPaginatorMixin, self).serialize()

        # Data is paginated
        if self._is_paging:
            self._paginator = Paginator(self._query, self.display_length)
            try:
                self._query = self._paginator.page(self._page_number)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                self._query = self._paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver no results.
                self._query = self.serializer.Meta.model.objects.none()

        # Provide data only from specified range interval
        elif self._is_limiting:
            count = self._query.count()
            start = self.display_start
            end = min(start + self.display_length, count)
            self._query = self._query[start:end]

        return self

    def _page_data(self, data):
        """Return paged data in correct output format"""
        records_count = self._paginator.count
        total_count = self._unfiltered_query.count() if self._unfiltered_query else records_count
        return {self.echo_tag: self.params[self.echo_tag],
                self.echo_format['total']: total_count,
                self.echo_format['filtered']: records_count,
                'aaData': data}

    @property
    def data(self):
        """Return serialized data"""
        data = super(SerializerPaginatorMixin, self).data
        return self._page_data(data) if self._is_paging else data


class SerializerSearchMixin(object):
    """
    Apply custom search to queryset data.

    Supports DataTables v1.9 and v1.10 server side search formats.
    """

    # URL parameter for search parameters
    search_tag = None

    # Ordering format
    order_format = None

    # Manager method implementing the query
    search_filter = 'filter_on_search'

    search_formats = [
        # DataTables v1.9 or earlier
        {
            'search_tag': 'sSearch',
            'order_format': {
                'column': 'iSortCol_0',
                'data': 'mDataProp_{0}',
                'order': 'sSortDir_0'
            }
        },

        # DataTables v1.10 or later
        {
            'search_tag': 'search[value]',
            'order_format': {
                'column': 'order[0][column]',
                'data': 'columns[{0}][data]',
                'order': 'order[0][dir]'
            }
        }
    ]

    def _decode_search_format(self):
        """Determine search format for the request"""

        for item in self.search_formats:
            self.search_tag = item['search_tag']
            self.order_format = item['order_format']
            if self.search_tag in self.params:
                return

    @property
    def _needs_search(self):
        """Return True if search need to be executed, False otherwise"""
        return self.search_tag in self.params

    @property
    def search_params(self):
        """Return search parameters"""
        return self.params.get(self.search_tag, '').lower()

    def _sorted_filter(self, query):
        """Apply ordering to specified queryset based on URL parameters"""

        column_mapper = getattr(self, 'search_column_name_map', None)
        if column_mapper is None:
            column_mapper = getattr(self.serializer.Meta.model, 'SORT_COLUMN_NAME_MAP', None)

        # Name mapper available
        if column_mapper:
            sort_col_num = self.params.get(self.order_format['column'], 0)
            sort_col_name = self.params.get(self.order_format['data'].format(sort_col_num), 'value')

            # Name to model field mapping existing
            if sort_col_name in column_mapper:
                sort_dir = self.params.get(self.order_format['order'], 'asc')
                sort_dir_prefix = (sort_dir == 'desc' and '-' or '')
                sort_col = column_mapper[sort_col_name]
                query = query.order_by('{0}{1}'.format(sort_dir_prefix, sort_col))

        return query

    def _search_filter(self, query):
        """Apply search to specified queryset"""
        self._decode_search_format()
        query = self._sorted_filter(query)
        if self._needs_search and self.search_params:
            kwargs = {'base_query': query}
            self._unfiltered_query = query
            req_obj = QueryRequest(method=self.search_filter,
                                   query_args=self.search_params,
                                   query_kwargs=kwargs)
            response = self.factory.do_query(req_obj)
            query = response.query

        return query


class BaseSerializerObject(object):
    """
    Base class that defines data query and related serialization. Requires that factory,
    serializer, and fields attributes are defined by the implementing class. The factory
    acts as interface towards acquiring the data, the serializer does the actual data
    serialization, and the fields defines what attributes from the data are to be used
    in the serialization.
    """

    # Factory
    factory = None

    # Serializer
    serializer = None

    # Fields used for serialization
    fields = []

    # URL parameter for specifying which fields to serialize
    fields_tag = 'fields'

    # Data fields for custom serialization
    custom_fields = []

    has_id = False
    has_meta = False
    has_history = False

    def __init__(self, request_obj):
        self._query = None
        self._unfiltered_query = None
        self._request_obj = request_obj

        # Manager method and kwargs that are assigned through set_query() method
        self._manager_method = None
        self._manager_kwargs = None

        if not self.fields and self.serializer:
            self.fields = self.serializer.Meta.fields + self.custom_fields

    @classmethod
    def create(cls, request_obj, model_cls):
        finder_obj = SerializerFinder(model_cls)

        # Use custom serializer object if such is defined for the model, otherwise default serializer object is used
        serializer_obj_cls = finder_obj.object
        if serializer_obj_cls is None:
            obj = cls(request_obj)
            obj.factory = Factory(model_cls.objects)
            obj.serializer = SerializerFinder(model_cls).serializer
            obj.fields = obj.serializer.Meta.fields
        else:
            obj = serializer_obj_cls(request_obj)
            obj.factory = Factory(model_cls.objects)

        return obj

    @property
    def request_obj(self):
        """Request object"""
        return self._request_obj

    @property
    def user(self):
        """User requesting the action"""
        return self.request_obj.user

    @property
    def kwargs(self):
        """Return kwargs from URL configuration"""
        return self.request_obj.kwargs

    @property
    def params(self):
        """Return URL parameters"""
        return self.request_obj.url_params

    @property
    def get_custom_fields(self):
        """
        Return custom fields for serialization. Custom fields are generated after
        the queryset has been serialized. Custom fields may use the entire
        serialized data when generating the field data.
        """
        # Fields tag present in URL
        fields = []
        if self.fields_tag in self.params:

            # Accept only known fields
            out_fields = self.get_input_fields
            for field in out_fields:
                if field in self.custom_fields:
                    fields.append(field)

            return fields

        return self.custom_fields

    @property
    def get_input_fields(self):
        """Return URL fields as list, if any"""
        return self.params[self.fields_tag].split(',') if self.fields_tag in self.params else []

    @property
    def get_fields(self):
        """Return fields used for serialization"""
        fields = []
        if self.fields_tag in self.params:
            out_fields = self.get_input_fields
            for field in out_fields:
                if self.fields:
                    if field in self.fields:
                        fields.append(field)

        return fields if fields else self.fields

    def _default_query(self):
        """Default query returns all items"""
        method = self._manager_method or 'get_data_listing'
        kwargs = self._manager_kwargs if self._manager_method else self.params
        return QueryRequest(method=method, query_kwargs={'kwargs': kwargs})

    def set_query(self, manager_method, kwargs):
        self._manager_method = manager_method
        self._manager_kwargs = kwargs

    def get_request_object(self):
        return getattr(self, '_' + self.kwargs.get('fn', 'default_query'))()

    def serialize(self):
        """Define the queryset for data serialization"""

        # Query specification
        req_obj = self.get_request_object()

        # Base query based on specification
        obj = self.factory.do_query(req_obj)

        # Search to base query unless it's model history
        query = obj.query
        if not self.has_history and not self.has_id:
            if hasattr(self, '_search_filter'):
                query = self._search_filter(query)
            if hasattr(self, '_post_query'):
                query = self._post_query(query)

        self._query = query

        return self

    @property
    def data(self):
        """Return serialized data"""

        if self.has_meta:
            return self._query

        # Base data serialization
        many = True if isinstance(self._query, (QuerySet, Page)) else False
        data = self.serializer(self._query, fields=self.get_fields, many=many).data

        # Custom field data serialization
        for field in self.get_custom_fields:
            fn = getattr(self, '_set_' + field, None)
            if fn:
                for index, item in enumerate(data):
                    fn(self._query[index], item)

        return data


class SerializerDataObject(SerializerPaginatorMixin,
                           SerializerSearchMixin,
                           BaseSerializerObject):
    """Base class for model data serialization with search and pagination support"""
    pass


class SerializerModelMetaObject(BaseSerializerObject):
    """Base class for model meta serialization"""

    has_meta = True

    def serialize(self):
        """Define the queryset for model meta serialization"""
        self._query = self.serializer.Meta.model.serialize_meta()
        return self


class SerializerModelDataObject(BaseSerializerObject):
    """
    Base class for serializing model data object. The request object must include
    proper data object that is then serialized.
    """

    has_id = True

    def serialize(self):
        """Serialize the data that was assigned as queryset for the request object"""
        self._query = self.request_obj.queryset
        return self


class SerializerDataItemObject(BaseSerializerObject):
    """
    Base class for serializing model data item. The class receives model ID as input
    and the fetches the data from database.
    """

    has_id = True
    data_tag = 'id'

    @property
    def data_id(self):
        """Return requested data item ID"""
        return self.kwargs[self.data_tag]

    def get_request_object(self):
        """Return model data based on ID"""
        return QueryRequest(method='get_model', query_args=[self.data_id])

    def serialize(self):
        try:
            return super(SerializerDataItemObject, self).serialize()
        except ModelManagerError:
            raise RestApiException('ID {} not found'.format(self.data_id))
