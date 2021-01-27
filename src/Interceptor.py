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
# Used to handle the command line arguments. (utility is a file of this project, not a Python official library)
import utilities

# Importing the custom addon used to save http requests/responses as JSON.
from HTTPLogger import *

# Using requests in order to obtain the JSON string describing the network built by host's Docker compose.
# The request will only be possible if the host's docker socket is shared with the container that
# runs this script.
import socket

# regular expressions will be used to obtain the name of every service that will be in execution on the
# network.
import re

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

    # httplogger_addon is the instance of HTTPLogger class employed to describe the addon that performs the
    # interception. If this script will be executed in container mode, this object will be replaced by one
    # instance that contains also the dictionary with the info about other containers on the same net.
    http_logger_addon = HTTPLogger()
    ################### END MITMPROXY AND BENCHMARK DEFAULT SETTINGS VARIABLES #####################

    # Reading command line arguments (if there any)
    cmd_arg = len(sys.argv)
    if cmd_arg > 1:
        # If this script will be executed as Docker container it will do a Docker inspect query to
        # discover the other hosts (e.g. benchmark or/and any other container that will send it
        # requests)
        if sys.argv[1] == '--mode' and sys.argv[2] == 'container':
            # Containers is a dictionary with key=name, value=IP
            containers = {}

            # Extracting services/container name from docker-compose.yml
            # The regex used to find these names is /container_name: .*/
            # The pharenteses are used to delimit a group.
            with open('docker-compose.yml') as docker_compose:
                for line in docker_compose.readlines():
                    if re.search(r'container_name: (.*)', line):
                        # After that the regex has been found, insert this as key and assign as value
                        # the IP Address discovered through the DNS.
                        service_name = re.search(r'container_name: (.*)', line).group(1)
                        containers[str(service_name)] = str(socket.gethostbyname(service_name))

            # checking that the docker-compose.yml is well formed and defines a container named "benchmark".
            try:
                benchmark_host = containers['benchmark']
            except KeyError as keyerror:
                print("docker-compose.yml doesn't define any container named 'benchmark'! Define it and retry!\n")
                raise keyerror
            # checking that the docker-compose.yml is well formed and defines a container named "interceptor".
            try:
                proxy_host = containers['interceptor']
            except KeyError as keyerror:
                print("docker-compose.yml doesn't define any container named 'interceptor'! Define it and retry!\n")
                raise keyerror

            # replace the default variable with the one that contains info about the network of containers.
            http_logger_addon = HTTPLogger(containers)


        # If the syntax is correct, change default variable values to custom ones.
        elif utilities.check_arguments(sys.argv):
            proxy_host = sys.argv[2]
            proxy_port = sys.argv[4]
            benchmark_host = sys.argv[6]
            benchmark_port = sys.argv[8]
        else:
            print("Wrong syntax detected. Running the script with default parameters...")

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