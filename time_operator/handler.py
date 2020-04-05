from datetime import timedelta
from json import JSONDecodeError
from re import compile
from typing import List

import operator as op
import numpy as np
import json
# TODO: add ujson after check the build issue with alpine and pep517
# import ujson as json

Times = List[timedelta]

VALID_TIME_REGEX = '([0-9]+)?(\\:)?([0-9]{2})?(\\:)?([0-9]{2})\\.([0-9]{3})'
TIME_SEPARATOR = ':'
PRECISION_SEPARATOR = '.'
OPERATIONS = {
    '+': op.add,
    '-': op.sub,
    '*': op.mul,
    '/': op.truediv
}


class InvalidTimeFormat(Exception):
    """
    """
    def __init__(self, message):
        if message:
            self.message = message
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return (f'InvalidTimeFormat: time in the wrong format, '
                    f'expected HH:MM:SS.mmm.\n{self.message}')
        else:
            return (f'InvalidTimeFormat: time in the wrong format, '
                    f'expected HH:MM:SS.mmm.')


class OperationNotSupported(Exception):
    """
    """
    def __init__(self, message):
        if message:
            self.message = message
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return (f'OperationNotSupported: Time Operator could not '
                    f'operate your request.\n{self.message}')
        else:
            return (f'OperationNotSupported: Time Operator could not operate '
                    f'your request.')


def create_response(code: int, content: dict, message: str) -> dict:
    return json.dumps({
        'code': code,
        'data': content,
        'message': message
    })


def validated_string_time(time_string: str) -> bool:
    # Compile regex and try to full match the string
    # if it's not a full match it will return None
    # then add a statment to check if it's none to return
    # the string validity
    valid = compile(VALID_TIME_REGEX)
    return valid.fullmatch(time_string) is None


def parse_time(time_string: str) -> dict:
    # Split time on a string list
    splitted_time = time_string.split(TIME_SEPARATOR)

    # Get the seconds and miliseconds from the last element (mandatory on time)
    # and remove last element from list
    seconds, miliseconds = splitted_time[-1].split(PRECISION_SEPARATOR)
    splitted_time.pop()

    if len(splitted_time):
        *hour, minute = splitted_time
    else:
        hour, minute = [], []

    parsed_time = {
        'hour': int(hour[0]) if len(hour) else 0,
        'minute': int(minute) if isinstance(minute, str) else 0,
        'second': int(seconds),
        'milisecond': int(miliseconds),
    }

    return parsed_time


def decode_timedelta(time: timedelta) -> str:
    if time.days > 0:
        additional_hours = time.days * 24
        temp = str(time).split(' ')[2][:-3]
        hours = int(temp[:2])
        decoded = str(additional_hours + hours) + temp[2:]
    elif time.total_seconds() == 0.0:
        decoded = '0:00.000'
    else:
        decoded = str(time)[:-3]

    return decoded


def dict_to_time(obj: dict) -> timedelta:
    return timedelta(
        milliseconds=obj['milisecond'],
        seconds=obj['second'],
        minutes=obj['minute'],
        hours=obj['hour']
    )


def operate(operation: str, binary: bool, times: list, base: int) -> Times:
    if binary:
        if operation in ['+', '-'] and not base:
            a, b = sorted(times, reverse=True)
            result = [OPERATIONS[operation](a, b)]
        elif operation in ['/'] and not base:
            a, b = times
            result = [timedelta(seconds=OPERATIONS[operation](a, b))]
        elif base:
            result = [OPERATIONS[operation](np.array(times), base)]
        else:
            raise OperationNotSupported(f'The operation \'{operation}\' is not'
                                        f' supported for binary operations')
    else:
        if base and operation in ['+', '-']:
            result = list(OPERATIONS[operation](
                np.array(times),
                timedelta(seconds=base))
            )
        elif base and operation in ['*', '/']:
            result = list(OPERATIONS[operation](
                np.array(times),
                base)
            )
        elif operation in ['+', '-'] and not base:
            times = sorted(times)
            base = times[-1]
            for time in times:
                base = OPERATIONS[operation](base, time)
            result = base
        else:
            raise OperationNotSupported(f'The operation \'{operation}\' is '
                                        f'not supported for non binary '
                                        f'operations. For this you should '
                                        f'define a base to operate the times.')
    return result


def clean_results(times: Times):
    for i in range(len(times)):
        if times[i].total_seconds() < 0:
            times[i] = timedelta(0)

    return times


def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    message = ''
    try:
        # Decode JSON from request
        data = json.loads(req)

        # Get data for operation
        operation = data['operation']
        binary = data['binary']
        times = data['times']
        base = data['base'] if 'base' in data.keys() else 0

        # Verify times
        not_valid_request = True in [
            validated_string_time(test) for test in times
        ]

        # Stop execution if request is not valid
        if not_valid_request:
            raise InvalidTimeFormat('Times are not valid!.')

        # Transform times from str to datetime.timedelta
        times = [dict_to_time(parse_time(time)) for time in times]

        # Calculate result
        result = operate(operation, binary, times, base)
        # Clean results for negative timedeltas
        result = clean_results(result)
        # Decode times from timedelta to string (JSON decodable)
        result = [decode_timedelta(time) for time in result]

    except JSONDecodeError as exception:
        message = (f'Error trying to load input JSON.\nMalformed JSON.'
                   f'Traceback: {exception}')
        response = create_response(
            500,
            {},
            f'😔 Error in execution.\nMessage: {message}'
        )
        return response
    except InvalidTimeFormat as exception:
        message = (f'Error while validating times.\nTraceback: {exception}')
        response = create_response(
            500,
            {},
            f'😔 Error in execution.\nMessage: {message}'
        )
        return response
    except OperationNotSupported as exception:
        message = (f'Error while operating times.\nTraceback: {exception}')
        response = create_response(
            500,
            {},
            f'😔 Error in execution.\nMessage: {message}'
        )
        return response
    else:
        response = create_response(
            200,
            {'times': result},
            '😀 Successful execution!'
        )
        return response
