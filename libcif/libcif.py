#!/usr/bin/python2
# -*- coding: latin1 -*-
#this is a library with modules for reading, writing and transforming CIF files
# Written by Jerome Kieffer Email: jerome.kieffer at terre-adelie.org or jerome.kieffer at terre-adelie.org
#
# Needs a functionnal version of platon, convert (imageMagic) and mozilla to generate reports

#!/usr/nekoware/bin/python
#!/disk1/cambridge/c_sgiv6/bin/python2.2

import os.path, sys, re,time, os,string



#at  the moment, the symmetries are not yet complete. please send me the modifications by Email

Symmetries={"x,y,z": ['Triclinic', 'P 1'],
	"x,y,z;-x,-y,-z": ['Triclinic', 'P -1'],
	"x,y,z;-x,y+1/2,-z": ['Monoclinic', 'P 21'],
	"x,y,z;-x,y+1/2,-z+1/2;-x,-y,-z;x,-y+1/2,z+1/2": ['Monoclinic', 'P 21/c'],
	"x,y,z;-x,y+1/2,-z+1/2;-x,-y,-z;x,-y-1/2,z-1/2": ['Monoclinic', 'P 21/c'],
	"x,y,z;-x+1/2,y+1/2,-z+1/2;-x,-y,-z;x-1/2,-y-1/2,z-1/2": ['Monoclinic', 'P 21/n'],
	"x,y,z;x+1/2,-y+1/2,z+1/2;-x,-y,-z;-x-1/2,y-1/2,-z-1/2": ['Monoclinic', 'P 21/n'],
	"x,y,z;-x+1/2,y+1/2,-z;-x,-y,-z;x-1/2,-y-1/2,z": ['Monoclinic', 'P 21/a'],
	"x,y,z;-x,y,-z+1/2;x+1/2,y+1/2,z;-x+1/2,y+1/2,-z+1/2;-x,-y,-z;x,-y,z+1/2;-x+1/2,-y+1/2,-z;x+1/2,-y+1/2,z+1/2": ['Monoclinic', 'C 2/c'],
	"x,y,z;-x,y,-z+1/2;x+1/2,y+1/2,z;-x+1/2,y+1/2,-z+1/2;-x,-y,-z;x,-y,z-1/2;-x+1/2,-y+1/2,-z;x+1/2,-y+1/2,z-1/2": ['Monoclinic', 'C 2/c'],
	"x,y,z;-x,y,-z;x+1/2,y+1/2,z;-x+1/2,y+1/2,-z": ['Monoclinic', 'C 2'],
	"x,y,z;x,-y,z+1/2": ['Monoclinic', 'P c'],
	"x,y,z;-x,y,-z;x+1/2,y+1/2,z+1/2;-x+1/2,y+1/2,-z+1/2": ['Monoclinic', 'I 2'],
	"x,y,z;-x+1/2,-y,z+1/2;-x,y+1/2,-z+1/2;x+1/2,-y+1/2,-z": ['Orthorhombic', 'P 21 21 21'],
	"x,y,z;-x+1/2,-y,z+1/2;x+1/2,-y+1/2,-z;-x,y+1/2,-z+1/2": ['Orthorhombic', 'P 21 21 21'],
	"x,y,z;-x,-y,z;-x+1/2,y+1/2,-z;x+1/2,-y+1/2,-z": ['Orthorhombic', 'P 21 21 21'],
	"x,y,z;x+1/2,-y+1/2,-z;-x,y+1/2,-z+1/2;-x+1/2,-y,z+1/2":['Orthorhombic', 'P 21 21 21'],
	"x,y,z;-x,-y,z+1/2;-x+1/2,y+1/2,z+1/2;x+1/2,-y+1/2,z": ['Orthorhombic', 'P n a 21'],
	"x,y,z;-x,-y,z+1/2;x+1/2,-y+1/2,z;-x+1/2,y+1/2,z+1/2": ['Orthorhombic', 'P n a 21'],
	"x,y,z;-x,-y,z+1/2;x+1/2,-y,z;-x+1/2,y,z+1/2": ['Orthorhombic', 'P c a 21'],
	"x,y,z;x+1/2,-y,-z;x,-y+1/2,z+1/2;x+1/2,y+1/2,-z+1/2": ['Orthorhombic', 'P 21 c n'],
	"x,y,z;x+1/2,-y,-z;x,y+1/2,-z+1/2;x+1/2,-y+1/2,z+1/2": ['Orthorhombic', 'P 21 n b'],
	"x,y,z;-x+1/2,-y,z+1/2;-x,y+1/2,-z+1/2;x+1/2,-y+1/2,-z;-x,-y,-z;x+1/2,y,-z+1/2;x,-y+1/2,z+1/2;-x+1/2,y+1/2,z": ['Orthorhombic', 'P b c a'],
	"x,y,z;-x+1/2,-y,z+1/2;-x,y+1/2,-z+1/2;x+1/2,-y+1/2,-z;-x,-y,-z;x-1/2,y,-z-1/2;x,-y-1/2,z-1/2;-x-1/2,y-1/2,z": ['Orthorhombic', 'P b c a'],
	"x,y,z;x,-y,-z;x,-y+1/2,z+1/2;x,y+1/2,-z+1/2;x+1/2,y+1/2,z;x+1/2,-y+1/2,-z;x+1/2,-y,z+1/2;x+1/2,y,-z+1/2": ['Orthorhombic', 'C 2 c b'],
	"x,y,z;-y,x-y,z+1/3;-x+y,-x,z+2/3": ['Trigonal', 'P 31'],
	"x,y,z;-x,-y,z+1/2;-y,x,z+1/4;y,-x,z+3/4": ['Tetragonal', 'P 43'],
	"x,y,z;-x+1/2,-y,z+1/2;-y+3/4,x+1/4,z+1/4;y+3/4,-x+3/4,z+3/4;x+1/2,y+1/2,z+1/2;-x+1,-y+1/2,z+1;-y+5/4,x+3/4,z+3/4;y+5/4,-x+5/4,z+5/4;-x,-y,-z;x-1/2,y,-z-1/2;y-3/4,-x-1/4,-z-1/4;-y-3/4,x-3/4,-z-3/4;-x+1/2,-y+1/2,-z+1/2;x,y+1/2,-z;y-1/4,-x+1/4,-z+1/4;-y-1/4,x-1/4,-z-1/4": ['Tetragonal', 'I 41/a'],
}


#Atomic moleculat weight taken from the MPQC program : http://www.mpqc.org
AtomicWeight={
'Ac':227.03,    'Ag':107.87,    'Al':26.98,     'Am':243.00,    'Ar':39.96,
'As':74.92,     'At':210.00,    'Au':196.97,    'B':11.01,      'Ba':137.33,
'Be':9.01,      'Bi':208.98,    'Bk':247.00,    'Br':79.90,     'C':12.01,
'Ca':39.96,     'Cd':112.41,    'Ce':140.12,    'Cf':251.00,    'Cl':35.45,
'Cm':247.00,    'Co':58.93,     'Cr':51.94,     'Cs':132.91,    'Cu':63.55,
'Dy':162.50,    'Er':167.26,    'Es':254.00,    'Eu':151.96,    'F':19.00,
'Fe':55.85,     'Fm':257.00,    'Fr':223.00,    'Ga':68.93,     'Gd':157.25,
'Ge':73.92,     'H':1.01,       'Ha':260.00,    'He':4.00,      'Hf':178.49,
'Hg':200.59,    'Ho':164.93,    'I':126.90,     'In':114.82,    'Ir':192.22,
'K':39.10,      'Kr':83.91,     'La':138.91,    'Li':6.94,      'Lr':260.00,
'Lu':174.97,    'Md':258.00,    'Mg':23.99,     'Mn':54.94,     'Mo':95.94,
'N':14.01,      'Na':22.99,     'Nb':92.91,     'Nd':144.24,    'Ne':19.99,
'Ni':58.70,     'No':259.00,    'Np':237.05,    'O':16.00,      'Os':190.20,
'P':30.97,      'Pa':231.04,    'Pb':207.20,    'Pd':106.40,    'Pm':145.00,
'Po':209.00,    'Pr':140.91,    'Pt':195.09,    'Pu':244.00,    'Ra':226.03,
'Rb':85.47,     'Re':186.21,    'Rf':260.00,    'Rh':102.91,    'Rn':222.00,
'Ru':101.07,    'S':32.06,      'Sb':121.75,    'Sc':44.96,     'Se':79.92,
'Si':27.98,     'Sm':150.40,    'Sn':118.69,    'Sr':87.62,     'Ta':180.95,
'Tb':158.93,    'Tc':98.00,     'Te':127.60,    'Th':232.04,    'Ti':47.95,
'Tl':204.37,    'Tm':168.93,    'U':238.03,     'Un':266.00,    'V':50.94,
'W':183.85,     'Xe':131.30,    'Y':88.91,      'Yb':173.04,    'Zn':65.35,
'Zr':91.22
}

NeededForRST={"_chemical_name_common":"Name of the molecule",
			"_symmetry_cell_setting":"Cell setting",
			"_symmetry_space_group_name_H-M":"Space group",
			"_cell_length_a":"Length a (Å)",
			"_cell_length_b":"Length b (Å)",
			"_cell_length_c":"Length c (Å)",
			"_cell_angle_alpha":"Angle alpha (°)",
			"_cell_angle_beta":"Angle beta (°)",
			"_cell_angle_gamma":"Angle gamma (°)",
			"_chemical_formula_moiety":"Chemical formula",
			"_chemical_formula_weight":"Molecular weight",
			"_diffrn_ambient_temperature":"Temperature (K)",
			"_diffrn_radiation_wavelength":"Wavelength (Å)",
			"_diffrn_radiation_type":"X-Ray source",
			"_diffrn_radiation_monochromator":"Monochromator",
			"_cell_formula_units_Z":"Molecule per cell (Z)",
			"_exptl_crystal_density_diffrn":"Density (Mg/m³)",
			"_diffrn_reflns_number":"Total number of reflexions" ,
			"_reflns_number_total": "Total number of UNIC reflexions",
#			"_refine_ls_R_factor_gt":"R factor",
#			"_computing_data_collection":"Data collection",
			"_diffrn_measurement_device_type":"Diffractometer",
			"_exptl_special_details" : "Experimental details",
			"_cell_volume": "Cell volume (Å³)",
			"_exptl_crystal_F_000": "F(000) (effective number of electrons)",
			"_diffrn_reflns_theta_min": "Theta min (°)",
			"_diffrn_reflns_theta_max": "Theta max (°)",
			"_diffrn_reflns_limit_h_min":"Minimal h indice",
			"_diffrn_reflns_limit_h_max":"Maximal h indice",
			"_diffrn_reflns_limit_k_min":"Minimal k indice",
			"_diffrn_reflns_limit_k_max":"Maximal k indice",
			"_diffrn_reflns_limit_l_min":"Minimal l indice",
			"_diffrn_reflns_limit_l_max":"Maximal l indice",
			"_diffrn_reflns_av_R_equivalents":"Average Residual for each reflection class",
			"_diffrn_measured_fraction_theta_max":"Completeness to theta_max",
			"_refine_ls_number_reflns":"Number of reflexions",			
			"_refine_ls_number_parameters":"Number of paramaters",
			"_refine_ls_number_restraints":"Number of restraints",
			"_refine_ls_goodness_of_fit_ref":"Goodness of fit",
			"_refine_ls_R_factor_gt":"R factor on intense reflections",
			"_refine_ls_R_factor_all":"R factor on all reflections",
			"_refine_ls_wR_factor_ref":"Weighted R factor on all reflections",
			"_refine_ls_wR_factor_gt":"Weighted R factor on intense reflections",
			"_refine_ls_abs_structure_Flack":"Absolute Structure parameter",
#			"_refine_ls_extinction_coef":"Extinction coefficient.",
			"_refine_diff_density_max":"Largest electron density peak (e/Å³)",
			"_refine_diff_density_min":"Deepest electron density hole (e/Å³)",
			"_exptl_absorpt_coefficient_mu":"Absorption coefficient",
			}

