
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import pandas as pd

class pandasModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        QtCore.QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None
    
    
class showStatistic():     
    def __init__(self, data):

        self.data = data
        self.kdrX = 450
        self.kdrY = 350
        self.flashX = 250
        self.flashY = 300
        
    def show_KDR(self):
        d = QtWidgets.QDialog()
        d.setWindowTitle("Final KDR")   
        d.resize(self.kdrX, self.kdrY)
        table = QtWidgets.QTableView(d)
        table.resize(self.kdrX,self.kdrY)
  
        kills = self.data["Kills"].groupby(["AttackerName"]).size().reset_index(name="Kills")
        deaths = self.data["Kills"].groupby(["VictimName"]).size().reset_index(name="Deaths")
        kdr = kills.merge(deaths, left_on = "AttackerName", right_on = "VictimName")
        kdr["KDR"] = kdr["Kills"]/kdr["Deaths"]
        kdr = kdr[["AttackerName", "Kills", "Deaths", "KDR"]]
        kdr.columns = ["PlayerName", "Kills", "Deaths", "KDR"]
        kdr.sort_values(by=["KDR"], ascending=False)

        model = pandasModel(kdr)
        table.setModel(model)
        
        d.setWindowModality(QtCore.Qt.ApplicationModal)
        d.exec_()   

    def show_EnemiesFlashed(self):
        d = QtWidgets.QDialog()
        d.setWindowTitle("Final EnemiesFlashed")   
        d.resize(self.flashX, self.flashY)
        table = QtWidgets.QTableView(d)
        table.resize(self.flashX,self.flashY)
        
        enemyiesFlashed = self.data["EnemiesFlashed"].groupby(["AttackerName"]).size().reset_index(name="EnemiesFlashed")
        enemyiesFlashed = enemyiesFlashed.sort_values(by=["EnemiesFlashed"], ascending=False)

        model = pandasModel(enemyiesFlashed)
        table.setModel(model)
        
        d.setWindowModality(QtCore.Qt.ApplicationModal)
        d.exec_()  
        
    def show_TeamFlashes(self):
        d = QtWidgets.QDialog()
        d.setWindowTitle("Final TeamFlashes")   
        d.resize(self.flashX, self.flashY)
        table = QtWidgets.QTableView(d)
        table.resize(self.flashX,self.flashY)
        
        teamFlashed = self.data["TeamFlashed"].groupby(["AttackerName"]).size().reset_index(name="TeamFlashed")
        teamFlashed = teamFlashed.sort_values(by=["TeamFlashed"], ascending=False)

        model = pandasModel(teamFlashed)
        table.setModel(model)
        
        d.setWindowModality(QtCore.Qt.ApplicationModal)
        d.exec_()  
        
    def show_utilityDMG(self):
        d = QtWidgets.QDialog()
        d.setWindowTitle("Final Utility Damage")   
        d.resize(self.flashX, self.flashY)
        table = QtWidgets.QTableView(d)
        table.resize(self.flashX,self.flashY)
        
        datatmp = self.data["Damages"][['AttackerName', 'Weapon', 'HpDamage']] 
        tmp1 = datatmp.loc[(datatmp['Weapon'] == 'Molotov')]
        tmp2 = datatmp.loc[(datatmp['Weapon'] == 'HE')]
        tmp3 = datatmp.loc[(datatmp['Weapon'] == 'Incendiary')]
        
        utilityDmg = pd.concat([tmp1,tmp2])
        utilityDmg = pd.concat([utilityDmg,tmp3])
        utilityDmg = utilityDmg.groupby(['AttackerName']).sum().reset_index()

        model = pandasModel(utilityDmg)
        table.setModel(model)
        
        d.setWindowModality(QtCore.Qt.ApplicationModal)
        d.exec_()  