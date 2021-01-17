# WAPT-Dataset-Collector

A software with the aim to record Penetration Testing sessions and to produce a 
dataset composed of various kind of data (http requests, screen recording, etc).

## Installation
So far the only library that is not included into the Python language and that is employed in this project is 
[mitmproxy](https://mitmproxy.org). 
mitmproxy libraries can be installed directly with the package manager [pip](https://pip.pypa.io/en/stable/) 

```bash
sudo pip3 install mitmproxy
```

## Usage
The script can be used with or without options. If there is the need to specify a custom set of 
options the user will be enforced to specify all the parameters that are needed to use mitmproxy
as reverse proxy. The syntax to run the script with custom options is the following
```bash
python3 Interceptor.py -ph 'proxy_host' -pp 'proxy_port' -bh 'benchmark_host' -bp 'benchmark_port' 

# The default options are the following:
python3 Interceptor.py -ph '127.0.0.1' -pp '8888' -bh '127.0.0.1' -bp '8080'
```

## Contributing

## License
[MIT](https://choosealicense.com/licenses/mit/)