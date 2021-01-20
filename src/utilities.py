# Author: Marco Urbano.
# Date: 17 January 2021.
# Description: this python file contains all the so called utility functions that belongs to no class.
# Notes:


"""
    Simple function to check the command line arguments.
    Returns True if the syntax of the arguments is correct, False otherwise.
    Users can submit their custom configuration to set the following:
    - mitmproxy host
    - mitmproxy port
    - benchmark host
    - benchmark port

    array argv should contain 9 arguments if this happens. This is explained because the syntax is the following:

    Interceptor.py(1) -ph(2) PROXY_HOST(3) -pp(4) PROXY_PORT(5) -bh(6) BENCHMARK_HOST(7) -bp(8) BENCHMARK_PORT(9)

    checkArguments does only a check on the 2nd, 4th, 6th, 8th position to assure that the user knows the name
    of the parameters to pass to the script. The correctness of the remaining will be assumed if the first check is
    passed.
    """


def check_arguments(argv):
    # If argv contains n elements, with n != 9, the user entered wrong arguments.
    if len(argv) == 9:
        if argv[2] == '-ph' and argv[4] == '-pp' and argv[6] == '-bh' and argv[8] == '-bp': return True

    return False
