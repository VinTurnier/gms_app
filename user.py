from herokuappRequest import app
from collections import namedtuple
import mysql.connector
from private import Keys

class User:

	def __init__(self):
		self.is_loggedin = False

	def login(self,email,password):
		gms = app()
		if gms.login(email,password)!='er0110':
			self.profile = gms.login(email,password)
			self.is_loggedin = True
			return self.is_loggedin
		else:
			return gms.login(email,password)

	def create(self, profile = None):
		self.refresh_db()
		user = namedtuple('user','first_name last_name email phone password')
		new_user = user._make(profile)
		gms = app()
		gms_create = gms.create(new_user.email,new_user.password)
		if gms_create!='er0010':
			values = (gms.getId,new_user.first_name,new_user.last_name,new_user.phone)
			command = 'INSERT INTO profile (user_id,first_name, last_name, phone) VALUES (%s,%s,%s,%s)'
			self.cursor.execute(command,values)
			self.db.commit()
			self.db.close()
			return True
		else:
			return gms_create

	def info(self):
		if self.is_loggedin:
			self.refresh_db()
			command = "SELECT profile.user_id,\
					   profile.first_name, \
					   profile.last_name,\
					   profile.phone,\
					   users.email \
					   FROM profile JOIN users ON(profile.user_id = users.id) \
					   WHERE user_id = \'"+str(self.profile['id'])+"\'"


			
			self.cursor.execute(command)
			user_info = self.cursor.fetchall()
			self.id = user_info[0][0]
			self.first_name = user_info[0][1]
			self.last_name = user_info[0][2]
			self.phone = user_info[0][3]
			self.email = user_info[0][4]
			command = "SELECT station.name\
					 FROM userStation JOIN station \
					 ON (userStation.station_id = station.id) \
					 WHERE user_id = "+str(self.id)
			self.cursor.execute(command)
			self.stations = []
			station_names = self.cursor.fetchall()
			for i in range(len(station_names)):
				self.stations.append(station_names[i][0])
			
			
	def add_station(self,station_id):
		command = "INSERT INTO userStation (user_id, station_id) VALUES (%s,%s)"
		values = (self.id,station_id)
		cursor = self.db.cursor()
		cursor.execute(command,values)
		self.db.commit()



	def refresh_db(self):
		key = Keys()
		self.db = mysql.connector.connect(host = key.mysql_host,
                                        user = key.mysql_user,
                                        passwd = key.mysql_password,
                                        database = key.mysql_database)
		self.cursor = self.db.cursor()


if __name__ == '__main__':
	user = User()
	print(user.login('usertest12@gmail.com','123456789'))
	print(user.info())
	print(user.stations)
	
