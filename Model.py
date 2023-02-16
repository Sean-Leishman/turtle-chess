import tensorflow as tf
import numpy as np

class Model():
    def __init__(self):
        self.model = tf.keras.models.load_model("./model")

    def predict_scores(self, boards):
        scores = self.model.predict(boards)
        return scores