NeededForCSD={#"_database_code_CSD":"Database Code", #by another way
			"_publ_author_name":"Author",
			"_symmetry_cell_setting":"Cell setting",
			"_symmetry_space_group_name_H-M":"Space group",
			"_cell_length_a":"Length a (Å)",
			"_cell_length_b":"Length b (Å)",
			"_cell_length_c":"Length c (Å)",
			"_cell_angle_alpha":"Angle alpha (°)",
			"_cell_angle_beta":"Angle beta (°)",
			"_cell_angle_gamma":"Angle gamma (°)",
			"_chemical_formula_moiety":"Chemical formula",
			"_chemical_formula_weight":"Molecular weight",
			"_diffrn_radiation_type":"X-Ray source",
			"_cell_formula_units_Z":"Molecule per cell (Z)",
			"_cell_volume": "Cell volume (Å³)",
			"_exptl_crystal_density_diffrn":"Density (Mg/m³)",
			"_refine_ls_R_factor_gt":"R factor on intense reflections",
			"_chemical_name_systematic":"Chemical name",
			"_chemical_name_common":"Chemical name (synonym)",
			"_publ_section_comment":"Other comments"
				}

UpperKey=['_atom_site_B_iso_or_equiv','_symmetry_space_group_name_Hall',
'_atom_site_Cartn_x','_atom_site_Cartn_y','_atom_site_Cartn_z','_atom_site_U_iso_or_equiv',
'_atom_site_Wyckoff_symbol','_atom_site_aniso_B_11','_atom_site_aniso_B_12','_atom_site_aniso_B_13',
'_atom_site_aniso_B_22','_atom_site_aniso_B_23','_atom_site_aniso_B_33','_atom_site_aniso_U_11',
'_atom_site_aniso_U_12','_atom_site_aniso_U_13','_atom_site_aniso_U_22','_atom_site_aniso_U_23',
'_atom_site_aniso_U_33','_atom_sites_Cartn_tran_matrix_11','_atom_sites_Cartn_tran_matrix_12','_atom_sites_Cartn_tran_matrix_13',
'_atom_sites_Cartn_tran_matrix_21','_atom_sites_Cartn_tran_matrix_22','_atom_sites_Cartn_tran_matrix_23','_atom_sites_Cartn_tran_matrix_31',
'_atom_sites_Cartn_tran_matrix_32','_atom_sites_Cartn_tran_matrix_33','_atom_sites_Cartn_transform_axes','_atom_type_scat_Cromer_Mann_a1',
'_atom_type_scat_Cromer_Mann_a2','_atom_type_scat_Cromer_Mann_a3','_atom_type_scat_Cromer_Mann_a4','_atom_type_scat_Cromer_Mann_b1',
'_atom_type_scat_Cromer_Mann_b2','_atom_type_scat_Cromer_Mann_b3','_atom_type_scat_Cromer_Mann_b4','_atom_type_scat_Cromer_Mann_c',
'_cell_formula_units_Z','_chemical_conn_atom_NCA','_chemical_conn_atom_NH','_database_code_CAS',
'_database_code_CSD','_database_code_ICSD','_database_code_MDF','_database_code_NBS',
'_database_code_PDF','_database_journal_ASTM','_database_journal_CSD','_diffrn_orient_matrix_UB_11',
'_diffrn_orient_matrix_UB_12','_diffrn_orient_matrix_UB_13','_diffrn_orient_matrix_UB_21','_diffrn_orient_matrix_UB_22',
'_diffrn_orient_matrix_UB_23','_diffrn_orient_matrix_UB_31','_diffrn_orient_matrix_UB_32','_diffrn_orient_matrix_UB_33',
'_diffrn_reflns_av_R_equivalents','_diffrn_reflns_av_sigmaI/netI','_exptl_absorpt_correction_T_max','_exptl_absorpt_correction_T_min',
'_exptl_crystal_F_000','_geom_hbond_angle_DHA','_geom_hbond_atom_site_label_A','_geom_hbond_atom_site_label_D',
'_geom_hbond_atom_site_label_H','_geom_hbond_distance_DA','_geom_hbond_distance_DH','_geom_hbond_distance_HA',
'_geom_hbond_site_symmetry_A','_geom_hbond_site_symmetry_D','_geom_hbond_site_symmetry_H','_journal_coden_ASTM',
'_journal_coden_Cambridge','_refine_ls_R_factor_all','_refine_ls_R_factor_gt','_refine_ls_R_factor_obs',
'_refine_ls_abs_structure_Flack','_refine_ls_abs_structure_Rogers','_refine_ls_restrained_S_all','_refine_ls_restrained_S_obs',
'_refine_ls_wR_factor_all','_refine_ls_wR_factor_gt','_refine_ls_wR_factor_obs','_refine_ls_wR_factor_ref',
'_refln_A_calc','_refln_A_meas','_refln_B_calc','_refln_B_meas',
'_refln_F-squared_meas','_refln_F_calc','_refln_F_meas','_refln_F_sigma',
'_refln_F_squared_calc','_refln_F_squared_sigma','_reflns_scale_meas_F','_reflns_scale_meas_F_squared',
'',','',','_space_group_IT_number','_space_group_name_H-M',
'_space_group_name_H-M_alt','_space_group_name_Hall','_symmetry_Int_Tables_number','_symmetry_space_group_name_H-M',
]






DefaultAuthor="J. Kieffer"
Version=[" Generated by libcif.py : June 2005"," Written by Jerome Kieffer : Jerome.Kieffer@terre-adelie.org "," X-Ray Crystallography "," (France)"]

#check for the existance of Booleans : this is only if your python is too old
try:
        True
except:
    True=(1==1)
    False=(1==0)


EOL=["\r","\n","\r\n","\n\r"]
Blank=[" ","	"]+EOL
StartComment=["\"","\'"]

for i in EOL:
	StartComment.append((i+";"))

EndComment=[]
for i in EOL:
	EndComment.append(i+";")
for i in ["\"","\'"]:
	for j in Blank:
		EndComment.append(i+j)



def LoadCIF(filename):
	"""Load the CIF file and returns the dictionnary
	@param filename: the name of the file to open
	@type  filename: string
	@return: the CIF object corresponding to the Xtal structure
	@rtype: dictionnary"""
	cif=parsecif(readcif(filename))
	#this corrects a bug that has existed for a long time about the case of the cif-keys: we just transform all the lowercase field in conventionnal writing
	keys={}
	for i in UpperKey:
		keys[i.lower()]=i
	cif2={}
	for i in cif:
		j=i.lower()
		if j in keys.keys():
			cif2[keys[j]]=cif[i]
		else:
			cif2[j.lower()]=cif[i]
	return cif2 

		
	
def readcif(filename):
	"""-Check if the filename exists 
	
	-read the cif file
	
	-removes the comments 
	
	@param filename: the name of the CIF file
	@type filename: string
	@return: a string containing the raw data
	@rtype: string"""
	if not os.path.isfile(filename):
		raise("I cannot find the file %s"%filename)
		sys.exit(1)
	f=open(filename,"r").readlines()
	text=""
	for ligne in f:
		pos=ligne.find("#")
		if pos >=0:
			text+=ligne[:pos]+"\n"
			if pos>80 : 
				print "Warning, this line is too long and could cause problems in PreQuest\n",ligne
		else :
			text+=ligne
			if len(ligne.strip())>80 : 
				print "Warning, this line is too long and could cause problems in PreQuest\n",ligne
	return text


def oneloop(fields,start):
	"""Processes one loop in the data extraction of the CIF file
	@param fields: list of all the words contained in the cif file
	@type fields: list
	@param start: the starting index corresponding to the "loop_" key 
	@type start: integer
	@return: the list of loop dictionnaries, the length of the data extracted from the fields and the list of all the keys of the loop.
	@rtype: tupple
	"""
#	in earch loop we first search the length of the loop
	curloop={}
	loop=[]
	keys=[]
	i=start+1
	fini=False
	while not fini:
		if fields[i][0]=="_":
			keys.append(fields[i])#.lower())
			i+=1
		else:
			fini=True
	data=[]
	while True:
		if i>=len(fields):
			break
		elif len(fields[i])==0:
			break	
		elif fields[i][0]=="_":
			break
		elif fields[i] in ["loop_","stop_","global_","data_","save_"]:
			break
		else:
			data.append(fields[i])
			i+=1
#	print len(keys), len(data)
	k=0
	
	if len(data)<len(keys):
		element={}
		for j in keys:
			if k<len(data):
				element[j]=data[k]	
			else :
				element[j]="?"
			k+=1
#		print element
		loop.append(element)	
		
	else:
		for i in range(len(data)/len(keys)):
			element={}
			for j in keys:
				element[j]=data[k]
				k+=1
#			print element
			loop.append(element)
#	print loop
	return loop,1+len(keys)+len(data),keys
	
def parsecif(text):
	""" 
	-Parses the text of a CIF file
	
	-Cut it in fields
	
	-Find all the loops and process
	
	-Find all the keys and values  
	
	@param text: the content of the CIF-file
	@type text: string
	@return: An CIF dictionnary
	@rtype: dictionnary
	"""

	cif={}
	loopidx=[]
	looplen=[]
	start=0
	loop=[]
	#first of all : separate the cif file in fields
	fields=splitcif(text.strip())
	#Then : look for loops
	for i in range(len(fields)):
		if fields[i].lower()=="loop_":
			loopidx.append(i)
	if len(loopidx)>0:
		for i in loopidx:
			loopone,length,keys=oneloop(fields,i)
			loop.append([keys,loopone])
			looplen.append(length)

 
		for i in range(len(loopidx)-1,-1,-1):
			f1=fields[:loopidx[i]]+fields[loopidx[i]+looplen[i]:]
			fields=f1
	
		cif["loop_"]=loop
	for i in range(len(fields)-1):
		if fields[i][0]=="_" and fields[i+1][0]!="_":
			cif[fields[i]]=fields[i+1]
	return cif	
		 

def splitcif(text):
	"""Separate the text in fields as defined in the CIF
	@param text: the content of the CIF-file
	@type text: string
	@return: list of all the fields of the CIF
	@rtype: list
	"""
	fields=[]
	while True:
		if len(text)==0: 
			break
		elif text[0]=="'":
			idx=0
			fini=False
			while not  fini:
				idx+=1+text[idx+1:].find("'")
##########debuging	in case we arrive at the end of the text 			
				if idx>=len(text)-1: 
#					print text,idx,len(text)
					fields.append(text[1:-1].strip())
					text=""
					fini=True
					break				

				if text[idx+1] in Blank:
					fields.append(text[1:idx].strip())
					text1=text[idx+1:]
					text=text1.strip()
					fini=True

		elif text[0]=='"':
			idx=0
			fini=False
			while not  fini:
				idx+=1+text[idx+1:].find('"')
##########debuging	in case we arrive at the end of the text 			
				if idx>=len(text)-1: 
