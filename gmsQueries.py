from private import Keys
from collections import namedtuple


class Query(Keys):

	def __init__(self):
		super().__init__()

	def displayCRX(self,id_citern):
		self.refresh_db()
		command = "SELECT * FROM crx WHERE idCitern = \'"+id_citern+"\'"
		self.cursor.execute(command)
		results = self.cursor.fetchall()
		if results == []:
			return 'error' #error code not described yet
			self.db.close()
		else:
			self.db.close()
			return results[0]


	def measurements(self, station_id, measurements = None):
	#1) collects the measurements
	#2) Adds them to the database
		self.refresh_db()
		command = "SELECT id FROM fuelDeposit WHERE station_id = \'"+str(station_id)+"\'"
		self.cursor.execute(command)
		id = self.cursor.fetchall()
		fuelDeposit_id = id[len(id)-1][0]

		command = "INSERT INTO measurements (station_id, fuelDeposit_id, compt, fuelType, rHeight, dHeight) VALUES (%s,%s,%s,%s,%s,%s)"


		for measurement in measurements:
			if 'N/A' in measurement:
				continue
			else:
				values = tuple([station_id, fuelDeposit_id]+measurement)
				self.cursor.execute(command,values)
				self.db.commit()
		self.db.close()
		return True


	def fuelDeposit(self, fuelDeposit_data = None):
		self.refresh_db()
		FuelDeposit = namedtuple('FuelDeposit','station_id id_citern date_added')
		fuelDeposit_data = FuelDeposit._make(tuple(fuelDeposit_data))

		command = "INSERT INTO fuelDeposit(station_id, idCitern, date_added) VALUES (%s,%s,%s)"
		if '' in fuelDeposit_data:
			self.db.close()

			return 'er0000'
		else:
			values = (fuelDeposit_data.station_id,
						fuelDeposit_data.id_citern,
						fuelDeposit_data.date_added)
			self.cursor.execute(command,values)
			self.db.commit()
			self.db.close()



	def inventory(self, inventoryData = None):
	#1) checks the inventory
	#2) add data to the database
		self.refresh_db()
		command = "INSERT INTO inventory (station_id, tank_id, stockBoD, fuelDeposit, sales, stockEoD, date_added) VALUES (%s,%s,%s,%s,%s,%s,%s)"
		if "N/A" in inventoryData:
			self.db.close()
			return 'er0000'
		else:
			values = tuple(inventoryData)
			self.cursor.execute(command,values)
			self.db.commit()
			self.db.close()

	def displayData(self, station_id,table, periods=''):
	#1) displays the information base on the critaria
		self.refresh_db()
		period = {"1 Day":"1 DAY",
					"5 Days": "5 DAY",
					"1 Month": "1 MONTH",
					"3 Months": "3 MONTH",
					"6 Months": "6 MONTH",
					"1 Year": "1 YEAR",
					"5 Years": "5 YEAR",
					"All": "100 YEAR"}

		tables = {'CRX':'SELECT * FROM crx',
						'Measurements': ' SELECT measurements.compt, \
						measurements.fuelType, \
						measurements.rHeight, \
						measurements.dheight, \
						fuelDeposit.date_added \
						FROM measurements \
						JOIN fuelDeposit \
						ON (measurements.fuelDeposit_id = fuelDeposit.id) \
						WHERE fuelDeposit.station_id = \''+str(station_id)+'\' \
						AND date_added BETWEEN(CURDATE() - INTERVAL '+period[periods]+') AND CURDATE()\
						ORDER BY fuelDeposit.date_added DESC',
				'Inventory': 'SELECT tank.name, \
							inventory.stockBoD, \
							inventory.fuelDeposit, \
							inventory.sales, \
							inventory.stockEoD, \
							inventory.date_added \
							FROM tank JOIN inventory \
							ON (tank.id = inventory.tank_id) \
							WHERE tank.station_id = \''+str(station_id)+'\' \
							AND date_added BETWEEN(CURDATE() - INTERVAL '+period[periods]+') AND CURDATE()\
							ORDER BY inventory.date_added DESC',
				'Fuel Deposit': 'SELECT fuelDeposit.idCitern, \
						truckCapacity.crx1+truckCapacity.crx2\
						+truckCapacity.crx3+truckCapacity.crx4+truckCapacity.crx5 \
						AS "Expected Deposit", \
						fuelDeposit.date_added \
						FROM fuelDeposit JOIN truckCapacity \
						ON (truckCapacity.id_citern = fuelDeposit.idCitern)\
						WHERE station_id = \''+str(station_id)+'\' \
						AND date_added BETWEEN(CURDATE() - INTERVAL '+period[periods]+') AND CURDATE()\
						ORDER BY fuelDeposit.date_added DESC'}


		self.tableHeader = {"CRX": ("ID Citern","CRX1","CRX2","CRX3","CRX4","CRX5","Eperation Date"),
							"Inventory": ("Tank Name","StockBoD","Fuel Deposit","Sales","StockEoD","Date"),
							"Measurements": ("Compartement","Tank","Recieved Height","Deposit Height","Date"),
							"Fuel Deposit": ("ID Citern","Expected (Gal)","Date")}

		command = tables[table]
		self.cursor.execute(command)
		data = self.cursor.fetchall()
		self.db.close()
		return data


