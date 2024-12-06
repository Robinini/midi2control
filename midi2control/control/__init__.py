"""
Generic function factory to create a function callable from the Mapping output

"""

def output(function, *args, **kwargs):
    """
    Function factory to defer the execution of argument function, with the provided arguments
    :param function: function to execute
    :param args: un-named arguments
    :param kwargs: named arguments
    :return: Prepared function to execute
    """

    return lambda *map_args, **map_kwargs: function(*args, **kwargs)