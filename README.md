# ServiceX-DID-finder

For a given RUCIO DID and client site finds optimal access paths.

Docker image is autobuilt here: https://cloud.docker.com/u/sslhep/repository/docker/sslhep/servicex-did-finder

output consist of:
* file in /data/request_name/did-finder/status.log
* if request successful paths to files will be listed in /data/request_name/did-finder/paths.json

To run it: 

``` docker run -it -d --name=did-finder sslhep/servicex-did-finder ```

After the container is started you can attach to it and start using the rucio commands:

``` docker exec -it did-finder /bin/bash rucio ping ```

An example command to run:

``` docker exec -it did-finder /bin/bash ./run.sh request_name mc15_13TeV:xAOD.root```


## NOTE
* make python code that checks es for entries to process, looks up rucio data and fills back rucio info.
* needs a config: elasticsearch instance, site where it runs, xcache to use to get data.