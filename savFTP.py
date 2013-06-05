# -*- coding: utf-8 -*-
#########################################################################################
# savFTP.py
# Sauvegarde FTP des container openVZ ou autres , à vous de voir.
#     2011 Rodolphe Trujillo rt@zone42.fr
#
#    Licence WTFPL :
#     This program is free software. It comes without any warranty, to
#     the extent permitted by applicable law. You can redistribute it
#     and/or modify it under the terms of the Do What The Fuck You Want
#     To Public License, Version 2, as published by Sam Hocevar. See
#     http://sam.zoy.org/wtfpl/COPYING for more details.
#
#
########################################################################################
import ftplib,os
from datetime import datetime,timedelta
# quelques paramêtres :
# le FTP (important)
user = "canard"
password = "coincoin"
host = "pouet.ftp"

#le repertoire ou on va trouver des sauvegardes (important aussi)
homeBackupDir = "/var/lib/vz/dump/"

#nombre de jours au delà duquel on supprime les anciennes sauvegardes sur le FTP (dont l'espace est limité , donc important aussi)
rmdays = 10

# extension des fichiers à sauvegarder.
# seule la dernière extension est prise en compte
# exemple : pour machin.tar.gz c'est le "gz" qui compte
extensionToSave = ['log' ,'tgz']

# un fichier de log pour garder une trace de ce qu'on fait
logFileName = '/var/log/savFTP.log'


#une classe qui represente un item ftp analysé suite au renvoi de la commande LIST
class dirFTPItem():
    def __init__ (self, line):
    # type 0 dir , 1 file , 2 undefined
        self.typeItem = 2
    # file name
        self.nameItem = "__default__"
    # file date
        self.date = None
    # on lance l'analyse
        line = line.split()
        self.nameItem = line[8]
        permission = line[0];
        if permission[0] == "d":
            self.typeItem=0
        else :
            self.typeItem=1
        #le serveur ftp renvoi selon l'ancienneté soit l'année de modification du fichier (pour les vieux fichiers)
        #soit l'heure (ça veux dire que l'année est l'année courante)
        if len(line[7].split(":")) > 1 :
            self.date = datetime.strptime(line[5]+" "+line[6]+" "+line[7]+" "+datetime.utcnow().strftime("%Y") , "%b %d %H:%M %Y")
        else:
            self.date = datetime.strptime(line[5]+" "+line[6]+" "+line[7], "%b %d %Y")


with open(logFileName, "a") as logfile:
    try:
        logfile.write(str(datetime.utcnow())+" Step 1 connect to host : "+host+"\n")
        ftp = ftplib.FTP(host,user,password)
        for filename in os.listdir(homeBackupDir):
            if os.path.isfile(homeBackupDir+filename):
                tabname = filename.split(".")
                for ext in extensionToSave:
                    if tabname[len(tabname)-1] == ext:
                        logfile.write(str(datetime.utcnow())+"Step 2 transmitting file : "+homeBackupDir+filename+"\n")
                        binaryFile = open(homeBackupDir+filename,'rb')
                        ftp.storbinary("STOR "+filename, binaryFile)
                        binaryFile.close()

        repdata = []
        ftp.dir(repdata.append)
        for line in repdata:
            item = dirFTPItem(line)
            if ((item.date + timedelta(days=rmdays) ) < datetime.utcnow()) & (item.typeItem == 1 ):
                logfile.write(str(datetime.utcnow())+" Step 2 deleting "+str(rmdays)+" old file : "+item.nameItem+"\n")
                ftp.delete(item.nameItem)
        ftp.quit()
    except Exception as e:
        logfile.write(str(datetime.utcnow())+" Error : "+str(e))
    finally:
        logfile.close()