#					print text,idx,len(text)
					fields.append(text[1:-1].strip())
					text=""
					fini=True
					break				

				if text[idx+1] in Blank:
					fields.append(text[1:idx].strip())
					text1=text[idx+1:]
					text=text1.strip()
					fini=True
		elif text[0]==';':
			idx=0
			fini=False
			while not  fini:
				idx+=1+text[idx+1:].find(';')
				if text[idx-1] in EOL:
					fields.append(text[1:idx-1].strip())
					text1=text[idx+1:]
					text=text1.strip()
					fini=True
		else:
			f=text.split(None,1)[0]
			fields.append(f)
			text1=text[len(f):].strip()
			text=text1

	return fields




#############################################################################################
########     everything needed to  write a cif file #########################################
#############################################################################################

def SaveCIF(cif,filename="test.cif"):
	"""transforms the CIF object in string and write it into the given file"""
	txt=cif2str(cif)
	try:
		f=open(filename,"w")
		f.write(txt)
		f.close()
	except:
		raise("Error during the writing of this file : %s"%filename)  



def cif2str(cif):
	"""converts a cif dictionnary to a string according to the CIF syntax
	@param cif: the CIF dictionnary correspondinf to a Xtal structure
	@return : a sting that corresponds to the content of the CIF-file.
	"""
	txt=""
	for i in Version:
		txt+="#"+i+"\n"
	if exists(cif,"_chemical_name_common"):
		t=cif["_chemical_name_common"].split()[0]
	else:
		t=""
	txt+="data_%s\n"%t
	#first of all get all the keys :
	keys=cif.keys()
	keys.sort()
	for i in keys:
		if i=="loop_":continue
		value=cif[i]
		if value.find("\n")>-1: #should add value  between ;;
			ligne="%s \n;\n %s \n;\n"%(i,value)
		elif len(value.split())>1: #should add value between ''
			ligne="%s		'%s' \n"%(i,value)
			if len(ligne)>80:
				ligne="%s\n '%s' \n"%(i,value)
		else:
			ligne="%s		%s \n"%(i,value)
			if len(ligne)>80:
				ligne="%s\n %s \n"%(i,value)
 		txt+=ligne
	if cif.has_key("loop_"):
		for loop in cif["loop_"]:
			txt+="loop_ \n"
			keys=loop[0]
			data=loop[1]
			for i in keys:
				txt+=" %s \n"%i
			for i in data:
				ligne=""
				for key in keys:
					rawvalue=i[key]
					if rawvalue.find("\n")>-1: #should add value  between ;;
						ligne+="\n; %s \n;\n"%(rawvalue)
						txt+=ligne
						ligne=""
					else:
						if len(rawvalue.split())>1: #should add value between ''
							value="'%s'"%(rawvalue)
						else:
							value=rawvalue
						if len(ligne)+len(value) > 78:
							txt+=ligne+" \n"
							ligne=" "+value
						else:
							ligne+=" "+value
				txt+=ligne+" \n"
			txt+="\n"
	return txt







################################################################################################
#########         few  calculation  on  the  structure                                    ######
################################################################################################

def CheckSym(cif,fix=False):
	"""
	Checks the symetry of a CIF file based on the symmetry operations
	
	@param cif: the CIF dictionnary of a Xtal structure
	@param fix: True if you want a corrected version of the CIF to be returned
	@return: the warning if the symmetry is not coherent inside the CIF data
	@rtype: string
	"""
	warning=""
	so=symop(cif)
	if len(so)==0 :
		warning+="Warning : no symmetry operation detected\n"
	elif not Symmetries.has_key(so):
		warning+="Warning : the symmetry exists but is not defined in the program, please check the data and the programm\n%s\n"%so
	else:
		[cell,sg]=Symmetries[so]
		if cif.has_key("_symmetry_cell_setting"):
			if cell.lower()!=cif["_symmetry_cell_setting"].lower():
				warning+="Warning : I found a %s cell wheras it is set to %s. \n"%(cell,cif["_symmetry_cell_setting"])
				cif["_symmetry_cell_setting"]=cell
		else:
			warning+="Warning : The symmetry of the cell is not set but I think it is %s.\n"%(cell)
			cif["_symmetry_cell_setting"]=cell
		if cif.has_key("_symmetry_space_group_name_H-M"):
			if sg.lower()!=cif["_symmetry_space_group_name_H-M"].lower():
				warning+="Warning : I found a %s space group wheras it is set to %s. \n"%(sg,cif["_symmetry_space_group_name_H-M"])
				cif["_symmetry_space_group_name_H-M"]=sg
		else:
			warning+="Warning : The Space Group is not set but I think it is %s.\n"%(sg)
			cif["_symmetry_space_group_name_H-M"]=sg
	if fix:
		return warning,cif
	else:
		return warning					

def symop(cif):
	"""Lists all the symetricaly equivalent positions\
	@param cif: CIF object of the Xtal structure
	@type cif: dictionnary 
	@return: ";" separated list of xyz equivalent positions 
	@rtype: string
	"""
	txt=""
	for loop in cif["loop_"]:
		for key in loop[0]:
			if key=="_symmetry_equiv_pos_as_xyz":
				for i in loop[1]: txt+=(i["_symmetry_equiv_pos_as_xyz"]+";")
	txt2,count=re.subn(" ","",txt[:-1])
	txt3,count=re.subn(";+",";",txt2.lower())
	txt,count=re.subn(",+",",",txt3)
	newtxt=""	
	for i in txt.split(";"):
		for j in i.split(","):
#		 	print "txt=", j
			pos=0
			for k in ["x","y","z"]:
				if j.find(k)!=-1:
					pos=j.find(k)
					break
			if pos==0:
				sig="+"
			else:
				sig=j[pos-1]
			res=""
			if pos in [0,1]:
				if pos<len(j)-1:
					res=j[pos+1:]
				else:
					res=""
			else:
				res=j[:pos-1]
			if len(res)>0 :
				if res[0] not in ["+","-"]:
					res="+"+res
			#print j+"="+sig,j[pos],res
			if sig=="-":
				t="-"+j[pos]+res
			else:
				t=j[pos]+res
#			if t!=j:print j+"="+t
			newtxt+=t+","
		newtxt=newtxt[:-1]+";"
						
	return newtxt[:-1]




	
def exists(cif,key):
	"""
	Check if the key exists in the CIF.
	@param key: CIF kay
	@type key: string
	@param cif: CIF dictionnary
	@return: True if the key exists in the CIF dictionnary and is non empty
	@rtype: boolean
	"""
	bool=False
	if cif.has_key(key):
		if len(cif[key])>=1:
			if cif[key][0]!="?" : bool=True
	return bool

def CellVol(cif):
	"""calculate the cell volume and return it as a real (in Å³)"""
	needed=["_cell_length_a","_cell_length_b","_cell_length_c","_cell_angle_alpha",
			"_cell_angle_beta","_cell_angle_gamma"]
	for i in needed:
		if not exists(cif,i):
			return 0
	import math
	a=floatp(cif["_cell_length_a"])
	b=floatp(cif["_cell_length_b"])	
	c=floatp(cif["_cell_length_c"])
	ca=math.cos(math.pi/180*floatp(cif["_cell_angle_alpha"]))	
	cb=math.cos(math.pi/180*floatp(cif["_cell_angle_beta"]))
	cc=math.cos(math.pi/180*floatp(cif["_cell_angle_gamma"]))	
	return a*b*c*math.sqrt(1-ca*ca-cb*cb-cc*cc+2*ca*cb*cc)

def Zprime(cif):
	"""Calculate Z' = Z/nop if the latice is primitive zp=2*Z/nop if the latice is centered ..."""
	zp=float(cif["_cell_formula_units_Z"])/len(symop(cif).split(";"))
	return str(int(zp))
#cif["_cell_formula_units_Z"]=str(zp*len(symop(cif).split(";")))	

def MolForm(cif,zp):
	"""count the atoms and returns the  molecular formula. Zp is the number of molecule per asymetric cell"""
	form={}
	for loop in cif["loop_"]:
		for key in loop[0]:
			if key=="_atom_site_type_symbol":
				for i in loop[1]: 
					atom=i["_atom_site_type_symbol"]
					try:
						occ=i["_atom_site_occupancy"]
					except:
						occ="1"
					if atom in form.keys():
						form[atom]+=floatp(occ)
					else:
						form[atom]=floatp(occ)	
	keys=form.keys()
	keys.sort()
	try:
		keys.remove("H")
		keys=["H"]+keys
	except:
		pass
	try:
		keys.remove("C")
		keys=["C"]+keys
	except:
		pass	
	txt=""
	for i in keys:
		if abs(form[i]/zp-1)<1E-3:
			txt+="%s "%(i)
		else:
			txt+="%s%i "%(i,form[i]/zp)
	return txt.strip()

def MolWeight(formula):
	"""calculate the molecular weight of a compound using its formula"""
	MW=0
	for sub in formula.split():
		j=sub.strip()
		atom=""
		count=""
		for i in j:
			figures= [ str(x) for x in range(10)]
			if i in figures:
				count+=i
			else:
				atom+=i
		if AtomicWeight.has_key(atom):
			if len(count)==0:
				x=1
			else:
				x=floatp(count)	
			MW+=AtomicWeight[atom]*x
		else:
			print "WARNING !!! the program is lacking the molecular weight of "+atom
	return MW		

def Density(cif):
	"""calculate the density in Mg/m³, for information : 10^30/Na/10^6=1.66054018667"""
	MW=floatp(cif["_chemical_formula_weight"])
	cell=floatp(cif["_cell_volume"])
	Z=int(cif["_cell_formula_units_Z"])
	return 1.66054018667*MW*Z/cell

def AsymetricCellContents(cif):
	"""tries to find the contents of the asymetric cell """
	txt=""
	if exists(cif,"_chemical_formula_moiety"):
		 txt=cif["_chemical_formula_moiety"]
	
	return txt.split(",")




	
def CheckForRST(cif):
	"""check in the CIF data if all the data needed to generate a RST report are present. 
	If not it will ask many anoying questions"""
	if exists(cif,"_computing_data_collection") and not exists(cif,"_diffrn_measurement_device_type"):
		cif["_diffrn_measurement_device_type"]=cif["_computing_data_collection"]
	table=NeededForRST.keys()
	table.sort()
	modified=False
	for key in table:
		if not exists(cif,key):
			modified=True
			txt=raw_input(" %s ? (%s) -->"%(NeededForRST[key],key))
			if len(txt)==0:txt="?"
			cif[key]=txt
	return cif,modified

