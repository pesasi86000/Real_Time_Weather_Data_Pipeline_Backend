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
