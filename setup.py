#!/usr/bin/env python3

import os
import subprocess as sp

# If Windows
if(os.name == 'nt'):
	proc = sp.Popen(["powershell.exe", "pip -V"], stdout=sp.PIPE, shell=True, universal_newlines=True)
	out = proc.communicate()[0]

# If Linux or Mac
else:
	proc = sp.Popen(["pip -V"], stdout=sp.PIPE, shell=True, universal_newlines=True)
	out = proc.communicate()[0]

# Python is installed
if(len(out.split("python"))>1):
	# Python3 installed as default
	if(out.split("python ")[1][0] == "3"):
		os.system("pip install colorama")
		os.system("pip install numpy")
		os.system("pip install sklearn")
		os.system("pip install scikit-learn")
		os.system("pip install pandas")

	# Python2 installed as default
	else:
		proc = sp.Popen(["powershell.exe", "pip3 -V"], stdout=sp.PIPE, shell=True, universal_newlines=True)
		out = proc.communicate()[0]
		# Python3 is installed too
		if(len(out.split("python"))>1):
			os.system("pip3 install colorama")
			os.system("pip3 install numpy")
			os.system("pip3 install sklearn")
			os.system("pip install scikit-learn")
			os.system("pip3 install pandas")
		else:
			print("Only Python2 is installed. Make sure to install Python3's latest version!")

# Python not Installed
else:
	print("Python is not installed. Make sure to install the latest version of Python 3!")

