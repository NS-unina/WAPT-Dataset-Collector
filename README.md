# WAPT-Dataset-Collector

A software with the aim to record Penetration Testing sessions and to produce a 
dataset composed of various kind of data (http requests, screen recording, etc).

## Installation
The only requirement to execute this script is to have a properly functioning installation of the following: 
- [docker](https://docs.docker.com/get-docker/) 
- [python](https://www.python.org/downloads/)

Every container provides to the installation of their required libraries,
for example the Interceptor, the one that records all the http request/responses, reads 
[depencencies](https://github.com/NS-unina/WAPT-Dataset-Collector/blob/main/Docker/interceptor/dependencies) file.

## Usage
To start the recording on your favourite vulnerable web application you only need to execute
```bash
docker-compose up
```
in the main folder of the downloaded zip file.
It is recommended to execute 
```bash
docker-compose down
```
after the usage.

The docker-compose.yml file contains the definition of the network that will be raised up by docker.
The default network will be built using a custom version of [wavsep](http://sectooladdict.blogspot.com/2017/11/wavsep-2017-evaluating-dast-against.html) 
as the 'benchmark' container (so the one that will be used as vulnerable web application to attack): obviously you
can use your own vulnerable web app. 
## Contributing
Marco Urbano, [marcourbano.me](marcourbano.me)
## License
[MIT](https://choosealicense.com/licenses/mit/)