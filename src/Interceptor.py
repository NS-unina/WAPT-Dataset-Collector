# Author: Marco Urbano.
# Date: 8 January 2021.
# Description: this is a simple Python script that uses mitmproxy to record http request/responses.
# Notes:
#           To run mitmproxy directly from Python:
#           - https://stackoverflow.com/questions/51893788/using-mitmproxy-inside-python-script


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

if __name__ == "__main__":
    ################### START MITMPROXY AND BENCHMARK DEFAULT SETTINGS VARIABLES ###################
    # The following default values are intended to be used if the script is gonna be executed on the
    # same machine that runs the benchmark server.

    # Variables to identify ports and addresses of mitmproxy and the benchmark http server.
    proxy_port = 8888
    proxy_host = '127.0.0.1'
    benchmark_port = 8080
    benchmark_host = '127.0.0.1'

    ################### END MITMPROXY AND BENCHMARK DEFAULT SETTINGS VARIABLES #####################

    # Reading command line arguments (if there any)
    cmd_arg = len(sys.argv)
    if cmd_arg > 1:
        # If the syntax is correct, change default variable values to custom ones.
        if utilities.check_arguments(sys.argv):
            proxy_host = sys.argv[2]
            proxy_port = sys.argv[4]
            benchmark_host = sys.argv[6]
            benchmark_port = sys.argv[8]
        else:
            print("Wrong syntax detected. Running the script with default parameters...")

    # Building mitmproxy_mode string on the fly to made it simple to modify.
    mitmproxy_mode = 'reverse' + ':' + 'http://' + str(benchmark_host) + ':' + str(benchmark_port)

    # Options to set up Mitmproxy as reverse proxy to Tomcat (default port 8080)
    options = Options(listen_host=proxy_host, listen_port=int(proxy_port), http2=True, mode=mitmproxy_mode)
    # DumpMaster instance: "with_termlog" option set to true to see logs on terminal.
    m = DumpMaster(options, with_termlog=True, with_dumper=False)
    config = ProxyConfig(options)
    m.server = ProxyServer(config)
    # Add an HTTPInterceptor instance as an addon for mitmproxy.
    m.addons.add(HTTPLogger())

    try:
        print('Interceptor is now listening...')
        m.run()
    except KeyboardInterrupt:
        print('KeyboardInterrupt received, shutting down mitmproxy.')
        m.shutdown()
        print('mitmproxy has been shutted down.')