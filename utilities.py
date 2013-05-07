import MySQLdb as mysql

def connect_to_basketballdb():
    return  mysql.connect(host="localhost",db="basketball_2011_2012")
    
