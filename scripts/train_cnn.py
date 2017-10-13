
from rmgpy.cnn_framework.predictor import Predictor
import os
import rmgpy
import logging
from rmgpy.rmg.main import initializeLog

level = logging.INFO
initializeLog(level, os.path.join('train_cnn_results', 'train0.log'))

h298_predictor = Predictor()

predictor_input = os.path.join('train_cnn_inputs', 'predictor_input.py')

h298_predictor.load_input(predictor_input)

lr_func = "float(0.0007 * np.exp(- epoch / 30.0))"
h298_predictor.kfcv_train(folds=5, lr_func=lr_func)