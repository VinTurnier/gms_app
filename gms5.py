from collections import namedtuple
from PyQt5 import QtCore, QtGui, QtWidgets
import gmsMainWindow
import mysql.connector
import hashlib, binascii, os
import re
from datetime import date

# GMS Modules
import user
import fields
import station
import gmsQueries
from private import Keys


class Tank:
    tank = namedtuple('tank','name capacity diameter length thickness')

    def __init__(self,station_id):
        key = Keys()
        self.station_id = station_id
        self.tankName = None
        self.tank_id = None
        self.capacity = None
        self.diameter = None
        self.length = None
        self.thickness = None
        self.db = mysql.connector.connect(host = key.mysql_host,
                                        user = key.mysql_user,
                                        passwd = key.mysql_password,
                                        database = key.mysql_database)

    def create(self,tankInfo = None):
        command = "INSERT INTO tank(station_id,name,capacity,diameter,length,thickness) VALUES(%s,%s,%s,%s,%s,%s)"
        cursor = self.db.cursor()
        for tank in tankInfo:
            tank_data = self.tank._make(tuple(tank))
            value = (self.station_id,
                     tank_data.name,
                     tank_data.capacity,
                     tank_data.diameter,
                     tank_data.length,
                     tank_data.thickness)
            cursor.execute(command,value)
            self.db.commit()

    def info(self,tankName):
        if tankName == "N/A":
            return 'er0000'
        else:
            command = "SELECT * FROM tank WHERE station_id = \'"+str(self.station_id)+"\' AND name = \'"+tankName+"\'"
            cursor = self.db.cursor()
            cursor.execute(command)
            tank_info = cursor.fetchall()
            self.tank_id = tank_info[0][0]
            self.capacity = tank_info[0][3]
            self.diameter = tank_info[0][4]
            self.length = tank_info[0][5]
            self.thickness = tank_info[0][6]

