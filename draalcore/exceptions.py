#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base exceptions"""


class AppException(Exception):
    """Base class for application errors."""
    pass


class RestApiException(AppException):
    """Base class for ReST API errors."""
    pass


class FactoryException(AppException):
    """Model(s) factory processing related error."""
    pass


class ModelNotFoundError(RestApiException):
    """Invalid model for specified for ReST API call."""
    pass


class ModelAccessDeniedError(RestApiException):
    """Model is not allowed to be accessed via ReST API."""
    pass


class ModelSerializerNotDefinedError(RestApiException):
    """No SERIALIZER attribute defined for model."""
    pass


class ModelSerializerNotFoundError(RestApiException):
    """Invalid serializer specified by model's SERIALIZER attribute."""
    pass


class DataParsingError(RestApiException):
    """Error in parsing and validating ReST API data."""
    pass


class ModelManagerError(RestApiException):
    """Error in model manager processing."""
    pass


class ActionError(AppException):
    """Action error."""
    pass
