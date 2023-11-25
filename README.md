# CGAV (Certificates Generation and Verification)

CGAV is a simple and light weight bulk certificate generation system.
It also provides a API for certificate verification. The systems is
designed with the following principles in mind: 

1. It has a minimal number of types of users (minimal privilege
    management).
2. Provide adapters with full certificate design management.
    - a. Users can add new certificate background. 
    - b. USers can manage how the certificate text would appear (e.g.,
        font type, size, alignment, etc).
    - c. Users can define multiple variables within the certificate
        (e.g., recipient name, recipient ranking, etc).
    - d. Users can define 1-3 certificates signers and their details
        (name, position, signature).
3. Define as many event types as users need (e.g., training course,
    award, etc).
4. Publish and unpublish certificates based on a created event.
5. Tag each generated certificate with a unique and short hash. 
5. Provide anonymous user with an API to verify the authenticity of
    a certificate. 


This project is developed and maintained by the College of Computer
at Qassim University. The list of contributors can be found in the
git history. 

# Getting Started

## Build and Run

The project is containerized using Docker and Docker Compose.
We explain how to build it and deploy it within the context of
compose. If you wish to build it from scratch we recommend you
look at the build recipe from `Dockerfile` to build it manually. 

### `.env` file:

Before you start you must provide a `.env` file that conform to
the following keys and structure.

```ini
# configurations used by the docker compose file

# web configurations
WEB_PORT=5000

# db configurations
DB_PORT=3306
INIT_FILE=./resources (or where you keep the .sql build script)
HOSTNAME=test
MYSQL_DATABASE=root
MYSQL_ROOT_PASSWORD=changeme
MYSQL_USER=dbuser
MYSQL_PASSWORD=changeme
SCHEMA=schema_name
```

```ini
# Mail Server Configuration for Gmail
MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME='your_mail@gmail.com'
MAIL_PASSWORD='your_mail_app_pass'
MAIL_DEFAULT_SENDER='your_mail@gmail.com'
```

**Note:**
If you need guidance on generating an App Password, please refer to the [README.md]() for step-by-step instructions.


### Build and Run the System: 

If you have the correct `.env` file, then all you need is to run    
```shell
docker-compose up -d
```
This will start the development server, and you can access the
web page in your browser at
[http://localhost:{your-prot}](http://localhost:{yourport}).

### Stop and Delete the Instants:

To stop the system and remove the instant completely, you would
pass the `down` option to docker compose.

```shell
docker-compose down
```

## Helpers 

If your would like to access the `web` container,
you can use a command similar to the ones below
depending on your system.

- Unix based systems:
  ```shell
  docker exec -it <your_container_name> /bin/bash
  ```
- Windows:
  ```shell
  docker exec -it <your_container_name> sh
  ```

~~## Usage~~

~~The system can be used manually by running the `main.py` file.~~ 
~~By default, the project uses the~~
~~[sample-event.yaml](src/events/sample-event.yaml) for the event details~~
~~which in turn uses the [sample-data.csv](src/data/sample-data.csv) to~~
~~get recipient information. You can change these settings by providing~~
~~a new event file (yaml file) and use the `-e` flag with main.~~ 

~~The following is a sample command for generating sample certificates:~~ 
```shell
cd src
python3 main.py
```

~~By default, all output will be saved under `src/output`.~~

# Sample Output

TBA

# Resources

TBA