def CheckForCSD(cif,name="None"):
	"""check in the CIF data if all the data needed to generate a RST report are present. 
	If not it will ask many anoying questions"""
	if name[-4:].lower()==".cif":name=name[:-4]
	modified=False
	if not exists(cif,"_diffrn_ambient_temperature") and exists(cif,"_cell_measurement_temperature"):
		modified=True
		cif["_diffrn_ambient_temperature"]=cif["_cell_measurement_temperature"]
	if not exists(cif,"_cell_volume"):
		vol=CellVol(cif)
		if vol>1:	
			modified=True
			cif["_cell_volume"]="%8.2f"%vol
	if not exists(cif,"_cell_formula_units_Z"):
		modified=True
		txt=raw_input(" Number of molecules per asymmetric cell ? (Z') -->")
		try:
			zp=int(txt)
		except:
			zp=1
		cif["_cell_formula_units_Z"]=str(zp*len(symop(cif).split(";")))		
	if not exists(cif,"_chemical_formula_sum"):
		cif["_chemical_formula_sum"]=MolForm(cif,int(cif["_cell_formula_units_Z"])/len(symop(cif).split(";")))

	if not exists(cif,"_chemical_formula_moiety"):
		modified=True
		txt=raw_input(" Chemical formula ? (_chemical_formula_moiety) [%s] -->"%cif["_chemical_formula_sum"])
		if txt=="":
			cif["_chemical_formula_moiety"]=cif["_chemical_formula_sum"]
		else:
			cif["_chemical_formula_moiety"]=txt.upper().strip()
			
	if cif["_chemical_formula_moiety"]=="C6 H12 O6":
		modified=True
		txt=raw_input(" Chemical formula ? (_chemical_formula_moiety) [%s] -->"%cif["_chemical_formula_sum"])
		if txt=="":
			cif["_chemical_formula_moiety"]=cif["_chemical_formula_sum"]
		else:
			cif["_chemical_formula_moiety"]=txt.upper().strip()	
		
	if not exists(cif,"_chemical_formula_weight") and exists(cif,"_chemical_formula_sum"):
		cif["_chemical_formula_weight"]="%7.2f"%MolWeight(cif["_chemical_formula_sum"])

	if not exists(cif,"_exptl_crystal_density_diffrn") and exists(cif,"_cell_volume") and exists(cif,"_cell_formula_units_Z") and exists(cif, "_chemical_formula_weight"):
		cif["_exptl_crystal_density_diffrn"]="%5.3f"%Density(cif)

	if not exists(cif,"_refine_ls_R_factor_gt") and exists(cif,"_refine_ls_R_factor_obs"):
		cif["_refine_ls_R_factor_gt"]=cif["_refine_ls_R_factor_obs"]

	if not exists(cif,"_publ_author_name"):
		modified=True
		txt=raw_input(" Author ? (_publ_author_name) [%s] -->"%DefaultAuthor)
		if txt=="":
			cif["_publ_author_name"]=DefaultAuthor
		else:
			cif["_publ_author_name"]=txt	
	if not exists(cif,"_journal_coden_Cambridge"):
		cif["_journal_coden_Cambridge"]="1078" # CAD "private communication"
	if not exists(cif,"_journal_year"):
		cif["_journal_year"]=str(time.localtime()[0]) # Publication year needed

	if not exists(cif,"_chemical_name_systematic"):
		modified=True
		txt=raw_input(" Chemical name ? (_chemical_name_systematic) [%s] -->"%name)
		if txt=="":
			cif["_chemical_name_systematic"]=name
		else:
			cif["_chemical_name_systematic"]=txt	
	
	if not exists(cif,"_chemical_name_common") and exists(cif,"_chemical_name_systematic"):
		modified=True
		txt=raw_input(" Chemical name (synonym) ? (_chemical_name_common) [%s] -->"%cif["_chemical_name_systematic"])
		if txt=="":
			cif["_chemical_name_common"]=cif["_chemical_name_systematic"]
		else:
			cif["_chemical_name_common"]=txt	

	
	table=NeededForCSD.keys()
	table.sort()
	for key in table:
		if not exists(cif,key):
			modified=True
			txt=raw_input(" %s ? (%s) -->"%(NeededForCSD[key],key))
			if len(txt)==0:txt="?"
			cif[key]=txt

	return cif,modified









######################################################################
###### Some   P.L.A.T.O.N.  related stuff         ####################		
######################################################################

def platon(filename):
	"""process the data throught PLATON 
	@param filename: name of the CIF (or .res ....) file
	@type filename: string  
	@return: the CIF data generated by PLATON
	@rtype: dictionnary
	"""
	chiral=[]
	if not os.path.isfile(filename): 
		raise "error in the platon procedure : %s filename does not exist"%filename
	i,o=os.popen2("platon -o %s"%filename)
	i.write("TABL CIF\n")
	i.flush()
	for l in o.readlines(): 
		print l.strip()
		if l.find("Chiral:")>-1:
			m=l.split()
			c={}
			c["_atom_site_asymmetry_label"]=m[1]
			c["_atom_site_asymmetry_type"]=m[9]
			chiral.append(c)
	o.close()
	i.close()
	cif=LoadCIF(os.path.splitext(filename)[0]+".acc")

	#here we remove the empty loops
	loops=cif["loop_"][:] #it is unwisy to modify a list used as loop iterator 
	for loop in loops:  
		if len(loop[1])==1:
			empty=True
			for i in loop[0]:
				if exists(loop[1][0],i):empty=False
			if empty: cif["loop_"].remove(loop)
			

	#here we append the information about chirality
	if len(chiral)>0:
		if exists(cif,"loop_"):
			cif["loop_"].append([["_atom_site_asymmetry_label","_atom_site_asymmetry_type"],chiral])	
		else:
			cif["loop_"]=[[chiral[0].keys(),chiral]]
	return cif

def mergeplaton(cif,acc):
	"""Merge cif and acc and returns a completed CIF-object.
	Special care is taken to select the most usefull data generated by platon
	@param cif: the initial CIF-object
	@type cif: dictionnary
	@param acc: the CIF-object generated by platon
	@type acc: dictionnary
	@return: merged CIF-object
	@rtype: dictionnary
	"""
	cif1=cif
	cif2=acc
	#first of all removes the sugar ;)
	if exists(cif,"_chemical_formula_moiety") and cif["_chemical_formula_moiety"]=="C6 H12 O6":	cif["_chemical_formula_moiety"]="?"
	PassKey=["_publ_contact_letter","_publ_requested_journal","_publ_contact_letter","_loop","_publ_section_references","_publ_section_figure_captions"]
	for i in cif2:
		if i in PassKey:
			continue
		if ( not exists(cif,i)) and exists(cif2,i):
			cif[i]=cif2[i]
	loop1=[]
	for loop in cif["loop_"]:
		loop1.append(loop[0])
	for loop in cif2["loop_"]:
		exist=False
		curkeys=loop[0]
		for l1 in loop1:
			c=0
			for i in l1:
				if i in curkeys:
					c+=1
#			if c>0 : print curkeys,c,len(l1),len(curkeys)
			if c==len(l1) or c>round(0.8*len(curkeys)): #here we accept if at least 80% is good.
				exist=True
				continue
		if not exist:
			cif["loop_"].append(loop)	 
	return cif


#########################################################################################










#########################################################################
###### Everything to write automaticalyy a report #######################
#########################################################################
	
	
def Html2table(html,BL,X,Y):
	"""	This function appends a table element to the html file with the X and Y headers"""
	html.start("p")
	html.start("table cellspacing=10")
	html.start("tr")
	html.element("th",X)
	html.element("th",Y)
	keys=BL.keys()
	keys.sort()
	for i in keys:
		html.end("tr")
		html.start("tr")
		html.element("td", i)
		html.element("td", BL[i])
	html.end("tr")
	html.end("table cellspacing=10")
	html.end("p")


def AtomicCoord(html,table):
	"""	This function appends a table with label, y, y, z and U to the html file"""
	html.start("p")
	html.start("table cellspacing=10")
	html.start("tr")
	html.element("th","Label")
	html.element("th","x")
	html.element("th","y")
	html.element("th","z")
	html.element("th","U(eq)")
	for i in table:
		html.end("tr")
		html.start("tr")
		html.element("td", i[0])
		html.element("td", i[1])
		html.element("td", i[2])
		html.element("td", i[3])
		html.element("td", i[4])
	html.end("tr")
	html.end("table cellspacing=10")
	html.end("p")
	


def XraySummary(html,cif):
	"""
	This function appends a table summarizing the Xray analysis, usually in Annexe as table 1
	@param html: HTML file represented as an XML-object
	@type html: XML object
	@param cif: The CIF-object of the Xtal structure 
	@type cif: dictionnary
	@return: None
	"""
	
	html.start("p")
	html.start("table cellspacing=15")
	html.start("tr")
	html.element("td","Identification code")
	html.element("td",cif["_chemical_name_common"])
	html.end("tr")
	html.start("tr")
	html.element("td","Chemical formula")
	html.element("td",cif["_chemical_formula_sum"])
	html.end("tr")
	html.start("tr")
	html.element("td","Molecular weight")
	html.element("td",cif["_chemical_formula_weight"])
	html.end("tr")
	html.start("tr")
	html.element("td","Temperature")
	html.element("td",cif["_diffrn_ambient_temperature"])
	html.end("tr")
	html.start("tr")
	html.element("td","Wavelength")
	html.element("td",cif["_diffrn_radiation_wavelength"])
	html.end("tr")
	html.start("tr")
	html.element("td","Crystal system ; space group")
	html.element("td","%s ; %s"%(cif["_symmetry_cell_setting"],cif["_symmetry_space_group_name_H-M"]))
	html.end("tr")
	html.start("tr")
	html.element("td","Unit cell dimentions")
	html.start("td")
	html.rawdata("<table><tr><td>a = %s </td><td> &Aring; ; &alpha; = %s °</td></tr>"%(cif["_cell_length_a"],cif["_cell_angle_alpha"]))
	html.rawdata("<tr><td> b = %s </td><td> &Aring; ;  &beta; = %s °</td></tr>"%(cif["_cell_length_b"],cif["_cell_angle_beta"]))
	html.rawdata("<tr><td> c = %s </td><td> &Aring; ;  &gamma; = %s °</td></tr></table> "%(cif["_cell_length_c"],cif["_cell_angle_gamma"]))
	html.end("td")
	html.end("tr")
	html.start("tr")
	html.element("td","Volume")
	html.rawdata("<td> %s &Aring;³ </td>"%(cif["_cell_volume"]))
	html.end("tr")
	html.start("tr")
	html.element("td","Z, Calculated density")
	html.element("td","%s, %s Mg/m³"%(cif["_cell_formula_units_Z"],cif["_exptl_crystal_density_diffrn"]))
	html.end("tr")
	html.start("tr")
	html.element("td","Absorption coefficient")
	html.element("td","%s 1/mm"%(cif["_exptl_absorpt_coefficient_mu"]))
	html.end("tr")
	html.start("tr")
	html.element("td","F(000)")
	html.element("td",cif["_exptl_crystal_F_000"])
	html.end("tr")
	html.start("tr")
	html.element("td","Theta range for data collection")
	html.element("td","%s° to %s°"%(cif["_diffrn_reflns_theta_min"],cif["_diffrn_reflns_theta_max"]))
	html.end("tr")
	html.start("tr")
	html.element("td","Limiting indices")
	html.element("td","%s <= h <= %s ; %s <= k <= %s ; %s <= l <= %s"%(cif["_diffrn_reflns_limit_h_min"],cif["_diffrn_reflns_limit_h_max"],cif["_diffrn_reflns_limit_k_min"],cif["_diffrn_reflns_limit_k_max"],cif["_diffrn_reflns_limit_l_min"],cif["_diffrn_reflns_limit_l_max"]))
	html.end("tr")
	html.start("tr")
	html.element("td","Reflexion collected / unique")
	html.element("td","%s / %s [R(int) = %s]"%(cif["_diffrn_reflns_number"],cif["_reflns_number_total"],cif["_diffrn_reflns_av_R_equivalents"]))	
	html.end("tr")
	html.start("tr")
	html.element("td","Completness to theta max")
	try:
		r=float(cif["_diffrn_measured_fraction_theta_max"])*100
	except:
		r=100
	html.element("td","%s %%"%r)
	html.end("tr")
	html.start("tr")
	html.element("td","Refinement method")
	html.element("td","Full-matrix least-square on F²")
	html.end("tr")
	html.start("tr")
	html.element("td","Data / restraints / parameters")
	html.element("td","%s / %s / %s"%(cif["_refine_ls_number_reflns"],cif["_refine_ls_number_restraints"],cif["_refine_ls_number_parameters"]))
	html.end("tr")
	html.start("tr")
	html.element("td","Goodness of fit on F²")
	html.element("td",cif["_refine_ls_goodness_of_fit_ref"])
	html.end("tr")
	html.start("tr")
	html.element("td","Final R indices [I>2sigma(I)]")
	html.element("td","R1 = %s ; wR2 = %s"%(cif["_refine_ls_R_factor_gt"],cif["_refine_ls_wR_factor_gt"]))
	html.end("tr")
	html.start("tr")
	html.element("td","Final R indices [all data]")
	html.element("td","R1 = %s ; wR2 = %s"%(cif["_refine_ls_R_factor_all"],cif["_refine_ls_wR_factor_ref"]))
	html.end("tr")	
	html.start("tr")
	html.element("td","Absolute structure parameter")
	html.element("td",cif["_refine_ls_abs_structure_Flack"])
	html.end("tr")	
