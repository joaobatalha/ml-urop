from utilities import *
import MySQLdb as mysql
import os
import collections
import pdb
import logging
import datetime

logging.basicConfig(level=logging.DEBUG)

CELTICS_TCODE = 2
gamecode = 2012021202
HALFCOURT_X= 46.998
FG_MADE_EVENT_ID = 3
POSSESSION_EVENT_ID = 23
PASS_EVENT_ID = 22

def fetch_positions(cursor, gamecode, quarter, possession, start):
    #basketball_db = connect_to_basketballdb()
    #cursor = basketball_db.cursor(mysql.cursors.DictCursor)
    #start = (possession['time_start'].seconds)/60.0
    finish = start - possession['possession_length'].seconds/60.0
    query = """SELECT Position_updated.gameclock, 
                Position_updated.X
                FROM Position_updated
                WHERE gamecode = %s AND 
                quarter = %s AND 
                (gameclock BETWEEN %s AND %s) AND
                player_id = -1""" % (gamecode, quarter, finish, start)
                 
    cursor.execute(query)
    ball_positions = cursor.fetchall()
    #if len(ball_positions) == 0:
    #    pdb.set_trace()
    return ball_positions

     
"""
This takes the finish time of possession that resulted in a field goal
In the future we can also take free throws into account
"""
def get_exact_start(cursor, gamecode, quarter, time):
    half_d = 10
    higher = time + half_d
    lower = time - half_d
    query = """SELECT Events_updated.game_clock, 
                Events_updated.event_id
                FROM Events_updated
                WHERE gamecode = %s AND 
                period = %s AND 
                (game_clock BETWEEN %s AND %s)
                ORDER BY game_clock DESC""" % (gamecode, quarter, lower, higher)
    cursor.execute(query)
    events = cursor.fetchall()
    min_dif = [None, None, None]
    #Find field goal made event that is closest to possession start
    #according to possessions table
    for event_i, event in enumerate(events):
        if int(event['event_id']) == FG_MADE_EVENT_ID:
            diff = abs(float(event['game_clock'] - time))
            if min_dif[0] == None or diff < min_dif[0]:
                min_dif = [diff, float(event['game_clock']),event_i]
    #If no field goal happened during that time interval something probably went wrong
    if min_dif[0] == None:
        print "No Field goal made event in the interval"
        #pdb.set_trace()
        raise Exception('No field goal made event in interval indicated')
    pass_event = None
    after_possession_event = None
    found_possession_event = False
    #Look through events after field goal made event
    #Find a possession event
    #Find the pass event that comes after that
    #NOTE: Does not cover all cases, but covers most of them
    #There are some cases where we get a bunch of dribble events.
    for event_i, event in enumerate(events[min_dif[2]:]):
        if int(event['event_id']) == POSSESSION_EVENT_ID and found_possession_event == False:
            after_possession_event = events[min_dif[2]:][event_i + 1]
            found_possession_event = True
        if found_possession_event and int(event['event_id']) == PASS_EVENT_ID:
            pass_event = event
            break
    if pass_event == None:
        if after_possession_event == None:
            print "Did not get anything after possession event"
            raise Exception("Did not find a pass event")
        #print "Using possession event time!\n"
        return float(after_possession_event['game_clock']) 
    return float(pass_event['game_clock']) 

def makedir(pathname):
    if os.path.isdir(pathname):
        return
    dirname = os.path.dirname(pathname)
    if dirname: makedir(dirname)
    os.mkdir(pathname, 0777)

def get_csv(team):
    team = (team.lower()).replace(" ", "_")
    dir_path = "/home/joao/halfcourt_analysis/csvs/%s" %(team)
    file_path = dir_path + "/times_results.csv"
    try:
        fout = open(file_path, 'a') 
    except IOError, e:
        print "File did for team %s did not exist!\n" % (team)
        makedir(dir_path)
        fout = open(file_path, 'w')
    return fout

def get_team_ids(gamecode, cursor):
    query = """SELECT Games_Table_updated.hteam, 
            Games_Table_updated.vteam
            FROM Games_Table_updated
            WHERE gamecode = %s""" % (gamecode)
    cursor.execute(query)
    teams = cursor.fetchall()[0]
    teams = teams.values()
    return teams

def get_team_name(team_id, cursor):
    query = """SELECT Team_Dict.team_name
            FROM Team_Dict
            WHERE team_id = %s""" % (team_id)
    cursor.execute(query)
    team_name = cursor.fetchall()[0]
    team_name = team_name.values()
   return team_name

