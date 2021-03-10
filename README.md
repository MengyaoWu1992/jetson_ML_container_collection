# jetson_ML_container_collection
flask with ML training, model merge, transfer learning functions inside container

git clone https://github.com/MengyaoWuNotAvailable/jetson_ML_container_collection.git

cd jetson_ML_container_collection/

Repo structure

        ├── combine
        │   └── build
        │       ├── Dockerfile
        │       ├── templates
        │       │   └── index.html
        │       └── upload_download.py
        ├── README.md
        └── train
            └── build
                ├── Dockerfile
                ├── templates
                │   └── index.html
                └── train_download.py

        6 directories, 7 files

Inside the train/build, train_download.py and folder templates should be boundled together
You need to install library used inside train_download.py

run: python3 train_download.py

you will get following console output

        2021-03-09 19:06:21.568330: I tensorflow/stream_executor/platform/default/dso_loader.cc:49] Successfully opened dynamic library libcudart.so.10.2
        * Serving Flask app "train_download" (lazy loading)
        * Environment: production
         WARNING: This is a development server. Do not use it in a production deployment.
         Use a production WSGI server instead.
        * Debug mode: off
        * Running on all addresses.
         WARNING: This is a development server. Do not use it in a production deployment.
        * Running on http://192.168.0.129:5000/ (Press CTRL+C to quit)

Follow the console print "http://192.168.0.129:5000/", but you cannot directly use this link, refer to file train_download.py
Inside the code, locate "@app.route('/upload', methods = ["GET","POST"])", we need to append "/upload" to the address so invoke the function def file_upload()
the gives you the address  http://192.168.0.129:5000/upload
 
 
 For container, first build the docker image, check the Dockerfile in build directory, docker build command follows the steps specific in Dockerfile
 
 sudo docker build build -t train_demo --network=host
 
 you will see console print below, it shows the steps specificed in the Dockerfile
 
       Step 1/13 : FROM nvcr.io/nvidia/l4t-tensorflow:r32.5.0-tf2.3-py3
       ---> 96818a623ae3
      Step 2/13 : ENV GO111MODULE=on
       ---> Using cache
       ---> 17d29572f6f6
      Step 3/13 : WORKDIR /app
       ---> Using cache
       ---> c2b1430c6796
      Step 4/13 : COPY train_download.py /app
      ...........
in the build command, -t stands for tag, that is your docker image name, first "build" is the command, second "build" (can be named in anyway) is the directory that contains everything you need to build docker image. Dockerfile has to be named this way.


Now check the image built

sudo docker images

        REPOSITORY                      TAG                 IMAGE ID            CREATED             SIZE
        train_demo                      latest              4f052926059e        4 minutes ago       2.11GB


You can see the name "train_demo" for the image we just built.

now you can run the docker image, once it is running, it is called container (a running instance of a docker image)
You can run it 2 modes, attached and detached. Attached mode will give you shell terminal of the container. Detached will make the container run in the background.

 Attached to container shell command
 sudo docker run -p 5000:5000 -it train_demo /bin/bash
 
 detached mode
 sudo docker run -p 5000:5000 -d train_demo
 
 prints a id like 0114d0e664d36af6a6ab43ab323abfbe36d3bc69274d954cd69286064da214ec
 
 Check the running container
 sudo docker container ls
 
     CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
    0114d0e664d3        train_demo          "/bin/sh -c 'python3…"   43 seconds ago      Up 42 seconds       0.0.0.0:5000->5000/tcp   funny_grothendieck
 
 to check logs (console print inside container)
 sudo docker logs 0114d0e664d3
 



