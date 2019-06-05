from private import Keys
from collections import namedtuple


class Station(Keys):

	def __init__(self,email):
		super().__init__()
		self.email = email
		self.station = namedtuple('station','franchisor name streetAddress city department numOfTanks')

	def user(self):
		self.refresh_db()
		command = 'SELECT station_id FROM userStation INNER JOIN users ON(userStation.user_id = users.id) WHERE users.email = \''+self.email+'\''

		
		self.cursor.execute(command)
		self.user_ids = self.cursor.fetchall()
		if not self.user_ids:
			self.db.close()
			return False
		self.db.close()
		return self.user_ids

	def create(self, stationInfo = None):
		#1) takes in the station information
		#2) takes the tank information
		station_data = self.station._make(tuple(stationInfo))
		command = "INSERT INTO station (franchisor,name,streetAddress,city,department,numOfTanks) VALUES(%s,%s,%s,%s,%s,%s)"
		values = (station_data.franchisor,
					station_data.name,
					station_data.streetAddress,
					station_data.city,
					station_data.department,
					station_data.numOfTanks)
		cursor = self.db.cursor()
		cursor.execute(command,values)
		self.db.commit()
		self.info(station_data.name)
		

	def info(self,stationName):
	#1) adds the information for the station such as address, city, department, numOfTanks
		self.refresh_db()
		self.stationName = stationName
		command = "SELECT * FROM station WHERE name = \'"+self.stationName+"\'"
		cursor = self.db.cursor()
		cursor.execute(command)
		results = cursor.fetchall()
		self.stationId = results[0][0]
		for result in results:
			station_data = self.station._make(tuple(result[1:]))

		self.franchisor = station_data.franchisor
		self.streetAddress = station_data.streetAddress
		self.city = station_data.city
		self.department = station_data.department
		self.numOfTanks = station_data.numOfTanks
		self.db.close()




if __name__ == '__main__':
	station = Station('vincentturnier@gmail.com')
	print(station.user())
	station.info('Vinny')
	print(station.city)
