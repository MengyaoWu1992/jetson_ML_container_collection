from tensorflow import keras
import numpy as np

from flask import Flask, send_file,render_template, request
app = Flask(__name__)
wsgi_app = app.wsgi_app

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
    return send_file(
        'uploads/merged_model.h5',
        mimetype=None,
        attachment_filename='merged_model.h5',
        as_attachment=True,
        cache_timeout=-1
    )


@app.route('/upload', methods = ["GET","POST"])
def file_upload():
    if request.method=="POST":
        files = request.files.getlist('data_input_folder[]')
        print(type(files))
        for file in files:
            print(file)
            file.save(os.path.join("uploads/data", file.filename.split('/')[-1]))
        files = request.files.getlist('model_input_folder[]')
        print(type(files))
        for file in files:
            print(file)
            model_path = os.path.join("uploads/model", file.filename.split('/')[-1])
            file.save(model_path)
            parts.append(model_path)
        training()
        return '''
            <html>
                <a href="http://127.0.0.1:5000/">Download File</a><br>
                <a href="/file"><button>Download</button></a>
            </html>
            '''
    else:
        return render_template("index.html", message="Upload")
                                                                                                                      
def training():
    models = []
    global parts
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
    new_model.save('uploads/merged_model.h5')
    print('new model merged at uploads/merged_model.h5')
    parts = []

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port = '5000')
