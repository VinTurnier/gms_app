
from private import Keys
from collections import namedtuple

class Tank(Keys):
	tank = namedtuple('tank','name capacity diameter length thickness')

	def __init__(self,station_id):
		super().__init__()
		self.station_id = station_id
		

	def create(self,tankInfo = None):
		self.refresh_db()
		command = "INSERT INTO tank(station_id,name,capacity,diameter,length,thickness) VALUES(%s,%s,%s,%s,%s,%s)"
		for tank in tankInfo:
			tank_data = self.tank._make(tuple(tank))
			value = (self.station_id,
					tank_data.name,
					tank_data.capacity,
					tank_data.diameter,
					tank_data.length,
					tank_data.thickness)
			self.cursor.execute(command,value)
			self.db.commit()
		self.db.close()
	def info(self,tankName):
		if tankName == "N/A":
			return 'er0000'
		else:
			command = "SELECT * FROM tank WHERE station_id = \'"+str(self.station_id)+"\' AND name = \'"+tankName+"\'"
			self.cursor.execute(command)
			tank_info = cursor.fetchall()
			self.tank_id = tank_info[0][0]
			self.capacity = tank_info[0][3]
			self.diameter = tank_info[0][4]
			self.length = tank_info[0][5]
			self.thickness = tank_info[0][6]
		self.db.close()


