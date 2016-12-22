#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Serializers for test models"""

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2015"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


# Project imports
from draalcore.rest.base_serializers import ModelSerializer
from .models import TestModel, TestModel2, TestModel6
from draalcore.rest.serializer_object import BaseSerializerObject


class TestModelSerializer(ModelSerializer):
    class Meta:
        model = TestModel
        fields = TestModel.serializer_fields()


class TestModel2Serializer(ModelSerializer):

    model1 = TestModelSerializer()
    model3 = TestModelSerializer(many=True)
    meta = TestModelSerializer()

    class Meta:
        model = TestModel2
        fields = TestModel2.serializer_fields()


class TestModel6Serializer(ModelSerializer):
    class Meta:
        model = TestModel6
        fields = TestModel6.serializer_fields()


class TestModel6SerializerObject(BaseSerializerObject):

    serializer = TestModel6Serializer
    custom_fields = ['size', 'request_user']

    def _set_size(self, obj, item):
        item['size'] = None

    def _set_request_user(self, obj, item):
        item['request_user'] = self.user.username

    def _post_query(self, query):
        return query
