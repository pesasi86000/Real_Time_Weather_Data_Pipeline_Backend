"""
Helpers Module
Common utility functions for the weather backend
"""

import logging
from flask import jsonify
from config import LOG_FORMAT, LOG_LEVEL


def setup_logger(name):
    """
    Configure logger for a module
    
    Args:
        name (str): Logger name (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    logger.propagate = False  # Prevent duplicate log entries from root logger

    # Only add handler if not already present
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def error_response(success, error, message, status_code=400):
    """
    Create a standardized error response
    
    Args:
        success (bool): Success status
        error (str): Error type/name
        message (str): Error message
        status_code (int): HTTP status code
        
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    return jsonify({
        'success': success,
        'error': error,
        'message': message
    }), status_code


def success_response(data, status_code=200):
    """
    Create a standardized success response
    
    Args:
        data (dict): Response data
        status_code (int): HTTP status code
        
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    response = {'success': True}
    response.update(data)
    return jsonify(response), status_code


def map_error_to_status(error_message):
    """
    Map a weather service error message to an appropriate HTTP status code
    and a short error title.

    Args:
        error_message (str): Error message string from the service layer

    Returns:
        tuple: (error_title: str, status_code: int)
    """
    msg = error_message.lower()
    if 'not found' in msg:
        return 'City not found', 404
    elif 'invalid' in msg and 'api' in msg:
        return 'Authentication error', 401
    elif 'rate limit' in msg or 'too many' in msg:
        return 'Rate limit exceeded', 429
    elif 'timeout' in msg:
        return 'Service unavailable', 503
    return 'Internal server error', 500
