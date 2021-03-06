import os
from time import sleep

from data import calculate_features
from joblib import load
from utils import create_model

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


# Import user parameters from config file
import config

config_dict = config.__dict__  # Parameters for feature extraction
photo_dir = "images"

print("Waiting to classify textures...")
script_dir = os.path.split(os.path.realpath(__file__))[0]
while not os.path.exists(os.path.join(script_dir, photo_dir, "matlab_flag")):
    sleep(0.1)
print("Textures have been received.")

X, names, feature_names = calculate_features(os.path.join(script_dir, photo_dir), **config_dict)

# Data pre-processing as done during training
scaler = load(os.path.join(script_dir, "data_scaler.joblib"))
X = scaler.transform(X)

# Select the best features used for training
best_feats = load(os.path.join(script_dir, "best_features.joblib"))
X = X[:, best_feats]

### Load classifier
enc = load(os.path.join(script_dir, "class_encoder.joblib"))
class_names = enc.categories_[0]
clf = create_model(input_size=X.shape[-1], output_size=len(class_names))
clf.load_weights(os.path.join(script_dir, "weights.hdf5"))

preds = clf.predict(X)
all_outputs = ["file," + ",".join(class_names.tolist())]

for i, pred in enumerate(preds):
    output = []
    for option in range(pred.shape[-1]):
        output.append("{:.2f}".format(pred[option]))
    output = "%s,%s" % (names[i, 0], ",".join(output))
    all_outputs.append(output)

with open(os.path.join(script_dir, photo_dir, "outputs.csv"), "w+") as f:
    f.write("\n".join(all_outputs))

with open(os.path.join(script_dir, photo_dir, "python_flag"), "w+") as f:
    f.write("")
print("Textures have been classified.")
