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

## Install

The project is containerized using Docker. We explain how to build
it and and deploy it within the context of the Docker container. If
you wish to build it from scratch we recommend you look at the build
recipe from `Dockerfile` to satisfy all the dependencies. 

- Build an image of the system: 
    ```shell
    docker build -t cgav:latest .
    ```
- Run an instance of the system given the image we just built:
    ```shell
    docker run --name new_cgav -it cgav:latest /bin/bash
    ```

## Usage

The system can be used manually by running the `main.py` file. 
By default the project uses the
[sample-event.yaml](src/events/sample-event.yaml) for the event details
which in turn uses the [sample-data.csv](src/data/sample-data.csv) to
get recipient information. You can change these settings by providing
a new event file (yaml file) and use the `-e` flag with main. 

The following is a sample command for generating sample certificates: 
```shell
cd src
python3 main.py
```

By default all output will be saved under `src/output`.

## Running the Web Page

To run the web page, follow these steps:

1. Build the Docker image :
    ```shell
    docker build -t cgav:latest .
    ```

2. Run an instance of the system with port mapping:
    ```shell
    docker run --name new_cgav -p 5000:5000 -it cgav:latest /bin/bash

    for windows 
    
    docker run --name new_cgav -p 5000:5000 -it cgav:latest sh 
    ```

3. Navigate to the `flask-website` directory:
    ```shell
    cd flask-website
    ```

4. Run the Flask web application:
    ```shell
    python app.py
    ```

This will start the development server, and you can access the web page in your browser at [http://localhost:5080](http://localhost:5080).


## Running the login Page

To run the web page, follow these steps:

1. Build the Docker image :
    ```shell
    docker build -t cgav:latest .
    ```

2. Run an instance of the system with port mapping:
    ```shell
    docker run --name new_cgav -p 5000:5000 -it cgav:latest /bin/bash

    for windows 
    
    docker run --name new_cgav -p 5000:5000 -it cgav:latest sh 
    ```

3. Navigate to the `flask-login` directory:
    ```shell
    cd flask-login
    ```

4. Run the Flask web application:
    ```shell
    python app.py
    ```

This will start the development server, and you can access the web page in your browser at [http://localhost:5000](http://localhost:5000).

# Sample Output

TBA

# Resources

TBA