def get_events( cursor, gamecode, period, start, end ):
    query = """SELECT Events_updated.game_clock,
               Events_updated.event_id
               From Events_updated
               WHERE gamecode = %s AND
               period = %s AND
               (game_clock BETWEEN %s AND %s)
               ORDER BY game_clock DESC""" % ( gamecode, period, start, end )
    cursor.execute(query)
    events = cursor.fetchall()
    return events

def fault_before_cross(cursor, possession):
    possession_start = (possession['time_start'].seconds)/60.0
    possession_end  = (possession['time_end'].seconds)/60.0 - 1
    events = get_events(cursor, 

def generate_data(gamecode, cursor):
    #After all of the data is in the server you can use the gamestable here
    teams = get_team_ids(gamecode, cursor) 
    team_1 = teams[0]
    team_2 = teams[1]
    
    #Generate data for both teams
    for i in range(2):
        results = []
        total = 0
        for quarter in range(1,5):
            query = """SELECT Possessions_updated.time_start,
                        Possessions_updated.time_end,
                        Possessions_updated.results,
                        Possessions_updated.team_id,
                        Possessions_updated.possession_length, 
                        Possessions_updated.points 
                        FROM Possessions_updated 
                        WHERE gamecode = %s AND  
                        quarter = %s""" % (gamecode, quarter)
            cursor.execute(query)
            possessions = cursor.fetchall()
            for possession_i, possession in enumerate(possessions): 
                if possession['results'] in ["FG2 Made", "FG3 Made"] and possession['team_id'] == team_2:
                    if possession_i + 1 >= len(possessions):
                        #Last possession of quarter
                        continue
                    afg_possession = possessions[possession_i + 1] #After field goal possession

                    if afg_possession['possession_length'] == datetime.timedelta(0): continue
                    time_end = (possession['time_end'].seconds)/60.0
                    possession_start = (afg_possession['time_start'].seconds)/60.0
                    try:
                        start = get_exact_start(cursor, gamecode, quarter, time_end)
                    except Exception, e:
                        #Using time from Possession table, which is less accurate
                        start = possession_start
                    ball_positions = fetch_positions(cursor, gamecode, quarter, afg_possession, start)
                    if len(ball_positions) == 0:
                        print "We are missing some position data! \n" 
                        #pdb.set_trace()
                        continue

                    #check if a timeout or a foul occurred in possession
                    #This is indicated by stopping the gameclock
                    pos_times = [ball_pos['gameclock'] for ball_pos in ball_positions]
                    if len(pos_times) != len(set(pos_times)):
                        #Detected a foul or a timeout, so skip possession
                        continue

                    
                    s = cmp(HALFCOURT_X - ball_positions[0]['X'], 0)
                    for ball_pos in ball_positions:
                        new_s = cmp(HALFCOURT_X - ball_pos['X'], 0)
                        if new_s != s:
                            time_to_cross  = start - ball_pos['gameclock']
                            if time_to_cross >= 7.5 or time_to_cross <= 1.5:
                                break

                            #print "FG possession start: %s\n" % (possession['time_start'].seconds/60.0)
                            #print "FG possession end: %s\n" % (possession['time_end'].seconds/60.0)
                            #print "afg_possession start: %s\n" % (afg_possession['time_start'].seconds/60.0)
                            #print "time_to_cross: %s\n" % (time_to_cross)
                            results.append((round(time_to_cross,2), int(afg_possession['points'])))
                            break
        team_name = get_team_name(team_1, cursor)[0]
        fout = get_csv(team_name)
        for (time, points) in results:
            fout.write("%s,%s \n" % (time,points))
        print "gamecode: %s \n" % (gamecode)
        fout.close()
        temp = team_1
        team_1 = team_2
        team_2 = temp
                
                

if __name__ == "__main__":
    basketball_db = connect_to_basketballdb()
    cursor = basketball_db.cursor(mysql.cursors.DictCursor)
    query = """SELECT Games_Table_updated.gamecode
            FROM Games_Table_updated"""
    cursor.execute(query)
    gamecodes = cursor.fetchall()
    gamecodes = [int(x['gamecode']) for x in gamecodes]
    gamecodes = set(gamecodes)
    total = len(gamecodes)
    for num, gamecode in enumerate(gamecodes, start=1):
        try:
            print "Analysing game %s out of %s games \n" %(num, total)
            generate_data(gamecode, cursor)
        except Exception, e:
            logging.exception("Something went wrong in the analysis")
            continue
    