#	html.start("tr")
#	html.element("td","Extinction coefficient")
#	html.element("td",cif["_refine_ls_extinction_coef"])
#	html.end("tr")
	html.start("tr")
	html.element("td","Largest diff peak and hole")
	html.rawdata("<td> %s and %s e/&Aring;³</td>"%(cif["_refine_diff_density_max"],cif["_refine_diff_density_min"]))
	html.end("tr")
#&lambda; = %s &Aring;	
	html.end("table cellspacing=15")
	html.end("p")
	

def WriteReport(filename,cif,Lang="En"):
	"""This function writes out an X-Ray structure report as an HTML file in the given language
	with the data taken from the CIF dictionnary
	
	@param filename: Name of the file (usually .cif or .html) 
	@type filename: string
	@param cif: The CIF-object of the Xtal structure 
	@type cif: dictionnary
	@param Lang: The language in which the repport has to be written, the default is English
	@type Lang: string
	"""
	if filename[-4:].lower()in [".cif",".htm",".htl",".lis"]:basename=filename[:-4]
	if filename[-5:].lower()==".html":basename=filename[:-5]

	if not os.path.isdir(basename):
		os.mkdir(basename)
	basename=os.path.join(basename,basename)

	SaveCIF(cif,basename+".cif")
	while not os.path.isfile("%s-%s.png"%(basename,"structure")):
		structureImage(basename,structure="structure")
	while not os.path.isfile("%s-%s.png"%(basename,"ADP")):
		structureImage(basename,structure="ADP")
	while not os.path.isfile("%s-%s.png"%(basename,"powder")):
		structureImage(basename,structure="powder")


	f=open(basename+".html","w")
	w = XMLWriter(f)
	html=w.start("html")
	w.start("head")
	
	if Lang.lower()=="fr":
		w.element("title","Rapport de diffraction X du %s \n"%cif["_chemical_name_common"])
	elif Lang.lower()in["en","us"]:
		w.element("title","Report of X-Ray diffraction of %s \n"%cif["_chemical_name_common"])
	for i in Version:
		w.element("meta", name="generator", value=i)		
	w.end("head")

	w.start("body")
	if Lang.lower()=="fr":
		MainreportFR(w,cif)
	elif Lang.lower()in["en","us"]:
		MainreportEN(w,cif)
	w.start("center")
	w.element("h2","Appendix\n")
	w.element("hr"," ")
	w.element("h3","Figure 1 : Structural representation of the molecule with atoms labels." )
	w.rawdata('<img  src="%s-structure.png" border=0 Width="100%%">'% os.path.dirname(basename))
	w.element("hr"," ")
	w.element("h3","Figure 2 : Ortep representation of the molecule with thermal ellipsoids at 50%." )
	w.rawdata('<img  src="%s-ADP.png" border=0 Width="100%%">'% os.path.dirname(basename))
	w.element("hr"," ")
	w.element("h3","Figure 3 : Simulated powder diffraction pattern from the crystal structure." )
	w.rawdata('<img  src="%s-powder.png" border=0 Width="100%%">'% os.path.dirname(basename))
	w.element("hr"," ")
	w.element("h3","Table 1: Crystal data and structure refinement.\n")
	XraySummary(w,cif)
	w.element("hr"," ")
	w.start("h3")
	w.rawdata("""Table 2: Atomic coordinates (x 10<sup>4</sup>) and equivalent isotropic displacements parameters
	(&Aring;<sup>2</sup> x 10<sup>3</sup>).<br>U(eq) is defined as one third of the trace of the orthogonalized U<sub>ij</sub> tensor.""")
	w.end("h3")
	heavy,hydro=AtomPositions(cif)
	AtomicCoord(w,heavy)
	w.element("hr"," ")
	w.start("h3")
	w.rawdata("""Table 3: Bond lengths (&Aring;ngstrom).""")
	w.end("h3")
	Html2table(w,BondLength(cif),"Bond","Length (Å)")
	w.element("hr"," ")
	w.start("h3")
	w.rawdata("""Table 4: Bond angles (°).""")
	w.end("h3")
	Html2table(w,BondAngle(cif),"Atoms","Angle (°)")
	w.element("hr"," ")
	w.start("h3")
	w.rawdata("""Table 5: Hydrogen coordinates (x 10<sup>4</sup>) and isotropic displacements parameters
	(&Aring;<sup>2</sup> x 10<sup>3</sup>).""")
	w.end("h3")
	AtomicCoord(w,hydro)
	w.element("hr"," ")
#####################
	w.start("h3")
	w.rawdata("""Table 6: Hydrogen bonds with bond lengths (&Aring;ngstrom) and angles (degrees °).""")
	w.end("h3")

	w.start("p")
	w.start("table cellspacing=10")
	w.start("tr")
	w.element("th","D ---- H ...... A")
	w.element("th","Distance (D-H)")
	w.element("th","Distance (H..A)")
	w.element("th","Distance (D...A)")
	w.element("th","Angle (D-H..A)")

	for loop in cif["loop_"]:
		if loop[0][0].find("_geom_hbond")==0:
			for i in loop[1]:
				w.end("tr")
				w.start("tr")
				w.element("td", "%s - %s ... %s"%(i["_geom_hbond_atom_site_label_D"],i["_geom_hbond_atom_site_label_H"],i["_geom_hbond_atom_site_label_A"]))
				w.element("td",i["_geom_hbond_distance_DH"])
				w.element("td",i["_geom_hbond_distance_HA"])
				w.element("td",i["_geom_hbond_distance_DA"])
				w.element("td",i["_geom_hbond_angle_DHA"])
	w.end("tr")
	w.end("table cellspacing=10")
	w.end("p")
	w.element("hr"," ")
	w.end("center")
	w.end("body")
	w.close(html)
	f.close()
	print "Lauching Mozilla to view the report"
	os.system("mozilla file://%s &"%os.path.abspath("./"+basename+".html"))


def MainreportEN(html,cif):
	"""
	This function generates the report in ENGLISH and add it to the HTML file
	@param html: HTML file represented as an XML object
	@type html: XML object
	@param cif: The CIF-object of the Xtal structure
	@type cif: dictionnary
	@return: None
	"""
	html.start("center")
	html.element("h1","Determination of the crystal structure of %s by single crystal X-ray diffraction"%cif["_chemical_name_common"])	
	html.end("center")
	html.start("ol")
	html.start("h2")
	html.element("li","Introduction")
	html.end("h2")
	html.element("p","\n The aim of this study was to determine the crystalline structure of %s, to establish its solid state molecular geometry and to generate a simulated X-ray powder diffraction pattern corresponding to the structure, which could be compared with experimental patterns."%cif["_chemical_name_common"])
#to prepare a list of major non-covalent bonds that are responsible for the cohesion of the crystalline structure 
	html.start("h2")
	html.element("li","X-ray experimental parameters")
	html.end("h2")
	if exists(cif,"_exptl_special_details"):
		html.element("p","Slow evaporation from %s affords crystals suitable for X-rays diffraction studies. "%cif["_exptl_special_details"] )
	html.start("p")
	html.data("\nA single crystal selected by observation under a binocular microscope was mounted on the goniometric head of a %s diffractometer. "%(cif["_diffrn_measurement_device_type"]))
	html.data("\n Intensities were collected at")
	try:
			T=float(re.sub("\(.\)","",cif["_diffrn_ambient_temperature"]))
	except:
			T=293
	if T<280: 
			html.data(" low temperature (T=%i K), "%T)
	else:
			html.data(" room temperature (T=%i K), "%T)

	html.data("with the use of a %s monochromated "%cif["_diffrn_radiation_monochromator"])
	
	if cif["_diffrn_radiation_type"].find("Mo")==0: 
		html.rawdata("Mo K&alpha; radiation ")
	if cif["_diffrn_radiation_type"].find("Cu")==0: 
		html.rawdata("Cu K&alpha; radiation ")
	if 	cif["_diffrn_radiation_type"].lower().find("syn")==0: 
		html.data("synchrotron radiation ")
	html.rawdata("( &lambda; = %s &Aring; ).\n"%(cif["_diffrn_radiation_wavelength"]))
	
	if cif["_symmetry_space_group_name_H-M"].upper()[0]=="I":
		tmptxt="body centered"
	elif cif["_symmetry_space_group_name_H-M"].upper()[0]=="C":
		tmptxt="centered"
	else:
		tmptxt="primitive"
	html.data(" Systematic investigation of the diffraction nodes indicate that the crystal belong to the %s system, with a %s Bravais lattice. The unit cell parameters are:\n"%(cif["_symmetry_cell_setting"].lower(),tmptxt))
	html.end("p")
	html.start("center")
	html.rawdata("a (&Aring;) = %5.2f ; b (&Aring;) = %5.2f  ; c (&Aring;) = %5.2f  ; &alpha; (°) = %5.2f ; &beta; (°) = %5.2f ; &gamma; (°) = %5.2f"%(floatp(cif["_cell_length_a"]),floatp(cif["_cell_length_b"]),floatp(cif["_cell_length_c"]),floatp(cif["_cell_angle_alpha"]),floatp(cif["_cell_angle_beta"]),floatp(cif["_cell_angle_gamma"]))) 	
	html.end("center")

	html.start("p")
	html.data("\nIn view of the number of atoms in the %s molecule and of the unit cell volume, it is concluded that this unit cell must contain %s molecules having the formula \n "%(cif["_chemical_name_common"],cif["_cell_formula_units_Z"]))
	html.rawdata(formula2chem(cif["_chemical_formula_sum"]))
	html.data("\n which is equivalent to a calculated density of %s. The number of reflections collected was %s, of which %s were unique.\n"%(cif["_exptl_crystal_density_diffrn"],cif["_diffrn_reflns_number"],cif["_reflns_number_total"] ))
	html.end("p")

	if cif["_symmetry_space_group_name_H-M"].upper() in ["P 21","P21"]:
		html.element("p","\nDetermination of the space group was achieved  unequivocally due to the presence of an unique systematic extinction along the monoclinic axis.\n")
	elif cif["_symmetry_space_group_name_H-M"].upper() in ["P C","PC"]:
		html.element("p","\nDetermination of the space group was achieved  unequivocally due to the presence of an unique zonal extinction orthogonal to the monoclinic axis.\n")
	elif cif["_symmetry_space_group_name_H-M"].upper()[0]=="C":
		html.element("p","\nDetermination of the space group was achieved  unequivocally due to the presence of an integral extinction.\n")
	elif cif["_symmetry_space_group_name_H-M"].upper() in ["P 21 21 21","P212121"]:
		html.element("p","\nDetermination of the space group was achieved  unequivocally due to the presence of three systematic extinctions along the main crystal directions.\n")
	elif cif["_symmetry_space_group_name_H-M"].upper() in ["P 21/C","P21/C","P21/A","P 21/A","P21/N","P 21/N","C 2/C","C2/C"]:
		html.element("p","\nDetermination of the space group was achieved  unequivocally due to the presence of a systematic extinction along the monoclinic axis together with a systematic zonal extinction othogonal to this axis.\n")
	elif cif["_symmetry_space_group_name_H-M"].upper() in ["P -1","P -1"]:
		html.element("p","Based on the statistical distribution of the intensities, a centrosymetric structure is deduced.")
	elif cif["_symmetry_space_group_name_H-M"].upper() in ["P1","P 1"]:
		html.element("p","Based on the statistical distribution of the intensities, a non centrosymetric structure is deduced.")
	else :
		html.element("p","Raconter ici des conneries sur la symetrie de ce bordel")

	
	html.start("h2")
	html.element("li","Structure Refinements")
	html.end("h2")
	html.element("p","\nThe structure was solved by a direct methods using the SIR software [1]; and refined on F² by full least squares methods with SHELXTL [2]. All non hydrogen atoms were refined with anisotropic displacement parameters, a riding model was used for hydrogen atoms. Final agreement values  are R1 = %s (observed reflections) and wR2 = %s (all data) for %s reflections and %s parameters, with a goodness of fit of %s.\n"%(cif["_refine_ls_R_factor_gt"],cif["_refine_ls_wR_factor_ref"],cif["_refine_ls_number_reflns"],cif["_refine_ls_number_parameters"],cif["_refine_ls_goodness_of_fit_ref"]))
	html.start("h2")
	html.element("li","\nDescription of the structure \n")
	html.end("h2")
	html.start("p")
	html.data("\n The compound (figure 1 and 2) crystallize in the space group %s, the asymmetric unit of the crystal is made up of %s molecule of "%(cif["_symmetry_space_group_name_H-M"],Zprime(cif)))
	html.rawdata(cif["_chemical_name_common"])
	html.data(", thus %s formula are present in the unit cell. \n "%(cif["_cell_formula_units_Z"]))
	if len(cif["_chemical_formula_moiety"].split(","))==1:
		html.data("No additional molecule like organic or water is found.\n")
	else:
		html.data("The asymetric cell contains : ")
		html.rawdata(formula2chem(cif["_chemical_formula_moiety"]))
		html.data(".")
	html.data(" Examination of the molecular structure confirms that all bond angles and lengths stand in the standard range values.")
	html.end("p")

	html.element("p","""\n	Crystal data, X-rays experimental parameters and structure refinements are given in Table 1. 
	Table 2 lists the positional parameters for all independent non-hydrogen atoms together with their equivalent isotropic displacement parameters.
	Bond lengths and angles are listed Table 3 and 4. Hydrogen positions are reported Table 5. Table 6 lists all the hydrogen bonds. The figures were generated with the PLATON program [3].""")


	
	if exists(cif,"_refine_ls_abs_structure_Flack"):
		if cif["_refine_ls_abs_structure_Flack"]!=".":
			AbsStructEN(html,cif)


	html.start("h2")

	html.element("li","\nSimulated X-ray diffraction pattern.\n")
	html.end("h2")
	html.element("p","A simulated diffraction pattern (Figure 3) was produced from the experimentally determined crystalline structure. An experimental powder diffraction pattern can be compared to this theoretical pattern to demonstrate the nature of the crystalline structure. Minor differences (if any) can be explained by preferential orientations in the powder.")
	html.start("h2")
	html.element("li","\nConclusion\n")
	html.end("h2")
	html.element("p","The crystalline structure of %s was determined by X-ray diffraction on a single crystal, allowing the generation of a reference powder pattern."%cif["_chemical_name_common"])
	html.start("h2")
	html.element("li","\nReferences\n")
	html.end("h2")
	html.start("p")
	html.rawdata("[1] Altomare, A.; Cascarano, G.; Giacovazzo, C.; Guagliardi, A.; Burla, M. C.; Polidori, G.; Cavalli, A. J. Appl. Crystallogr. <b>1994</b>, 27, p 435-436.<br>")
	html.rawdata("[2] Sheldrick, G. M. SHELXTL-Plus, Rel. 5.03; Siemens Analytical X-ray Instruments Inc.: Madison, WI, <b>1995</b>.<br>")
	html.rawdata("[3] Spek, A.L. J. Appl. Cryst. <B>2003</B> 36, p 7-13.<br>")
	html.end("p")
	html.end("ol")
	html.element("hr"," ")



