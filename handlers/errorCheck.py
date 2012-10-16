import databaseOperations
import re
import hashlib

def checkLogin(username, password):
	if (username, password) == (None, None):
		return "Username and Password were left empty"
	elif username == None:
		return "Username was left empty"
	elif password == None:
		return "Password was left empty"
	else:
		hashedPwd = hashlib.sha512(password).hexdigest()
		return databaseOperations.checkLogin(username, hashedPwd)
		
def checkRegister(email, username, password):

	if email == None or username == None or password == None:
		return "All the details marked with a * must be filled"
	elif not checkEmail(email):
		return "Email address is not valid"
	else:
		return databaseOperations.checkRegister(email, username)
		
def checkEmail(email):
	pattern = r'\w+@\w+\.\w'
	return re.match(pattern, email)
	
def checkChangePassword(username, cpassword, npassword, rnpassword):
	if cpassword == None or npassword == None or rnpassword == None:
		return "Some of the fields were left blank"
	elif not databaseOperations.login(username, hashlib.sha512(cpassword).hexdigest()):
		return "Wrong current password entered"
	elif npassword != rnpassword:
		return "The new password was not repeated correctly"
	else:
		return None
