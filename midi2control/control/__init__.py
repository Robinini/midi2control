"""
Generic function factory to create a function callable from the Mapping output

"""

def output(function, *args, **kwargs):
    """
    Generic closure to creates a callable function for deferred execution of the function, with the provided arguments

    :param function: function to execute
    :param args: un-named arguments
    :param kwargs: named arguments
    :return: mapping output function suitable to pass to device mapping
    """

    return lambda *map_args, **map_kwargs: function(*args, **kwargs)