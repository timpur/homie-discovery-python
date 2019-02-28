import re
from itertools import zip_longest

valid_topic = r"^([^\/\s\#\+]+|\+)(\/([^\/\s\#\+]+|\+|\#))*$|^\#$"


def topic_matches_sub(sub, topic):
    if not(re.match(valid_topic, sub) and re.match(valid_topic, topic)):
        return False
    for sub_part, topic_part in zip_longest(sub.split("/"), topic.split("/")):
        if sub_part and not topic_part or not sub_part and topic_part:
            return False
        if sub_part == '#':
            break
        elif sub_part == '+' or sub_part == topic_part:
            continue
        else:
            return False
    return True


def data_down(data):
    if isinstance(data, bytearray):
        return data
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data.encode()

    raise Exception('data must be type string')


def data_up(data):
    if isinstance(data, str):
        return data
    if isinstance(data, bytearray):
        return data.decode()
    if isinstance(data, bytes):
        return data.decode()

    raise Exception('data must be type bytearray')


def version_down(major, minor, bugfix):
    if not isinstance(major, int) or not isinstance(minor, int) or not isinstance(bugfix, int):
        raise ValueError('params must be type int')
    return f"{major}.{minor}.{bugfix}"


def version_up(version):
    if not isinstance(version, str):
        raise ValueError('version must be type string')
    major, minor, bugfix = map(int, version.split('.'))
    return (major, minor, bugfix)


def version_supported(supported, version):
    s_major, s_minor, _ = version_up(supported)
    major, minor, _ = version_up(version)
    return major == s_major and minor >= s_minor


# def split_at_nth_index(value, sub_str, n):
#     if n > 0:
#         index = 0
#         for i in range(n):
#             try:
#                 index = value.index(sub_str, index + 1)
#             except ValueError:
#                 raise Exception(f"'{sub_str}' not found for the {i + 1} times")
#     elif n < 0:
#         index = len(value)
#         for i in range(abs(n)):
#             try:
#                 index = value.rindex(sub_str, 0, index - 1)
#             except ValueError:
#                 raise Exception(f"'{sub_str}' not found for the {-i - 1} times")
#     return [value[:index], value[index + 1:]]
