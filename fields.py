import re
from collections import namedtuple
from user import User
from private import Keys
class Field(Keys):

	def __init__(self):
		super().__init__()


	def check(self, data = None):
		data_check = namedtuple('data_check','first_name last_name email phone password password2')
		data_to_check = data_check._make(tuple(data))
		err_arr = [self.name(data_to_check.first_name),
				   self.name(data_to_check.last_name),
				   self.email(data_to_check.email),
				   self.phone(data_to_check.phone,output=True),
				   self.verify_password(data_to_check.password,data_to_check.password2)]
		error = self.error(err_arr)
		emp = self.empty(err_arr)
		if error == False and emp == False:
			user = User()
			data_checked = [data_to_check.first_name,
							data_to_check.last_name,
							data_to_check.email,
							data_to_check.phone,
							data_to_check.password]
			user.create(data_checked)
			return True
		else:
			return error


	def verify_password(self,password1,password2):
		if(password2==password1):
			return password1
		else:
			return 'er0101'

	def phone(self, phoneNumber, country_code = '+509',output = False):
        # 1) Identify phone number
        # 2) returns a boolean value or the country code and phone number
        #    The default value returns a boolean value
		Phone = namedtuple('Phone','country_code exchange_num subscribers_num')
		phone_number = re.findall(r'(\+?\d{1,3})?[-. \S]*?(\d{4})[-. \S]*?(\d{4})',phoneNumber) #(1)
		if not phone_number:
			return 'er0011' #(2)
		else:
		    if output:
		        phone = Phone._make(phone_number[0])
		        return phone.exchange_num+phone.subscribers_num #(2)
		    else:
		        return True     #(2)

	def email(self, email):
	    # 1) Checks to see if the email field is properly entered
	    self.refresh_db()
	    emailCheck = re.findall(r'@\w*?\.[a-z]*',email) #(1)
	    if not emailCheck:
	        return 'er0001'    #returning False means email field fails check
	    else:
	        # 2) Checks to see if email already exist in database
	        #    if it does pop up window opens up warning the user that the email is
	        #    already registered
	        command = 'SELECT * FROM users WHERE email = \''+email+'\''
	        self.cursor.execute(command)
	        user_data = self.cursor.fetchall()
	        self.db.close()
	        if not user_data:
	        	return email
	        else:
	        	return 'er0010'

	def name(self,text):
		#checks to see if the name does not have non alphabetical characters
		# returns returns the name else an error
		name = re.findall(r'[a-zA-Z]+[\D]',text)
		if self.empty(name) == False and len(name) <=1:
			return name[0].capitalize()
		else:
			# er0111: name cannot have non alphabetic characters
			return 'er1111'

	def station_name(self,name):
		self.refresh_db()
		command ="SELECT name FROM station WHERE name =\'"+name+"\'"
		self.cursor.execute(command)
		names = self.cursor.fetchall()
		if not names:
			return name
		else:
			return 'er0111'

	def error(self,error = None):
		# 1) will take as input a single error or a list of errors
        # 2) each error will be Identified by a four digit error code
        #       Error Code =    er0000: Empty Field
        #                       er0001: Enter an Email in Email Field
        #                       er0010: Email already Exists
        #                       er0011: Enter Valid Phone number
        #                       er0100: Username already Exists
        #                       er0101: Password does not match
        #                       er0110: Username or password do not match
        #						er0111: name contains non-alphabetical characters
        #						er1111: First name or last name cannot contain non-alphabetical characters

		errors = ['er0001','er0010','er0011','er0100','er0101','er0110','er1111','er0111']
		for i in error:
			if i in errors:
				return i
		return False

	def empty(self,data = None):
		# array has empty field
		if '' in data:
			return True
		else:
			return False


if __name__ == '__main__':
	field = Field()
	user_profile = ['user','test','usertest1134@gmail.com','37011002','123456789','123456789']
	print(field.check(user_profile))
	print(field.station_name('Vinny'))


