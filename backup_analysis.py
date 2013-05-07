from utilities import *
import MySQLdb as mysql
import pdb

CELTICS_TCODE = 2
gamecode = 2012021202
CELTICS_ALIAS = 'Bos'
HALFCOURT_X= 46.998

def fetch_positions(cursor, gamecode, quarter, possession):
    #basketball_db = connect_to_basketballdb()
    #cursor = basketball_db.cursor(mysql.cursors.DictCursor)
    start = (possession['time_start'].seconds)/60.0
    finish = start - possession['possession_length'].seconds/60.0
    query = """SELECT Position_joao.gameclock, 
                Position_joao.X
                FROM Position_joao
                WHERE gamecode = %s AND 
                quarter = %s AND 
                player_id = -1 AND 
                (gameclock BETWEEN %s AND %s)""" % (gamecode, quarter, finish, start)

    #cursor.execute("""SELECT Position_joao.gameclock, 
    #            Position_joao.X
    #            FROM Position_joao
    #            WHERE gamecode = %s AND 
    #            quarter = %s AND 
    #            player_id = -1 AND 
    #            (gameclock BETWEEN %s AND %s)""", (gamecode, quarter, start, finish))
    cursor.execute(query)
    ball_positions = cursor.fetchall()
    return ball_positions
     


def generate_data():
    fout = open('/home/joao/halfcourt_analysis/csvs/halfcourt_times_with_result.csv', 'w')
    basketball_db = connect_to_basketballdb()
    cursor = basketball_db.cursor(mysql.cursors.DictCursor)
    results = []
    f = 0
    total = 0
    for quarter in range(1,5):
        cursor.execute("""SELECT Possessions_joao.time_start,
                    Possessions_joao.results,
                    Possessions_joao.possession_length, 
                        Possessions_joao.points 
                        FROM Possessions_joao 
                        WHERE team_alias = %s AND 
                        gamecode = %s AND  
                        quarter = %s""", (CELTICS_ALIAS,gamecode, quarter))
        possessions = cursor.fetchall()
        total += len(possessions)
        for possession in possessions: 
            ball_positions = fetch_positions(cursor, gamecode, quarter, possession)
            if abs(HALFCOURT_X - ball_positions[0]['X']) < 34: 
                f += 1
                print "Possession did not start close enough to baseline! X: %f \n" %(ball_positions[0]['X'])
                print "Possess starting at clock time: %i, quarter: %i,  length: %i and with result: %s \n" %((possession['time_start'].seconds)/60.0, quarter, possession['possession_length'].seconds/60.0, possession['results'])
            if abs(HALFCOURT_X - ball_positions[0]['X']) >= 34: #if ball is 
                start = ball_positions[0]['gameclock']
                s = cmp(HALFCOURT_X - ball_positions[0]['X'], 0)
                for ball_pos in ball_positions:
                    new_s = cmp(HALFCOURT_X - ball_pos['X'], 0)
                    if new_s != s:
                        time_to_cross  = start - ball_pos['gameclock']
                        results.append((round(time_to_cross,2), int(possession['points'])))
                        break
    print "Total possessions: %i \n" % (total)
    print "Possessions that we did not analyse because they started too far from baseline: %i \n" % (f)
    for (time, points) in results:
        fout.write("%s,%s\n" % (time,points))
    fout.close()
    print "Finished writing to csv file!"
    return results 
                
                

if __name__ == "__main__":
    generate_data()
