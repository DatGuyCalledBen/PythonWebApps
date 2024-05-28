import sys
import platform
import socket
import hashlib
import datetime

# WSGI application function
def application(environ, start_response):
    # Set response headers
    start_response('200 OK', [('Content-Type', 'text/plain')])

    # Test basic functionality
    message = 'Python WSGI Test Application\n'
    version_info = 'Python Version: {}\n'.format(platform.python_version())
    os_info = 'Operating System: {}\n'.format(platform.platform())
    hostname = 'Hostname: {}\n'.format(socket.gethostname())
    response = '\n'.join([message, version_info, os_info, hostname])

    # Test string manipulation
    string_example = 'hello world'
    reversed_string = 'Reversed String: {}\n'.format(string_example[::-1])
    uppercase_string = 'Uppercase String: {}\n'.format(string_example.upper())
    response += reversed_string + uppercase_string

    # Test data structures
    numbers = [1, 2, 3, 4, 5]
    list_info = 'List Sum: {}\n'.format(sum(numbers))
    dictionary = {'a': 1, 'b': 2, 'c': 3}
    dictionary_info = 'Dictionary Keys: {}\n'.format(', '.join(dictionary.keys()))
    response += list_info + dictionary_info

    # Test datetime functionality
    current_time = 'Current Time: {}\n'.format(datetime.datetime.now())
    response += current_time

    # Test hashlib - calculate MD5 hash of a string
    input_string = 'test'
    md5_hash = hashlib.md5(input_string).hexdigest()
    md5_info = 'MD5 Hash of "{}": {}\n'.format(input_string, md5_hash)
    response += md5_info

    return [response.encode()]
