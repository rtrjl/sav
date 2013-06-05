import ftplib

ftp = ftplib.FTP("host.ftp")
ftp.login("canard", "coincoin")

data = []

ftp.dir(data.append)

ftp.quit()

for line in data:
    print "-", line