def MainreportFR(html,cif):
	"""this function generates the report in FRENCH to the HTML file"""
	html.start("center")
	html.element("h1","Détermination de la structure cristalline du composé %s par diffraction des rayons X sur monocristal"%cif["_chemical_name_common"])	
	html.end("center")
	html.start("ol")
	html.start("h2")
	html.element("li","Introduction")
	html.end("h2")
	html.element("p","\n Le but de ce travail est d'établir la structure cristalline du composé %s, de décrire sa géométrie moléculaire à l'état solide, d'inventorier les principales liaisons non covalentes responsables de la cohésion de l'édifice cristallin, et de générer le diagramme de diffraction X sur poudres simulé correspondant à la structure qui sera comparé aux enregistrements expérimentaux."%cif["_chemical_name_common"])
	html.start("h2")
	html.element("li","Paramètres Expérimentaux")
	html.end("h2")
	if exists(cif,"_exptl_special_details"):
		html.element("p","Provenance des cristaux : %s. "%cif["_exptl_special_details"] )
	html.start("p")
	html.data("\nUn monocristal sélectionné optiquement sous microscope binoculaire a été placé sur la tête goniométrique d'un diffractomètre %s"%(cif["_diffrn_measurement_device_type"]))
	try:
			T=floatp(cif["_diffrn_ambient_temperature"])
	except:
			T=293
	
	if T<280: 
			html.data(" à basse température (T=%i K), "%T)
	else:
			html.data(" à température ambiante (T=%i K), "%T)
	
	if cif["_diffrn_radiation_type"].find("MoK")==0: 
		html.data("et exposé aux rayons X produits par un tube à filament de molybdène ")
	if cif["_diffrn_radiation_type"].find("CuK")==0: 
		html.data("et exposé aux rayons X produits par un tube à filament de cuivre ")
	if 	cif["_diffrn_radiation_type"].find("CoK")==0: 
		html.data("et exposé aux rayons X produits par un tube à filament de cobalt ")
	html.rawdata("( &lambda; = %s &Aring; )\n"%(cif["_diffrn_radiation_wavelength"]))
	html.data(" après monochromatisation sur cristal de %s."%cif["_diffrn_radiation_monochromator"])
	html.data(" Une recherche systématique de noeuds de diffraction indique que le cristal appartient au système %sque avec les paramètres de maille suivants :\n"%cif["_symmetry_cell_setting"].lower()[:-1])
	html.end("p")
	html.start("center")
	html.rawdata(dot2virg("a = %5.2f &Aring; ; b = %5.2f &Aring; ; c = %5.2f &Aring; ; &alpha; = %5.2f° ; &beta; = %5.2f° ; &gamma; = %5.2f°"%(floatp(cif["_cell_length_a"]),floatp(cif["_cell_length_b"]),floatp(cif["_cell_length_c"]),float(cif["_cell_angle_alpha"]),floatp(cif["_cell_angle_beta"]),floatp(cif["_cell_angle_gamma"])))) 	
	html.end("center")
	if cif["_symmetry_space_group_name_H-M"].upper() in ["P 21","P21"]:
		html.element("p","\nLa détermination du groupe spatial s'est déroulée sans ambiguïté en raison de l'unique extinction systématique axiale mise en évidence le long de l'axe monoclinique.\n")
	elif cif["_symmetry_space_group_name_H-M"].upper() in ["P C","PC"]:
		html.element("p","\nLa détermination du groupe spatial s'est déroulée sans ambiguïté en raison de l'unique extinction systématique zonale mise en évidence perpendiculairement à l'axe monoclinique.\n")
	elif cif["_symmetry_space_group_name_H-M"].upper()=="C":
		html.element("p","\nLa détermination du groupe spatial s'est déroulée sans ambiguïté en raison de l'unique extinction systématique intégrale mise en évidence.\n")
	elif cif["_symmetry_space_group_name_H-M"].upper() in ["P 21 21 21","P212121"]:
		html.element("p","\nLa détermination du groupe spatial s'est déroulée sans ambiguïté en raison de la présence de trois extinctions systématiques détectées le long des axes principaux du cristal.\n")
	elif cif["_symmetry_space_group_name_H-M"].upper() in ["P 21/C","P21/C"]:
		html.element("p","\nLa détermination du groupe spatial s'est déroulée sans ambiguïté en raison de la présence d'une extinction systématique axiale le long de l'axe monoclinique associée à une extinction systématique zonale perpendiculaire à cet axe.\n")

	html.start("p")
	html.data("\nCompte tenu du nombre d'atomes appartenant à la molécule de %s et des paramètres de la maille élémentaire, il est déduit que cette maille doit contenir %s molécules de formule\n "%(cif["_chemical_name_common"],cif["_cell_formula_units_Z"]))
	html.rawdata(formula2chem(cif["_chemical_formula_moiety"]))
	html.data("\n ce qui correspond à une densité calculée de %s. Le nombre de réflexions collectées est de %s, parmi lesquelles %s ont été trouvées uniques.\n"%(cif["_exptl_crystal_density_diffrn"],cif["_diffrn_reflns_number"],cif["_reflns_number_total"] ))
	html.end("p")
	# et [[] ont été] considérées comme observées, une [bonne faible médiocre] équivalence par symétrie ayant été constaté [en raison de la taille réduite de l'échantillon].	

	
	html.start("h2")
	html.element("li","Affinement de la structure")
	html.end("h2")
	try:
		Ra=float(cif["_refine_ls_R_factor_all"])*100
		Ri=float(cif["_refine_ls_R_factor_gt"])*100
		wRa=float(cif["_refine_ls_wR_factor_ref"])*100
		wRi=float(cif["_refine_ls_wR_factor_gt"])*100
		R=min(Ra,Ri,wRa,wRi)
	except:
		R=100
	if R<5.5:
		txt="haute"
	elif R<7:
		txt="bonne"
	elif R<11:
		txt="moyenne"
	else :
		txt="mediocre"
	html.element("p","\nLa structure à été résolue par méthode directe à l'aide du programme SIR, les affinements par moindres carrés effectués grâce au programme SHELX ont permis d'aboutir à une structure de %s résolution, l'indice d'accord de référence atteignant la valeur %s %%. Les positions des atomes d'hydrogène ont été placées selon leurs coordonnées idéalisées et introduites, ainsi qu'une composante isotropique fonction de l'atome porteur, dans les calculs finaux des facteurs de structure.\n"%(txt,R))
	
	html.start("h2")
	html.element("li","\nDescription de la structure\n")
	html.end("h2")
	html.element("p","\nLe schéma 1, en annexe, présente la numérotation atomique, alors que les tables jointes en annexe consignent les paramètres expérimentaux et d'affinements, ainsi que les valeurs des distances et angles de liaisons.\n")
	
	html.end("ol")
	html.element("hr"," ")

