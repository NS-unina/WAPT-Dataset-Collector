# Author: Marco Urbano.
# Date: 8 January 2021.
# Description: this is a simple Python script that uses mitmproxy to record http request/responses.
# Notes:
#           To run mitmproxy directly from Python:
#           - https://stackoverflow.com/questions/51893788/using-mitmproxy-inside-python-script

#           If this script will be executed in a dockerized environment with a networks that assigns
#           IP Addresses dynamically, it will probably be the last container to be executed. This
#           is needed because Interceptor.py needs to know which hosts (with their IP's) will send it
#           requests and which container runs the Benchmark. To assure that the container that runs this
#           script is the last one executed check:
#           - https://medium.com/better-programming/a-look-at-docker-composes-bootup-sequence-1f597049cc65
#
#           Docker API reference manual:
#           - https://docker-py.readthedocs.io/en/stable/api.html#networks
#

from mitmproxy.options import Options
from mitmproxy.proxy.config import ProxyConfig
from mitmproxy.proxy.server import ProxyServer
from mitmproxy.tools.dump import DumpMaster

# Used to read command line arguments with argv.
import sys

# Importing the custom addon used to save http requests/responses as JSON.
from HTTPLogger import *

# Using requests in order to obtain the JSON string describing the network built by host's Docker compose.
# The request will only be possible if the host's docker socket is shared with the container that
# runs this script.
import socket

import argparse

if __name__ == "__main__":
    ################### START MITMPROXY AND BENCHMARK DEFAULT SETTINGS VARIABLES ###################
    # The following default values are intended to be used if the script is gonna be executed on the
    # same machine that runs the benchmark server.

    # Variables to identify ports and addresses of mitmproxy and the benchmark http server.
    proxy_port = 8888
    proxy_host = '127.0.0.1'
    benchmark_port = 8080
    benchmark_host = '127.0.0.1'
    benchmark_protocol = 'http://'
    # String to identify the path of the javascript code used to capture events from the browser of the pentester.
    javascript_path = "./action_recording.js"

    # httplogger_addon is the instance of HTTPLogger class employed to describe the addon that performs the
    # interception. If this script will be executed in container mode, this object will be replaced by one
    # instance that contains also the dictionary with the info about other containers on the same net.
    http_logger_addon = None
    ################### END MITMPROXY AND BENCHMARK DEFAULT SETTINGS VARIABLES #####################

    # Reading command line arguments (if there any)
    cmd_arg = len(sys.argv)
    if cmd_arg > 1:
        # delegate parsing task to argparse library.
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument("-mode", "--mode", default='standalone',
                                help="default --mode is 'standalone'. This script can be used also "
                                     + "as docker container by submitting 'container'.")
        # -ph(2) PROXY_HOST(3) -pp(4) PROXY_PORT(5) -bh(6) BENCHMARK_HOST(7) -bp(8) BENCHMARK_PORT(9)
        arg_parser.add_argument("-ph","-proxy_host", default=proxy_host,
                                help="IP Address of the proxy")
        arg_parser.add_argument("-pp", "-proxy_port", default=proxy_port,
                                help="the port used by the proxy to receive requests")
        arg_parser.add_argument("-bh", "-benchmark_host", default=benchmark_host,
                                help="IP Address of the benchmark")
        arg_parser.add_argument("-bp", "-benchmark_port", default=proxy_port,
                                help="the port that the benchmark webserver will use to receive requests")
        args = arg_parser.parse_args()

        # When executed as a Docker container it'll perform a quick check to discover if the 'benchmark'
        # container has been correctly executed. (here we perform an additional check to ensure that
        # current container has been named 'interceptor')
        if args.mode == 'container':
            # Containers is a dictionary with key=IP, value=hostname
            containers = {}

            try:
                benchmark_host = socket.gethostbyname('benchmark')
                containers[benchmark_host] = 'benchmark'
            except socket.gaierror as gai_error:
                print("docker-compose.yml doesn't define any container named 'benchmark'! Define it and retry!\n")
                raise gai_error
            # checking that current container has been correctly named as 'interceptor'
            try:
                proxy_host = socket.gethostbyname('interceptor')
                containers[proxy_host] = 'interceptor'
            except socket.gaierror as gai_error:
                print("docker-compose.yml doesn't define any container named 'interceptor'! Define it and retry!\n")
                raise gai_error

            # construct the addon instance with the dictionary initially composed only by the addresses of
            # benchmark and interceptor itself.
            http_logger_addon = HTTPLogger(containers, javascript_path)
        else:
            # If the syntax is correct, change default variable values to custom ones.
            http_logger_addon = HTTPLogger(None, javascript_path)
            proxy_host = args.ph
            proxy_port = args.pp
            benchmark_host = args.bh
            benchmark_port = args.bp
        #else:
        #    print("Wrong syntax detected. Running the script with default parameters...")

    # Building mitmproxy_mode string on the fly to made it simple to modify.
    mitmproxy_mode = 'reverse' + ':' + benchmark_protocol + str(benchmark_host) + ':' + str(benchmark_port)

    # Options to set up Mitmproxy as reverse proxy to Tomcat (default port 8080)
    options = Options(listen_host=proxy_host, listen_port=int(proxy_port), http2=True, mode=mitmproxy_mode)
    # DumpMaster instance: "with_termlog" option set to true to see logs on terminal.
    m = DumpMaster(options, with_termlog=True, with_dumper=False)
    config = ProxyConfig(options)
    m.server = ProxyServer(config)
    # Add an HTTPInterceptor instance as an addon for mitmproxy.
    m.addons.add(http_logger_addon)

    try:
        print('Interceptor is now listening...')
        m.run()
    except KeyboardInterrupt:
        print('KeyboardInterrupt received, shutting down mitmproxy.')
        m.shutdown()
        print('mitmproxy has been shutted down.')