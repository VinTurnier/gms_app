

class Query:

	def __init__(self):
		pass

	def displayCRX(self,id_citern):
		command = "SELECT * FROM crx WHERE idCitern = \'"+id_citern+"\'"
		cursor = self.db.cursor()
		cursor.execute(command)
		results = cursor.fetchall()
		if results == []:
			return 'error' #error code not described yet

		else:
			return results[0]


	def measurements(self, station_id, measurements = None):
	#1) collects the measurements
	#2) Adds them to the database

		command = "SELECT id FROM fuelDeposit WHERE station_id = \'"+str(station_id)+"\'"
		cursor = self.db.cursor()
		cursor.execute(command)
		id = cursor.fetchall()
		fuelDeposit_id = id[len(id)-1][0]

		command = "INSERT INTO measurements (station_id, fuelDeposit_id, compt, fuelType, rHeight, dHeight) VALUES (%s,%s,%s,%s,%s,%s)"


		na_count = 0
		for measurement in measurements:
			if "N/A" in measurement:
				na_count +=1

		for measurement in measurements:
			if na_count!=5:
				values = tuple([station_id, fuelDeposit_id]+measurement)
				cursor.execute(command,values)
				self.db.commit()
				return True
			else:
				return 'er0000'

	def fuelDeposit(self, fuelDeposit_data = None):
		FuelDeposit = namedtuple('FuelDeposit','station_id id_citern date_added')
		fuelDeposit_data = FuelDeposit._make(tuple(fuelDeposit_data))

		command = "INSERT INTO fuelDeposit(station_id, idCitern, date_added) VALUES (%s,%s,%s)"
		if '' in fuelDeposit_data:
			return 'er0000'
		else:
			values = (fuelDeposit_data.station_id,
						fuelDeposit_data.id_citern,
						fuelDeposit_data.date_added)
			cursor = self.db.cursor()
			cursor.execute(command,values)
			self.db.commit()


	def inventory(self, inventoryData = None):
	#1) checks the inventory
	#2) add data to the database
		command = "INSERT INTO inventory (station_id, tank_id, stockBoD, fuelDeposit, sales, stockEoD, date_added) VALUES (%s,%s,%s,%s,%s,%s,%s)"
		if "N/A" in inventoryData:
			return 'er0000'
		else:
			values = tuple(inventoryData)
			cursor = self.db.cursor()
			cursor.execute(command,values)
			self.db.commit()

	def displayData(self, table, periods=''):
	#1) displays the information base on the critaria
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
						WHERE fuelDeposit.station_id = \''+str(self.stationId)+'\' \
						AND date_added BETWEEN(CURDATE() - INTERVAL '+period[periods]+') AND CURDATE()',
				'Inventory': 'SELECT tank.name, \
							inventory.stockBoD, \
							inventory.fuelDeposit, \
							inventory.sales, \
							inventory.stockEoD, \
							inventory.date_added \
							FROM tank JOIN inventory \
							ON (tank.id = inventory.tank_id) \
							WHERE tank.station_id = \''+str(self.stationId)+'\' \
							AND date_added BETWEEN(CURDATE() - INTERVAL '+period[periods]+') AND CURDATE()',
				'Fuel Deposit': 'SELECT fuelDeposit.idCitern, \
						truckCapacity.crx1+truckCapacity.crx2\
						+truckCapacity.crx3+truckCapacity.crx4+truckCapacity.crx5 \
						AS "Expected Deposit", \
						fuelDeposit.date_added \
						FROM fuelDeposit JOIN truckCapacity \
						ON (truckCapacity.id_citern = fuelDeposit.idCitern)\
						WHERE station_id = \''+str(self.stationId)+'\' \
						AND date_added BETWEEN(CURDATE() - INTERVAL '+period[periods]+') AND CURDATE()'}


		self.tableHeader = {"CRX": ("ID Citern","CRX1","CRX2","CRX3","CRX4","CRX5","Eperation Date"),
							"Inventory": ("Tank Name","StockBoD","Fuel Deposit","Sales","StockEoD","Date"),
							"Measurements": ("Compartement","Fuel Type","Recieved Height","Deposit Height","Date"),
							"Fuel Deposit": ("ID Citern","Expected (Gal)","Date")}

		command = tables[table]
		cursor = self.db.cursor()
		cursor.execute(command)
		return cursor.fetchall()


	def refresh_db(self):
		key = Keys()
		self.db = mysql.connector.connect(host = key.mysql_host,
                                        user = key.mysql_user,
                                        passwd = key.mysql_password,
                                        database = key.mysql_database)
		self.cursor = self.db.cursor()