def AbsStructEN(html,cif):
	"""Adds some text to the English report about the absolute configuration of the molecule
	@param html: HTML object where the text will be added to.
	@type html: XMLWrite object.
	@param cif: The CIF-object of the structure 
	@type cif: CIF-like Dictionnary
	@return: None, le test is simply added to the HTML file
	"""
	html.start("h2")
	html.element("li","\nAbsolute configuration\n")
	html.end("h2")
	html.start("p")
	if cif["_chemical_formula_sum"].find("S")>-1:
		txt="sulfur"
	elif cif["_chemical_formula_sum"].find("Cl")>-1:
		txt="chlorine"
	elif cif["_chemical_formula_sum"].find("Br")>-1:
		txt="bromine"
		
	else:
		txt="heavy"
	html.data("The %s molecule contains a %s atom that allows the absolute configuration to be determined, \
	making used of a high resolution data collection"%(cif["_chemical_name_common"],txt))
	if floatp(cif["_cell_measurement_temperature"])<280 : 
		html.data("	(performed at low temperature).")
	else:
		html.data(".")
	txt=""
	chiral=[]
	if exists(cif,"loop_"):
		for i in cif["loop_"]:
			if i[0][0].find("_atom_site_asymmetry_label")==0:
				chiral=i[1]
	for i in chiral:
		txt+=" %s: %s ;"%(i["_atom_site_asymmetry_label"],i["_atom_site_asymmetry_type"])
	if len(txt)>0:
		txt=txt[:-2]
		
	html.data(" The Flack x parameter is calculated based on the anomalous scattering method. \
	It gives the absolute structure, providing a sufficient estimate standard deviation is reached. \
	According to the theory, the expected values of the Flack x parameter are 0 for correct (within 3 esd.s) \
	and +1 for inverted absolute structure. The results considering the configuration  %s is %s, \
	which unambiguously proved this absolute configuration for %s."%(txt,cif["_refine_ls_abs_structure_Flack"],cif["_chemical_name_common"]))
	#html.data(txt)
	html.end("p")	

def structureImage(basename,structure="structure"):
	"""lauch PLATON and let the user chose the structural (or the ADP or powder) representation of the molecule
	@param basename: the name of the CIF-file without the extention
	@type basename: string
	@type structure: string
	@param structure: can be "powder" and "ADP", if not a simple structure is chosen
	@return None
	""" 

	if structure.lower()=="powder":
		txt=raw_input("I will now lauch PLATON and let you chose the simulated powder pattern of the molecule\nOnce you have selected a nice view, please click on «EPS» to export the drawing and quit.")
		while not os.path.isfile(basename+".ps"):
			i=os.popen("platon %s.cif"%(basename))
			for l in i.readlines(): print l.strip()
			i.close()
	else:
		txt=raw_input("I will now lauch PLATON and let you chose the %s representation of the molecule\nOnce you have selected a nice view, please click on «EPS» to export the drawing and quit."%structure)
		while not os.path.isfile(basename+".ps"):
			i,o=os.popen2("platon -o %s.cif"%(basename))
			if structure.lower()=="adp":
				i.write("plot adp\n")
			else:
				i.write("pluton\n")
			i.flush()
			i.write("menu on\n")
			i.flush()
			for l in o.readlines(): print l.strip()
			i.close()

	os.rename(basename+".ps","%s-%s.ps"%(basename,structure))
	print "Converting PostScript to PNG ... can take a while"
	inp=os.popen("convert -rotate 90 -quality 90 -geometry 2400x1800 %s-%s.ps %s-%s.png"%(basename,structure,basename,structure))
	for l in inp.readlines(): print l.strip()
	inp.close()
	if (not os.path.isfile("%s-%s.png"%(basename,structure)) and os.path.isfile("%s-%s.png.0"%(basename,structure))):
		workdir=os.path.dirname(basename)
		name=os.path.basename(basename)
		if len(workdir)==0:workdir="."
		dir1=os.listdir(workdir)
		dir2=[]
		for i in dir1:
			if i.find("%s-%s.png."%(name,structure))==0 : dir2.append(i)
		dir2.sort()
		os.rename(os.path.join(workdir,dir2[-1]),"%s-%s.png"%(basename,structure))
	print "Done !\n"+70*"_"




def BondLength(cif):
	"""Returns a dictionnary with all the bond lengths between heavy atoms. 
	Datas have to be already in the CIF
	@param cif: The CIF-object of the Xtal structure
	@type cif: dictionnary
	@return: a dictionnary with all the "A1 - A2": "distance"
	@rtype: dictionnary 
	"""
	BL={}
	for loop in cif["loop_"]:
		for key in loop[0]:
			if key=="_geom_bond_distance":
				for i in loop[1]: 
					BL[" %s - %s "%(i["_geom_bond_atom_site_label_1"],i["_geom_bond_atom_site_label_2"])]=i["_geom_bond_distance"]
	return BL

def BondAngle(cif):
	"""Returns a dictionnary with all the bond/valence angles between heavy atoms
	Datas have to be already in the CIF
	@param cif: The CIF-object of the Xtal structure
	@type cif: dictionnary
	@return: dictionnary with all the "A1 - A2 - A3":"Angle"
	@rtype: dictionnary
	"""
	BA={}
	for loop in cif["loop_"]:
		for key in loop[0]:
			if key=="_geom_angle":
				for i in loop[1]: 
					BA[" %s - %s - %s "%(i["_geom_angle_atom_site_label_1"],i["_geom_angle_atom_site_label_2"],i["_geom_angle_atom_site_label_3"])]=i["_geom_angle"]
	return BA
	



def AtomPositions(cif):
	"""Extract the atome name, position and U(eq) fropm the CIF.
	Each table contents the atome label + x, y and z coordinate and the U(eq)
	@param cif: The CIF-object of the Xtal structure
	@type cif: dictionnary
	@return: tupple of 2 tables, the first with the heavy atoms, the second with the hydrogens
	@rtype: tupple
	"""
	heavy=[]
	hydro=[]
	for loop in cif["loop_"]:
		for key in loop[0]:
			if key=="_atom_site_U_iso_or_equiv":
				for i in loop[1]: 
					atom=[]
					atom.append(i["_atom_site_label"])
					x=stringmulti(i["_atom_site_fract_x"],10000)
					y=stringmulti(i["_atom_site_fract_y"],10000)
					z=stringmulti(i["_atom_site_fract_z"],10000)
					U=stringmulti(i["_atom_site_U_iso_or_equiv"],1000)
					atom.append(x)
					atom.append(y)
					atom.append(z)
					atom.append(U)
					if i["_atom_site_type_symbol"]=="H":
						hydro.append(atom)
					else:
						heavy.append(atom)
	heavy.sort()
	hydro.sort()					
	return heavy,hydro
	
	

	



def dot2virg(text):
	""" Substitute the english dots with french virgules
	@param text: input test
	@type text: string
	@return: modified text
	@rtype: string
	"""
	return re.sub("\.",",",text)

def floatp(txt):
	"""Removes the () from the text and convert to a float 
	@param txt: the input test
	@type txt: string
	@return: the value of the txt
	@rtype: float
	"""
	#float(re.sub("\(","",re.sub("\)","",txt)))
	return float(txt.strip().split("(")[0])
	
	
def stringmulti(text,value):
	"""Convert a string to a real, multiplies by the value and returns a string
	@param text: input text
	@type text: string
	@type value: float or integer
	@return: txt*value
	@rtype: string 
	"""
	if "(" not in text: return str(float(text.strip().split("(")[0])*value)
	valuetxt,esdtxt=text.strip().split("(",1)
	l1=list(valuetxt)
	l1.reverse()
	l2=list(esdtxt.split(")",1)[0])
	l2.reverse()
	chiffres=[str(i) for i in range(10)]
	for i in range(len(l1)):
		if l1[i] in chiffres:
			if i<len(l2):
				l1[i]=l2[i]
			else:
				l1[i]="0"
		elif l1[i] in ["+","-"]:
			l1[i]="+"
	l1.reverse()
	esd=""
	for i in l1:esd+=str(i)	
#	esd="%8.2f"%(float(esd)*value)
	valuef="%s"%(float(valuetxt)*value)	
	esd2=""
	start=True
	for i in list("%s"%(float(esd)*value)):
		if  not i in ["0","."," "] or  not start :
			esd2+=i
			start=False
	if len(valuef)>2 and len(esd2)>2:
		if 	valuef[-2:]==".0" and esd2[-2:]==".0":
			valuef=valuef[:-2]
			esd2=esd2[:-2]	
	return "%s(%s)"%(valuef,esd2)

def formula2chem(txt):
	"""return a HTML representatin of the chemical formula"""
	out=""
	figu=[ str(x) for x in range(10)]
	for i in txt:
		if i in  figu:
			out+="<sub>%s</sub>"%i
#		elif i==" ":
#			continue
		else:
			out+=i
	return out

	
	


#
# SimpleXMLWriter
# $Id: SimpleXMLWriter.py 1862 2004-06-18 07:31:02Z Fredrik $
#
# a simple XML writer
#
# history:
# 2001-12-28 fl   created
# 2002-11-25 fl   fixed attribute encoding
# 2002-12-02 fl   minor fixes for 1.5.2
# 2004-06-17 fl   added pythondoc markup
#
# Copyright (c) 2001-2004 by Fredrik Lundh
#
# fredrik@pythonware.com
# http://www.pythonware.com
#
# --------------------------------------------------------------------
# The SimpleXMLWriter module is
#
# Copyright (c) 2001-2004 by Fredrik Lundh
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# and will comply with the following terms and conditions:
#
# Permission to use, copy, modify, and distribute this software and
# its associated documentation for any purpose and without fee is
# hereby granted, provided that the above copyright notice appears in
# all copies, and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of
# Secret Labs AB or the author not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
# ABILITY AND FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR
# BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
# --------------------------------------------------------------------

##
# Tools to write XML files, without having to deal with encoding
# issues, well-formedness, etc.
# <p>
# The current version does not provide built-in support for
# namespaces. To create files using namespaces, you have to provide
# "xmlns" attributes and explicitly add prefixes to tags and
# attributes.
#
# <h3>Patterns</h3>
#
# The following example generates a small XHTML document.
# <pre>
#
# from elementtree.SimpleXMLWriter import XMLWriter
# import sys
#
# w = XMLWriter(sys.stdout)
#
# html = w.start("html")
#
# w.start("head")
# w.element("title", "my document")
# w.element("meta", name="generator", value="my application 1.0")
# w.end()
#
# w.start("body")
# w.element("h1", "this is a heading")
# w.element("p", "this is a paragraph")
#
# w.start("p")
# w.data("this is ")
# w.element("b", "bold")
# w.data(" and ")
# w.element("i", "italic")
# w.data(".")
# w.end("p")
#
# w.close(html)
# </pre>
##

try:
    unicode("")
except NameError:
    def encode(s, encoding):
        # 1.5.2: application must use the right encoding
        return s
    _escape = re.compile(r"[&<>\"\x80-\xff]+") # 1.5.2
else:
    def encode(s, encoding):
        return s.encode(encoding)
    _escape = re.compile(eval(r'u"[&<>\"\u0080-\uffff]+"'))

def encode_entity(text, pattern=_escape):
    # map reserved and non-ascii characters to numerical entities
    def escape_entities(m):
        out = []
        for char in m.group():
            out.append("&#%d;" % ord(char))
        return string.join(out, "")
    return encode(pattern.sub(escape_entities, text), "ascii")


del _escape


def escape_cdata(s, encoding=None, replace=string.replace):
    s = replace(s, "&", "&amp;")
    s = replace(s, "<", "&lt;")
    s = replace(s, ">", "&gt;")
    if encoding:
        try:
            return encode(s, encoding)
        except UnicodeError:
            return encode_entity(s)
    return s

def escape_attrib(s, encoding=None, replace=string.replace):
    s = replace(s, "&", "&amp;")
    s = replace(s, "'", "&apos;")
    s = replace(s, "\"", "&quot;")
    s = replace(s, "<", "&lt;")
    s = replace(s, ">", "&gt;")
    if encoding:
        try:
            return encode(s, encoding)
        except UnicodeError:
            return encode_entity(s)
    return s

##
# XML writer class.
#
# @param file A file or file-like object.  This object must implement
#    a <b>write</b> method that takes an 8-bit string.
# @param encoding Optional encoding.

