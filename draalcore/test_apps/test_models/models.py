#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test models"""

# System imports
from django.db import models

# Project imports
from draalcore.models.base_model import BaseModel, ModelLogger, ModelBaseManager
from draalcore.models.fields import (AppModelCharField, AppModelForeignKey, AppModelManyToManyField,
                                     AppModelTextField, AppModelForeignObjectKey)

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2014,2021"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


class TestModel(ModelLogger):
    """Simple test model that can be used only internally"""

    __test__ = False

    EXTERNAL_API = False
    SERIALIZER = 'TestModelSerializer'

    name = AppModelCharField(mandatory=True, max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'testmodel'

    def __str__(self):
        return "%s(%s,%s)" % (self.__class__.__name__, self.id, self.name)


class TestModelBaseModel(BaseModel):
    """Model that is derived from BaseModel"""

    __test__ = False

    EXTERNAL_API = False

    name = AppModelCharField(mandatory=True, max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'testmodelbasemodel'


class TestModel2Manager(ModelBaseManager):
    def public_call(self, query, kwargs):
        return query


class TestModel2(ModelLogger):
    """Simple test model that can be accessed also externally (e.g., via ReST API)"""

    __test__ = False

    EXTERNAL_API = True
    SERIALIZER = 'TestModel2Serializer'

    ADDITIONAL_SERIALIZE_FIELDS = ['actions', 'type']

    PARTIAL_UPDATE_FIELDS_META = ['name', 'comments', 'free_text', 'model1', 'model2', 'model3', 'meta']

    SEARCH_FIELDS = ['name__contains']

    SORT_COLUMN_NAME_MAP = {
        'id': 'id',
        'name': 'name'
    }

    name = AppModelCharField(mandatory=True, max_length=256, blank=True, null=True,
                             verbose_name='Name')
    comments = AppModelCharField(optional=True, max_length=256, blank=True, null=True)
    free_text = AppModelTextField(optional=True, blank=True, null=True, read_only=True)
    model1 = AppModelForeignKey(TestModel, mandatory=True, related_name="model1", on_delete=models.CASCADE)
    model2 = AppModelForeignKey(TestModel, optional=True, blank=True, null=True, related_name="model2", on_delete=models.CASCADE)
    model3 = AppModelManyToManyField(TestModel, optional=True, blank=True, related_name="model3")
    meta = AppModelForeignObjectKey(TestModel, optional=True, null=True, blank=True,
                                    help_text='Metadata information', label='Meta data',
                                    on_delete=models.CASCADE)
    duration = models.FloatField(default=-1, blank=True, null=True, verbose_name='Test duration')

    objects = TestModel2Manager()

    class Meta:
        db_table = 'testmodel2'

    def __str__(self):
        return "%s(%s,%s,%s)" % (self.__class__.__name__, self.id, self.name, self.model1)

    def serialize_type(self):
        return 'type A'


class TestModel3(models.Model):
    """Simple test model that don't have serializer defined"""

    __test__ = False

    EXTERNAL_API = True

    name = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'testmodel3'

    def __str__(self):
        return "%s(%s,%s)" % (self.__class__.__name__, self.id, self.name)


class TestModel4(ModelLogger):
    """Simple test model that has invalid serializer defined"""

    __test__ = False

    EXTERNAL_API = True
    SERIALIZER = 'TestModel4Serializer'

    name = AppModelCharField(optional=True, max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'testmodel4'

    def __str__(self):
        return "%s(%s,%s)" % (self.__class__.__name__, self.id, self.name)


class TestModel5(ModelLogger):
    """Simple test model that has serializer object attribute defined but not implemented"""

    __test__ = False

    EXTERNAL_API = True
    SERIALIZER_OBJECT = 'TestModel5SerializerObject'

    name = AppModelCharField(optional=True, max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'testmodel5'

    def __str__(self):
        return "%s(%s,%s)" % (self.__class__.__name__, self.id, self.name)


class TestModel6Manager(ModelBaseManager):
    def test_model6(self, kwargs):
        return self.all()


class TestModel6(ModelLogger):
    """Simple test model that has serializer object attribute defined and implemented"""

    __test__ = False

    EXTERNAL_API = True
    SERIALIZER_OBJECT = 'TestModel6SerializerObject'

    name = AppModelCharField(optional=True, max_length=256, blank=True, null=True)

    objects = TestModel6Manager()

    class Meta:
        db_table = 'testmodel6'
