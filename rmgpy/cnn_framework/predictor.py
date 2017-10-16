
from cnn_model import build_model
from .input import read_input_file
from .molecule_tensor import get_molecule_tensor
import os
import rmgpy

class Predictor(object):

	def __init__(self, input_file=None):

		self.model = None
		if input_file:
			self.input_file = input_file
		else:
			self.input_file = os.path.join(os.path.dirname(rmgpy.__file__),
										'cnn_framework',
										'test_data', 
										'minimal_predictor', 
										'predictor_input.py'
										)

	def build_model(self):
		"""
		This method is intended to provide a way to build default model 
		"""

		self.model = build_model()

	def load_input(self, path=None):
		"""
		This method is intended to provide a way to build model from an input file
		"""
		
		if path is None: 
			path = self.input_file
			print path
		read_input_file(path, self)

	def train(self):

		pass

	def load_parameters(self, param_path):

		self.model.load_weights(param_path)

	def save_parameters(self):

		pass

	def predict_on_batch(self, molecules):

		molecule_tensors = []
		for molecule in molecules:
			molecule_tensor = get_molecule_tensor(molecule)
			molecule_tensors.append(molecule_tensor)

		molecule_tensor_array = np.array(molecule_tensors)
		return self.model.predict_on_batch(molecule_tensor_array)
    
