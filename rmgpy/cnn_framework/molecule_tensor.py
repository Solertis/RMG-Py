
import numpy as np

def get_molecule_tensor(molecule):

	"""
	this method takes RMG `Molecule` object and vectorize 
	it into a numpy molecule tensor with dimension: 
	non_H_atom_num * non_H_atom_num * attribute_num
	"""
	non_H_atoms = [atom0 for atom0 in molecule.atoms if not atom0.isHydrogen()]
	non_H_atom_num = len(non_H_atoms)
	
	atom_attributes_dict = get_atom_attributes(molecule, non_H_atoms)
	bond_attributes_dict = get_bond_attributes(molecule, non_H_atoms)

	atom_attribute_num = len(atom_attributes_dict.values()[0])
	bond_attribute_num = len(bond_attributes_dict.values()[0])
	attribute_num = atom_attribute_num + bond_attribute_num
	molecule_tensor = np.zeros((non_H_atom_num, non_H_atom_num, attribute_num))

	
	for i, atom in enumerate(non_H_atoms):
		molecule_tensor[i, i, :] = np.concatenate((atom_attributes_dict[atom], np.zeros_like(bond_attributes_dict.values()[0])))
		for bonded_atom, bond in atom.bonds.iteritems():
			if bonded_atom in non_H_atoms:
				j = non_H_atoms.index(bonded_atom)
				molecule_tensor[i, j, :] = np.concatenate((atom_attributes_dict[bonded_atom], bond_attributes_dict[bond]))

	return molecule_tensor

def get_atom_attributes(molecule, non_H_atoms):

	"""
	this method takes a molecule with hydrogen pre-removed and returns a dict
	with non-H atom as key, atom attributes as value
	"""
	
	atom_attributes_dict = {}
	for atom in non_H_atoms:

		attributes = oneHotVector(
			atom.element.number, 
			[5, 6, 7, 8, 9, 15, 16, 17, 35, 53, 999]
		)

		non_H_neighbors = [atom0 for atom0 in atom.bonds if not atom0.isHydrogen()]
		attributes += oneHotVector(
			len(non_H_neighbors),
			[0, 1, 2, 3, 4, 5]
		)
		# Add hydrogen count
		H_neighbors = [atom0 for atom0 in atom.bonds if atom0.isHydrogen()]
		attributes += oneHotVector(
			len(H_neighbors),
			[0, 1, 2, 3, 4]
		)
		# charge
		atom.updateCharge()
		attributes.append(atom.charge)
		
		#in ring
		attributes.append(molecule.isVertexInCycle(atom))
		
		# Add boolean if aromatic atom
		is_aromatic = False
		for bonded_atom, bond in atom.bonds.iteritems():
			if bond.isBenzene():
				is_aromatic = True
				break
		attributes.append(is_aromatic)

		atom_attributes_dict[atom] = np.array(attributes, dtype=np.float32)
	
	return atom_attributes_dict

def get_bond_attributes(molecule, non_H_atoms):
	"""
	this method takes a molecule with hydrogen pre-removed and returns a dict
	with bond as key, bond attributes as value
	"""
	bond_attributes_dict = {}
	for atom in non_H_atoms:
		for bonded_atom, bond in atom.bonds.iteritems():
			if not bonded_atom.isHydrogen() and (bond not in bond_attributes_dict):
				attributes = oneHotVector(bond.order,
										['S', 'B', 'D', 'T']
										)
				# Add if is aromatic
				attributes.append(bond.isBenzene())

				attributes.append(is_bond_conjugated(bond))
				
				attributes.append(molecule.__isChainInCycle([bond.atom1, bond.atom2]))

				# add if connected
				attributes.append(1)

				bond_attributes_dict[bond] = np.array(attributes, dtype=np.float32)

	if not bond_attributes_dict:
		bond_attributes_dict['no_bond'] = np.array([0]*8, dtype=np.float32)
	
	return bond_attributes_dict

def is_bond_conjugated(bond):
	
	atom1 = bond.atom1
	atom2 = bond.atom2
	if bond.order == 'S':
		atom1_has_non_single_bond = False
		atom2_has_non_single_bond = False
		for bonded_atom, bond in atom1.bonds.iteritems():
			if bond.order != "S":
				atom1_has_non_single_bond = True
				break
		for bonded_atom, bond in atom2.bonds.iteritems():
			if bond.order != "S":
				atom2_has_non_single_bond = True
				break

		return (atom1_has_non_single_bond and atom2_has_non_single_bond)

	elif bond.order == 'B':
		return True
	else:
		for atom3, bond23 in atom2.bonds.iteritems():
			if bond23.order == "S":
				for atom4, bond34 in atom3.bonds.iteritems():
					if bond34.order != "S":
						return True

		for atom3, bond13 in atom1.bonds.iteritems():
			if bond13.order == "S":
				for atom4, bond34 in atom3.bonds.iteritems():
					if bond34.order != "S":
						return True

		return False

def oneHotVector(val, lst):
	'''Converts a value to a one-hot vector based on options in lst'''
	if val not in lst:
		val = lst[-1]
	return map(lambda x: x == val, lst)