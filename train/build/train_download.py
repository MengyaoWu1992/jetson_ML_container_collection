import csv
import matplotlib.image as mpimg
import numpy as np
import os
import shutil

from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Flatten, Dense, Lambda, Conv2D, Cropping2D, Dropout

from tensorflow import keras

from flask import Flask, send_file,render_template, request
app = Flask(__name__)
wsgi_app = app.wsgi_app

parts = []
download_model_name = ""
transfer_learning = False
data_exist = False
base_model_exist = False
model_combine = False

def createPreProcessingLayers():
    """
    Creates a model with the initial pre-processing layers.
    """
    model = Sequential()
    # /255 for normalization, -0.5 is to move the mean to 0
    model.add(Lambda(lambda x: (x / 255.0) - 0.5, input_shape=(160,320,3)))
    model.add(Cropping2D(cropping=((50,20), (0,0))))
    return model

def nVidiaModel():
    # Model shown in the course video, I copied it here
    model = createPreProcessingLayers()
    model.add(Conv2D(24,5,2, activation='relu'))
    model.add(Conv2D(36,5,2, activation='relu'))
    model.add(Conv2D(48,5,2, activation='relu'))
    model.add(Conv2D(64,3, activation='relu'))
    model.add(Conv2D(64,3, activation='relu'))
    model.add(Flatten())
    model.add(Dropout(0.2))
    model.add(Dense(100))
    model.add(Dropout(0.2))
    model.add(Dense(50))
    model.add(Dropout(0.2))
    model.add(Dense(10))
    model.add(Dense(1))
    return model



def training():

    global download_model_name
    images = []
    steerings = []
    #Open CSV file
    lines = []
    with open('uploads/data/driving_log.csv') as csvFile:
        reader = csv.reader(csvFile)
        for line in reader:
            lines.append(line)

    #lines extracted includes the header in the csv file, remove it
    lines = lines[1:]
    #adjust labelling angle for left/right camera image
    correction = 0.18

    for line in lines:

        steering = float(line[3])

        # Loop through center, left, right images in one line of record
        for index in range(3):
            imgPath = line[index]
            #could be data recorded from Windows PC
            if '\\' in imgPath:
                imgName = imgPath.split('\\')[-1]
            else:
                imgName = imgPath.split('/')[-1]

            imgNewPath = 'uploads/data/' + imgName
            print(imgNewPath)

            image = mpimg.imread(imgNewPath)

            images.append(image)

            if index == 0:#for center image
                steerings.append(steering)
            elif index == 1:#for left image
                steerings.append(steering + correction)
            elif index == 2:#for right image
                steerings.append(steering - correction)
            else:
                raise("index out of range for iterating center,left,right images")

    X_train = np.array(images)
    Y_train = np.array(steerings)
    # Call function to create neutral network
    if transfer_learning:
        global parts
        model = keras.models.load_model(parts[0])
        parts = []
        download_model_name = 'retrained_model.h5'
    else:
        model = nVidiaModel()
        download_model_name = 'trained_model.h5'
    # loss chosen to be mse for a simple regression network (cross-entropy is for classification network)
    model.compile(loss='mse',optimizer='adam')
    history_object = model.fit(X_train,Y_train,validation_split=0.1,shuffle=True,epochs=3)
    # Save the trained model with specified name
    model.save('uploads/'+download_model_name)
    print("model " + download_model_name + " saved\n")

def model_merge():
    
    models = []
    global parts
    global download_model_name

    for part in parts:
        print('loading model at:' + part)
        models.append(keras.models.load_model(part))


    weights = [model.get_weights() for model in models]

    new_weights = list()
    for weights_list_tuple in zip(*weights):
        new_weights.append(
            np.array([np.array(w).mean(axis=0) for w in zip(*weights_list_tuple)])
        )

    new_model = models[0]
    new_model.set_weights(new_weights)
    download_model_name = 'merged_model.h5'
    new_model.save('uploads/'+download_model_name)
    print('new model merged at uploads/'+download_model_name )
    parts = []

@app.route('/download')
def file_downloads():
    return '''
        <html>
            <a href="http://127.0.0.1:5000/">Home</a><br>
            <a href="/file"><button>Download</button></a>
        </html>
        '''

@app.route('/file')
def return_files():

    global download_model_name

    return send_file(
        'uploads/' + download_model_name,
        mimetype=None,
        attachment_filename=download_model_name,
        as_attachment=True,
        cache_timeout=-1
    )


@app.route('/upload', methods = ["GET","POST"])
def file_upload():
    if request.method=="POST":

        global data_exist
        data_exist = False

        global base_model_exist
        base_model_exist = False

        global model_combine
        model_combine = False

        global parts
        parts = []

        shutil.rmtree("uploads/data")
        os.mkdir("uploads/data")
        shutil.rmtree("uploads/model")
        os.mkdir("uploads/model")

        files = request.files.getlist('data_input_folder[]')
        print(files)

        fileCounter = 0
        for file in files:
            print(file)
            fileName = file.filename.split('/')[-1]
            if fileName == "":
                continue
            file.save(os.path.join("uploads/data", fileName))
            fileCounter = fileCounter + 1

        if fileCounter >= 2:
            data_exist = True

        files = request.files.getlist('model_input_folder[]')




        fileCounter = 0
        for file in files:
            print(file)
            fileName = file.filename.split('/')[-1]
            if fileName == "": 
                continue
            model_path = os.path.join("uploads/model", fileName)
            file.save(model_path)
            parts.append(model_path)
            fileCounter = fileCounter + 1

        if fileCounter == 1:
            base_model_exist = True
        elif fileCounter > 1:
            model_combine = True


        global transfer_learning

        if data_exist and base_model_exist:
            transfer_learning = True
            training()
        elif model_combine:
            model_merge()
        elif data_exist:
            transfer_learning = False
            training()
        else:
            return render_template("index.html", message="Upload")

        return '''
            <html>
                <a href="http://127.0.0.1:5000/">Download File</a><br>
                <a href="/file"><button>Download</button></a>
            </html>
            '''
    else:
        return render_template("index.html", message="Upload")




if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port = '5000')
