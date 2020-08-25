
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
    
    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        try:
            self.layoutAboutToBeChanged.emit()
            self._data = self._data.sort_values(self._data.columns[Ncol], ascending=not order)
            self.layoutChanged.emit()
        except Exception as e:
            print(e)
    
class showStatistic():     
    def __init__(self, data):

        self.data = data
        self.statsX = 720
        self.statsY = 300
        
    def show_finalStats(self):
        d = QtWidgets.QDialog()
        d.setWindowTitle("Final KDR")   
        d.resize(self.statsX, self.statsY)
        table = QtWidgets.QTableView(d)
        table.resize(self.statsX,self.statsY)
        table.setSortingEnabled(True)
  
        kills = self.data["Kills"].groupby(["AttackerName"]).size().reset_index(name="Kills")
        deaths = self.data["Kills"].groupby(["VictimName"]).size().reset_index(name="Deaths")
        kdr = kills.merge(deaths, left_on = "AttackerName", right_on = "VictimName")
        kdr["KDR"] = round(kdr["Kills"]/kdr["Deaths"], 2)
        kdr = kdr[["AttackerName", "Kills", "Deaths", "KDR"]]
        
        damage = self.data["Damages"][['AttackerName', 'Weapon', 'HpDamage']] 
        tmp1 = damage.loc[(damage['Weapon'] == 'Molotov')]
        tmp2 = damage.loc[(damage['Weapon'] == 'HE')]
        tmp3 = damage.loc[(damage['Weapon'] == 'Incendiary')]
        utilityDmg = pd.concat([tmp1,tmp2])
        utilityDmg = pd.concat([utilityDmg,tmp3])
        utilityDmg = utilityDmg.groupby(['AttackerName']).sum().reset_index()
        utilityDmg = utilityDmg.rename(columns={"HpDamage": "UtilityDMG"})
        
        enemyiesFlashed = self.data["EnemiesFlashed"].groupby(["AttackerName"]).size().reset_index(name="EnemiesFlashed")
        teamFlashed = self.data["TeamFlashed"].groupby(["AttackerName"]).size().reset_index(name="TeamFlashed")
        
        stats = pd.merge(kdr, utilityDmg, on="AttackerName")
        stats = pd.merge(stats, enemyiesFlashed, on="AttackerName")
        stats = pd.merge(stats, teamFlashed, on="AttackerName")

        model = pandasModel(stats)
        table.setModel(model)
        
        d.setWindowModality(QtCore.Qt.ApplicationModal)
        d.exec_()   