class gmsMain:
    error = {'er0000':"Please make sure that all text field are filled with the appropriate information",
            'er0001': "Please enter an email in the email field",
            'er0010':"The email you have provided already exists",
            'er0011':"Please enter a valid phone number",
            'er0100': "Username already exists",
            'er0101': "The passwords you have entered do not match",
            'er0110': "Username or Password does not match",
            'er0111': "Station name already exists",
            'er1000': "Invalid ID Citern",
            'er1111': "First name or last name cannot contain non-alphabetical characters"}

    def __init__(self):
        #gui window code
        self.gmsMainWindow = QtWidgets.QMainWindow()
        self.mainWindow = gmsMainWindow.Ui_GMSAnalytics()
        self.mainWindow.setupUi(self.gmsMainWindow)

        #Modules initialized
        self.usr = user.User()
        self.field = fields.Field()
        self.query = gmsQueries.Query()


        #User Actions Code
        self.mainWindow.login_btn.clicked.connect(self.loginAction)
        self.mainWindow.password_lineEdit.returnPressed.connect(self.loginAction)
        self.mainWindow.logout_btn.clicked.connect(self.logoutAction)
        self.mainWindow.signUp_btn.clicked.connect(self.signUpPageAction)
        self.mainWindow.return_btn.clicked.connect(self.returnToLoginPageAction)
        self.mainWindow.createUser_btn.clicked.connect(self.signupAction)
        self.mainWindow.returnToLogin_btn.clicked.connect(self.returnToLoginPageAction)

        #Station Set up Code
        self.mainWindow.newStation_btn.clicked.connect(self.createNewStation_page)
        self.mainWindow.stationSetupMain_btn.clicked.connect(self.setupStation_page)
        self.mainWindow.tankInfo_btn.clicked.connect(self.setupStation)
        self.mainWindow.stationInfo_btn.clicked.connect(self.createNewStation_page)
        self.numOfTanks_comboBox_text()
        self.franchisor_comboBox_text()
        self.mainWindow.finishSetup_btn.clicked.connect(self.stationTankSetup)
        self.mainWindow.tankInfoPre_btn.clicked.connect(self.tankInfo_page)
        self.mainWindow.createStation_btn.clicked.connect(self.createStation)

        #gms Main Window Code
        self.mainWindow.fuels_btn.clicked.connect(self.fuelDataInput_page)
        self.mainWindow.tanks_btn.clicked.connect(self.tankDataInput_page)
        self.mainWindow.data_btn.clicked.connect(self.dataDatainput_page)
        self.mainWindow.fuelSearch_btn.clicked.connect(self.displayCRX)
        self.period_comboBox_text()
        self.table_comboBox_text()
        self.currentDate()
        self.mainWindow.fuelSubmit_btn.clicked.connect(self.addMeasurements)
        self.mainWindow.dataSearch_btn.clicked.connect(self.displayTable)
        self.mainWindow.tankSubmit_btn.clicked.connect(self.addInventory)
        self.mainWindow.selectStation_comboBox.currentIndexChanged.connect(self.changeStation)


    def loginAction(self):
        
        

        email = self.mainWindow.loginId_lineEdit.text()
        password = self.mainWindow.password_lineEdit.text()

        self.station = station.Station(email)
        if self.usr.login(email,password)==True and self.station.user()!=False:
            self.usr.info()
            self.mainWindow.main_stackedWidget.setCurrentIndex(0)
            self.selectStation_comboBox_text(tuple(self.usr.stations))
            self.mainWindow.loginId_lineEdit.clear()
            self.mainWindow.password_lineEdit.clear()
            _translate = QtCore.QCoreApplication.translate
            self.mainWindow.username_label.setText(_translate("MainWindow", self.usr.first_name)+' '+self.usr.last_name)
            self.fuelType()
        elif self.usr.login(email,password)==True and self.station.user()==False:
            self.mainWindow.main_stackedWidget.setCurrentIndex(2)
            self.mainWindow.loginId_lineEdit.clear()
            self.mainWindow.password_lineEdit.clear()
        else:
            error = self.field.error([self.usr.login(email,password)])
            self.mainWindow.msgBoxError(self.error[error])

    def signupAction(self):
        signup_data = [self.mainWindow.fName_lineEdit.text(),
                       self.mainWindow.lName_lineEdit.text(),
                       self.mainWindow.email_lineEdit.text(),
                       self.mainWindow.phoneNumber_lineEdit.text(),
                       self.mainWindow.newPassword_lineEdit.text(),
                       self.mainWindow.newPasswordCon_lineEdit.text()]

        
        if self.field.check(signup_data) == True:
            self.mainWindow.msgBox("""Your profile has been created. Next create your station, if your station already exist, add the station code.""")
            self.mainWindow.main_stackedWidget.setCurrentIndex(2)
            self.mainWindow.fName_lineEdit.clear()
            self.mainWindow.lName_lineEdit.clear()
            self.mainWindow.email_lineEdit.clear()
            self.mainWindow.phoneNumber_lineEdit.clear()
            self.mainWindow.newPassword_lineEdit.clear()
            self.mainWindow.newPasswordCon_lineEdit.clear()
        else:
            self.mainWindow.msgBoxError(self.error[self.field.check(signup_data)])

    def setupStation(self):

        self.setupStation_info = [self.mainWindow.franchisor_comboBox.currentText(),
                                  self.field.station_name(self.mainWindow.stationName_lineEdit.text()),
                                  self.mainWindow.streetAddress_lineEdit.text(),
                                  self.mainWindow.city_lineEdit.text(),
                                  self.mainWindow.department_lineEdit.text(),
                                  self.mainWindow.numOfTanks_comboBox.currentText()]

        if self.field.error(self.setupStation_info) == False and self.field.empty(self.setupStation_info) == False:
            self.tankInfo_page()

        else:
            try:
                self.mainWindow.msgBoxError(self.error[self.field.error(self.setupStation_info)])
            except:
                self.mainWindow.msgBoxError(self.error[self.field.empty(self.setupStation_info)])

    def changeStation(self):
        try:
            stationName = self.mainWindow.selectStation_comboBox.currentText()
            self.station.info(stationName)
            self.station_id = self.station.stationId
            self.fuelType()
        except:
            pass

    def fuelDataInput_page(self):
        self.mainWindow.gmsAnalytics_stackedWidget.setCurrentIndex(0)

    def tankDataInput_page(self):
        self.mainWindow.gmsAnalytics_stackedWidget.setCurrentIndex(1)

    def dataDatainput_page(self):
        self.mainWindow.gmsAnalytics_stackedWidget.setCurrentIndex(2)

    def logoutAction(self):
        self.mainWindow.selectStation_comboBox.clear()
        self.mainWindow.totalCRX1_doubleSpinBox.clear()
        self.mainWindow.totalCRX2_doubleSpinBox.clear()
        self.mainWindow.totalCRX3_doubleSpinBox.clear()
        self.mainWindow.totalCRX4_doubleSpinBox.clear()
        self.mainWindow.totalCRX5_doubleSpinBox.clear()
        self.mainWindow.CRX1_comboBox.clear()
        self.mainWindow.CRX2_comboBox.clear()
        self.mainWindow.CRX3_comboBox.clear()
        self.mainWindow.CRX4_comboBox.clear()
        self.mainWindow.CRX5_comboBox.clear()
        self.mainWindow.tankSelect_comboBox.clear()
        self.mainWindow.truckId_lineEdit.clear()
        self.mainWindow.data_tableWidget.clear()
        self.mainWindow.data_tableWidget.setRowCount(0)
        self.mainWindow.data_tableWidget.setColumnCount(0)
        self.mainWindow.main_stackedWidget.setCurrentIndex(1)
        self.mainWindow.gmsAnalytics_stackedWidget.setCurrentIndex(0)
        self.mainWindow.gmsLogin_stackedWidget.setCurrentIndex(0)
        self.usr.db.close()
        self.station.db.close()

    def signUpPageAction(self):
        self.mainWindow.gmsLogin_stackedWidget.setCurrentIndex(1)

    def returnToLoginPageAction(self):
        self.mainWindow.main_stackedWidget.setCurrentIndex(1)
        self.mainWindow.gmsLogin_stackedWidget.setCurrentIndex(0)

    def selectStation_comboBox_text(self,station_names = None):
        self.mainWindow.selectStation_comboBox.addItems(station_names)

    def numOfTanks_comboBox_text(self):
        numOfTanks = ('1','2','3','4','5','6','7','8','9','10')
        self.mainWindow.numOfTanks_comboBox.addItems(numOfTanks)

    def franchisor_comboBox_text(self):
        franchisors = ('Total','National','Go')
        self.mainWindow.franchisor_comboBox.addItems(franchisors)

    def period_comboBox_text(self):
        dates = ('1 Day','5 Days','1 Month','3 Months','6 Months','1 Year', '5 Years','All')
        self.mainWindow.dataPeriod_comboBox.addItems(dates)

    def table_comboBox_text(self):
        tables = ('CRX', 'Measurements','Inventory','Fuel Deposit')
        self.mainWindow.tableSelection_comboBox.addItems(tables)

    def createNewStation_page(self):
        self.mainWindow.gmsStationSetup_stackedWidget.setCurrentIndex(1)
        self.mainWindow.tableWidget.clear()

    def setupStation_page(self):
        self.mainWindow.gmsStationSetup_stackedWidget.setCurrentIndex(0)

    def tankInfo_page(self):
        self.mainWindow.tableWidget.setColumnCount(5)
        self.mainWindow.tableWidget.setHorizontalHeaderLabels(('Name','Capacity','Diameter','Length','Thickness'))
        self.mainWindow.tableWidget.setRowCount(int(self.mainWindow.numOfTanks_comboBox.currentText()))
        self.mainWindow.listWidget.clear()
        self.mainWindow.gmsStationSetup_stackedWidget.setCurrentIndex(2)

    def stationTankSetup(self):
        rowCount = int(self.mainWindow.numOfTanks_comboBox.currentText())
        columnCount = 5
        self.tankData = []
        items =("Station Name: "+self.setupStation_info[1],
                "Street: "+self.setupStation_info[2],
                "City: "+self.setupStation_info[3],
                "Departement: "+self.setupStation_info[4],
                "Franchisor: "+self.setupStation_info[0],
                "Number of Tanks: "+self.setupStation_info[5])

        for r in range(rowCount):
            tank = []
            for c in range(columnCount):
                try:
                    tank.append(self.mainWindow.tableWidget.item(r,c).text())
                except:
                    tank.append("N/A")

            items+=("Tank Name: "+tank[0],
                    "Capacity: "+tank[1],
                    "Diameter: "+tank[2],
                    "Length: "+tank[3],
                    "Thickness: "+tank[4])

            self.tankData.append(tank)

        for tank in self.tankData:
            if("N/A" in tank):
                return self.mainWindow.msgBoxError(self.error['er0000'])

        self.mainWindow.listWidget.addItems(items)
        self.mainWindow.gmsStationSetup_stackedWidget.setCurrentIndex(3)
        return self.tankData

    def createStation(self):
        self.usr.info()
        user_id = self.usr.id
        self.station.create(self.setupStation_info)
        station_id = self.station.stationId
        tank = Tank(station_id)
        tank.create(self.tankData)
        self.usr.add_station(station_id)
        self.mainWindow.msgBox("Station has been created")
        self.logoutAction()
        self.mainWindow.tableWidget.clear()
        self.mainWindow.stationName_lineEdit.clear()
        self.mainWindow.streetAddress_lineEdit.clear()
        self.mainWindow.city_lineEdit.clear()
        self.mainWindow.department_lineEdit.clear()
        self.mainWindow.gmsStationSetup_stackedWidget.setCurrentIndex(1)

    def show(self):
        self.gmsMainWindow.show()

    def displayCRX(self):
        CRXData = namedtuple('crx_data','id_citern crx1 crx2 crx3 crx4 crx5 experation_date')
        id_citern = self.mainWindow.truckId_lineEdit.text()
        crx = self.query.displayCRX(id_citern)
        try:
            crx_data = CRXData._make(crx)
            self.mainWindow.totalCRX1_doubleSpinBox.setValue(crx_data.crx1)
            self.mainWindow.totalCRX2_doubleSpinBox.setValue(crx_data.crx2)
            self.mainWindow.totalCRX3_doubleSpinBox.setValue(crx_data.crx3)
            self.mainWindow.totalCRX4_doubleSpinBox.setValue(crx_data.crx4)
            self.mainWindow.totalCRX5_doubleSpinBox.setValue(crx_data.crx5)
            self.mainWindow.totalCRX1_doubleSpinBox.hide()
            self.mainWindow.totalCRX1_doubleSpinBox.show()
            self.mainWindow.totalCRX2_doubleSpinBox.hide()
            self.mainWindow.totalCRX2_doubleSpinBox.show()
            self.mainWindow.totalCRX3_doubleSpinBox.hide()
            self.mainWindow.totalCRX3_doubleSpinBox.show()
            self.mainWindow.totalCRX4_doubleSpinBox.hide()
            self.mainWindow.totalCRX4_doubleSpinBox.show()
            self.mainWindow.totalCRX5_doubleSpinBox.hide()
            self.mainWindow.totalCRX5_doubleSpinBox.show()
        except:
            self.mainWindow.msgBoxError(self.error['er1000'])

    def fuelType(self):
        self.mainWindow.CRX1_comboBox.clear()
        self.mainWindow.CRX2_comboBox.clear()
        self.mainWindow.CRX3_comboBox.clear()
        self.mainWindow.CRX4_comboBox.clear()
        self.mainWindow.CRX5_comboBox.clear()
        self.mainWindow.tankSelect_comboBox.clear()
        fuelTypeData = namedtuple('fuelTypeData','id station_id name capacity diameter length thickness')
        command = "SELECT * FROM tank WHERE station_id = \'"+str(self.station_id)+"\'"
        self.station.refresh_db()
        self.station.cursor.execute(command)
        results = self.station.cursor.fetchall()
        self.mainWindow.CRX1_comboBox.addItem("N/A")
        self.mainWindow.CRX2_comboBox.addItem("N/A")
        self.mainWindow.CRX3_comboBox.addItem("N/A")
        self.mainWindow.CRX4_comboBox.addItem("N/A")
        self.mainWindow.CRX5_comboBox.addItem("N/A")
        self.mainWindow.tankSelect_comboBox.addItem("N/A")
        for result in results:
            fuelType_data = fuelTypeData._make(result)
            self.mainWindow.CRX1_comboBox.addItem(fuelType_data.name)
            self.mainWindow.CRX2_comboBox.addItem(fuelType_data.name)
            self.mainWindow.CRX3_comboBox.addItem(fuelType_data.name)
            self.mainWindow.CRX4_comboBox.addItem(fuelType_data.name)
            self.mainWindow.CRX5_comboBox.addItem(fuelType_data.name)
            self.mainWindow.tankSelect_comboBox.addItem(fuelType_data.name)
        self.station.db.close()

    def currentDate(self):
        today = date.today()
        now = today.strftime("%Y-%m-%d")
        today = self.mainWindow.tank_dateEdit.dateTimeFromText(now)
        self.mainWindow.tank_dateEdit.setDate(today.date())
        self.mainWindow.fuel_dateEdit.setDate(today.date())

    def addMeasurements(self):

        stationName = self.mainWindow.selectStation_comboBox.currentText()
        self.station.info(stationName)
        fuelDepositData = [self.station.stationId,
                           self.mainWindow.truckId_lineEdit.text(),
                           self.mainWindow.fuel_dateEdit.text()]

        if (self.query.fuelDeposit(fuelDepositData)=='er0000'):
            self.mainWindow.msgBoxError(self.error['er0000'])
        else:
            measurements_data = [["CRX1",self.mainWindow.CRX1_comboBox.currentText(),self.mainWindow.RCRX1_doubleSpinBox.value(),self.mainWindow.DCRX1_doubleSpinBox.value()],
                                 ["CRX2",self.mainWindow.CRX2_comboBox.currentText(),self.mainWindow.RCRX2_doubleSpinBox.value(),self.mainWindow.DCRX2_doubleSpinBox.value()],
                                 ["CRX3",self.mainWindow.CRX3_comboBox.currentText(),self.mainWindow.RCRX3_doubleSpinBox.value(),self.mainWindow.DCRX3_doubleSpinBox.value()],
                                 ["CRX4",self.mainWindow.CRX4_comboBox.currentText(),self.mainWindow.RCRX4_doubleSpinBox.value(),self.mainWindow.DCRX4_doubleSpinBox.value()],
                                 ["CRX5",self.mainWindow.CRX5_comboBox.currentText(),self.mainWindow.RCRX5_doubleSpinBox.value(),self.mainWindow.DCRX5_doubleSpinBox.value()]]

            self.query.fuelDeposit(fuelDepositData)
            measurements_status = self.query.measurements(station_id = self.station.stationId ,measurements = measurements_data)
            if measurements_status!=True:
                self.mainWindow.msgBox(self.error[measurements_status])

            else:   
                self.mainWindow.CRX1_comboBox.setCurrentIndex(0)
                self.mainWindow.CRX2_comboBox.setCurrentIndex(0)
                self.mainWindow.CRX3_comboBox.setCurrentIndex(0)
                self.mainWindow.CRX4_comboBox.setCurrentIndex(0)
                self.mainWindow.CRX5_comboBox.setCurrentIndex(0)

                self.mainWindow.RCRX1_doubleSpinBox.clear()
                self.mainWindow.RCRX2_doubleSpinBox.clear()
                self.mainWindow.RCRX3_doubleSpinBox.clear()
                self.mainWindow.RCRX4_doubleSpinBox.clear()
                self.mainWindow.RCRX5_doubleSpinBox.clear()

                self.mainWindow.DCRX1_doubleSpinBox.clear()
                self.mainWindow.DCRX2_doubleSpinBox.clear()
                self.mainWindow.DCRX3_doubleSpinBox.clear()
                self.mainWindow.DCRX4_doubleSpinBox.clear()
                self.mainWindow.DCRX5_doubleSpinBox.clear()

                self.mainWindow.msgBox('Measurements for '+self.mainWindow.truckId_lineEdit.text()+' has been added to database')

    def displayTable(self):
        tableName = self.mainWindow.tableSelection_comboBox.currentText()
        period = self.mainWindow.dataPeriod_comboBox.currentText()
        self.station.info(self.mainWindow.selectStation_comboBox.currentText())
        data = self.query.displayData(self.station.stationId,tableName,period)
        tableHeader = self.query.tableHeader[tableName]
        self.mainWindow.data_tableWidget.setColumnCount(len(tableHeader))
        self.mainWindow.data_tableWidget.setHorizontalHeaderLabels(tableHeader)
        self.mainWindow.data_tableWidget.setRowCount(len(data))
        self.mainWindow.data_tableWidget.hide()
        self.mainWindow.data_tableWidget.show()
        rowID = 0
        for row in data:
            columnID = 0
            for column in row:
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(column))
                item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
                self.mainWindow.data_tableWidget.setItem(rowID,columnID,item)
                self.mainWindow.data_tableWidget.hide()
                self.mainWindow.data_tableWidget.show()
                columnID+=1
            rowID+=1

    def addInventory(self):
        self.tank = Tank(self.station.stationId)
        tankName = self.mainWindow.tankSelect_comboBox.currentText()
        if self.tank.info(tankName) == 'er0000':
            self.mainWindow.msgBoxError(self.error['er0000'])
            self.clearInventory()
        else:
            self.tank.info(tankName)
            stockBoD = self.mainWindow.StockBoD_doubleSpinBox.value()
            fuelDeposit = self.mainWindow.fuelReceived_doubleSpinBox.value()
            sales = self.mainWindow.sales_doubleSpinBox.value()
            stockEoD = self.mainWindow.StockEoD_doubleSpinBox.value()
            date = self.mainWindow.tank_dateEdit.text()
            inventoryData = [self.station.stationId,self.tank.tank_id, stockBoD, fuelDeposit, sales, stockEoD, date]
            self.query.inventory(inventoryData)
            self.clearInventory()
            
    def clearInventory(self):
        self.mainWindow.StockBoD_doubleSpinBox.clear()
        self.mainWindow.fuelReceived_doubleSpinBox.clear()
        self.mainWindow.sales_doubleSpinBox.clear()
        self.mainWindow.StockEoD_doubleSpinBox.clear()
        self.mainWindow.groupBox_2.hide()
        self.mainWindow.groupBox_2.show()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = gmsMain()
    main.show()
    sys.exit(app.exec_())


# class Ui_MainWindow(QtWidgets.QMessageBox):
#
#     def msgBoxError(self,message = ''):
#         QtWidgets.QMessageBox.about(self, "Error", message)
#
#     def msgBox(self,message = ''):
#         QtWidgets.QMessageBox.about(self, "Message", message)