class XMLWriter:

    def __init__(self, file, encoding="us-ascii"):
        self.__write = file.write
        self.__open = 0 # true if start tag is open
        self.__tags = []
        self.__data = []
        self.__encoding = encoding

    def __flush(self):
        if self.__open:
            self.__write(">")
            self.__open = 0
        if self.__data:
            data = string.join(self.__data, "")
            self.__write(escape_cdata(data, self.__encoding))
            self.__data = []

    ##
    # Opens a new element.  Attributes can be given as keyword
    # arguments, or as a string/string dictionary. You can pass in
    # 8-bit strings or Unicode strings; the former are assumed to use
    # the encoding passed to the constructor.  The method returns an
    # opaque identifier that can be passed to the <b>close</b> method,
    # to close all open elements up to and including this one.
    #
    # @param tag Element tag.
    # @param attrib Attribute dictionary.  Alternatively, attributes
    #    can be given as keyword arguments.
    # @return An element identifier.

    def start(self, tag, attrib={}, **extra):
        self.__flush()
        tag = escape_cdata(tag, self.__encoding)
        self.__data = []
        self.__tags.append(tag)
        self.__write("<%s" % tag)
        if attrib or extra:
            attrib = attrib.copy()
            attrib.update(extra)
            attrib = attrib.items()
            attrib.sort()
            for k, v in attrib:
                k = escape_cdata(k, self.__encoding)
                v = escape_attrib(v, self.__encoding)
                self.__write(" %s=\"%s\"" % (k, v))
        self.__open = 1
        return len(self.__tags)-1

    ##
    # Adds a comment to the output stream.
    #
    # @param comment Comment text, as an 8-bit string or Unicode string.

    def comment(self, comment):
        self.__flush()
        self.__write("<!-- %s -->\n" % escape_cdata(comment, self.__encoding))

    def rawdata(self, comment):
        """insert raw HTML data to the XML-file
		"""
        self.__flush()	
        self.__write("%s" %(comment))
    ##
    # Adds character data to the output stream.
    #
    # @param text Character data, as an 8-bit string or Unicode string.

    def data(self, text):
        """insert text data to the XML-file"""
        self.__data.append(text)

    ##
    # Closes the current element (opened by the most recent call to
    # <b>start</b>).
    #
    # @param tag Element tag.  If given, the tag must match the start
    #    tag.  If omitted, the current element is closed.

    def end(self, tag=None):
        if tag:
            assert self.__tags, "unbalanced end(%s)" % tag
            assert escape_cdata(tag, self.__encoding) == self.__tags[-1],\
                   "expected end(%s), got %s" % (self.__tags[-1], tag)
        else:
            assert self.__tags, "unbalanced end()"
        tag = self.__tags.pop()
        if self.__data:
            self.__flush()
        elif self.__open:
            self.__open = 0
            self.__write(" />")
            return
        self.__write("</%s>" % tag)

    ##
    # Closes open elements, up to (and including) the element identified
    # by the given identifier.
    #
    # @param id Element identifier, as returned by the <b>start</b> method.

    def close(self, id):
        while len(self.__tags) > id:
            self.end()

    ##
    # Adds an entire element.  This is the same as calling <b>start</b>,
    # <b>data</b>, and <b>end</b> in sequence. The <b>text</b> argument
    # can be omitted.

    def element(self, tag, text=None, attrib={}, **extra):
        apply(self.start, (tag, attrib), extra)
        if text:
            self.data(text)
        self.end()
	
def renamefile(infile,namelist):
	"""
	The CSD database has only room for 8 char to define the reference of the molecule.
	This function just tries to find a coherent name for the molecule in the database :
	it uses the 6 first numbers of the molecule name then "-" or a letter depending if the Xtal is a base or a
	salt (the letter corresponding to the number of the salt)
	The 8th position is for the polymorph or the data-acquisition.
	
	Afterwars it asks the user for the name, provinding a suggestion.
	 
	@param infile: name of the CIF file
	@type infile: string
	@param namelist: list of all the files that already exists
	@type namelist: list 
	@return: the name of the reference suggested by the program
	@rtype:string
	
	"""
	figures=[str(x) for x in range(10)]
	letters=[chr(x) for x in range(65,91)]
	ref=""
	sel=""
	if 	infile[:2].upper().find("SR")==0:
		for i in infile[2:9].upper():
			if i in figures:
				if len(ref)>=6: continue
				ref+=i
			if i in letters:
				sel+=i
				break
			if i in[".","-","_"]:
				break
	elif 	infile[:3].upper().find("SSR")==0:
		for i in infile[3:10].upper():
			if i in figures:
				if len(ref)>=6: continue
				ref+=i
			if i in letters:
				sel+=i
				break
			if i in[".","-","_"]:
				break
	elif 	infile[:2].upper().find("SL")==0:
		if len(infile)>12:
			try:
				if float(infile[10:12])>0:sel="A"
			except:
				sel=""	
		for i in infile[2:9].upper():
			if i in figures:
				if len(ref)>=6: continue
				ref+=i
			if i in letters:
				sel+=i
				break
	elif (infile[7] in figures) and (infile[6].upper() in letters+["-"]):
		a=0
		for i in infile[:6].upper():
			if i in figures : a+=1
		if a>5: return infile
	else:
		ref=infile[:6]
		sel=""
				
	while len(ref)<6:
		ref="0"+ref
	if sel=="":sel="-"
	name=ref+sel
	count=1
	for i in namelist:
		if i.find(name)==0:count+=1
	name+=str(count)
	
	print "I suggest using %s as reference for the database for file %s"%(name,infile)
	while True:
		txt=raw_input(" Database reference (<= 8 characters) [%s]-->"%name)
		if len(txt)==0:
			break
		if len(txt)<=8:
		 	name=txt
			break
	if name[-1]=="?":
		count=1
		name=name[:-1]
		for i in namelist:
			if i.find(name)==0:count+=1
		name+=str(count)
		print "using "+name

	return name+".cif"		
				

def MergeSg(name,kcd,sg):
	""" Merge 2 cif objects : add from sg the missing values in kcd
	@param name: the name of the molecule, used only if the value exist in kcd
	@type name: string
	@param kcd: The CIF-object of the Xtal structure 
	@type kcd: dictionnary
	@param sg: The CIF-object of the Xtal structure 
	@type sg: dictionnary
	@return: a new cif-object
	@rtype: dictionnary 
	"""
	DoNotMerge=["loop_","_chemical_formula_weight","_chemical_formula_moiety","_chemical_formula_sum"]  
	if not exists(kcd,"_chemical_name_common"):
		kcd["_chemical_name_common"]=name
	for i in sg:
		if i in DoNotMerge: continue
		if not exists(kcd,i):
			kcd[i]=sg[i]
	w,cif=CheckSym(kcd,True)
	if len(w)==0:
			w="OK"
	print "Checking for symmetry : \n%s"%w			
	return cif
	
if __name__=='__main__':
	if sys.argv[0].lower().split("/")[-1]=="cif2csd":
		if len(sys.argv)==2: 
			filename=sys.argv[1]
			outfile=filename[:-4]+"-process.cif"
		elif len(sys.argv)==3:
			filename=sys.argv[1]
			outfile=sys.argv[2]
		else:
			raise "Please enter the name of CIF file to process"
			sys.exit(1)
		cif=LoadCIF(filename)
		w,cif2=CheckSym(cif,True)
		if len(w)==0:
			w="OK"
		print "Checking for symmetry : \n%s"%w	
		print "Checking for the data needed to enter them to the Database"
		
		cif,mod=CheckForCSD(cif2,name=filename)
		if not mod: print "OK"
		if mod or len(w)>0:
			outfile=raw_input("Please enter the name of the file where to save the CIF data -->")
			if len(outfile)>0:
				if outfile[-4:].lower()!=".cif":outfile+=".cif"
				SaveCIF(cif,outfile)
	elif sys.argv[0].lower().split("/")[-1]=="checkall2csd":
		infiles=[]
		table={}
		for i in os.listdir("."):
			if i[-4:].lower()==".cif":infiles.append(i)
		infiles.sort()
		if os.path.isfile("ConversionTable"):
			print "Loading the Conversion Table"
			f=open("ConversionTable","r")
			ct=f.readlines()
			f.close()
			for i in ct:
				j=i.split(None,1)
				table[j[0].strip()]=j[1].strip()
		print "Processing all the files : ",infiles
		if not os.path.isdir("process"):
			os.mkdir("process")
		for filename in infiles:
			print "Processing file : ",filename

			if table.has_key(filename):
				outfile=table[filename]
			else :
				outfile=renamefile(filename,table.values())
				table[filename]=outfile
			if os.path.isfile(os.path.join("./process",outfile)):
				print "The destination file exists",os.path.join("./process",outfile)
				print "###########################################################"
				continue
			cif=LoadCIF(filename)
			w,cif2=CheckSym(cif,True)	
			if len(w)==0:
				w="OK"
			print "Checking for symmetry : \n%s"%w		
			cif2["_database_code_CSD"]=outfile[:-4]
#			print "Checking for the data needed to enter them to the Database"
			cif,mod=CheckForCSD(cif2,name=filename)
			if not mod: print "OK"

			print "Saving the Conversion Table"
			f=open("ConversionTable","w")
			for i in table:
				f.write("%s	%s\n"%(i,table[i]))
			f.close()	
			print "###########################################################"

			if outfile[-4:].lower()!=".cif":outfile+=".cif"
			SaveCIF(cif,"process/"+outfile)
	elif sys.argv[0].lower().split("/")[-1]=="report":
		if len(sys.argv)==2: 
			filename=sys.argv[1]
			outfile=filename[:-4]+"-process.cif"
		elif len(sys.argv)==3:
			filename=sys.argv[1]
			outfile=sys.argv[2]
		else:
			raise "Please enter the name of CIF file to process"
			sys.exit(1)
		cif=LoadCIF(filename)
		
		w,cif2=CheckSym(cif,True)
		if len(w)==0:
			w="OK"
		print "Checking for symmetry : \n%s"%w	
		print "Completing the CIF file with the data generated by PLATON"
		cif3=mergeplaton(cif2,platon(filename))
		print "Checking for the data needed to generate a report"
		cif,mod=CheckForRST(cif3)
		if not mod: print "OK"
		WriteReport(filename,cif,Lang="En")
	elif sys.argv[0].lower().split("/")[-1]=="fixallsym":
		print "Doing a trivial rewrite with symmetry check"
		infiles=[]
		for i in os.listdir("."):
			if i[-4:].lower()==".cif":infiles.append(i)
		infiles.sort()
		print "Processing all the files : ",infiles
		for filename in infiles:
			print "Processing file : ",filename
			cif=LoadCIF(filename)
			w,cif2=CheckSym(cif,True)	
			SaveCIF(cif,filename)
	elif sys.argv[0].lower().split("/")[-1]=="checksym":
		if len(sys.argv)==2: 
			filename=sys.argv[1]
			outfile=filename[:-4]+"-process.cif"
		elif len(sys.argv)==3:
			filename=sys.argv[1]
			outfile=sys.argv[2]
		else:
			raise "Please enter the name of CIF file to process"
			sys.exit(1)
#		print "Doing a trivial rewrite with symmetry check on file : %s to %s"%(filename,outfile)
#		cif=LoadCIF(filename)
		cif=LoadCIF(filename)
		w,cif2=CheckSym(cif,True)
		if len(w)==0:
			w="OK"
		print "Checking for symmetry : %s ... %s -> %s"%(w,filename,outfile)	
		SaveCIF(cif,outfile)
		
	else:
		print "What do you want me to do ?"
#	print "Done"
