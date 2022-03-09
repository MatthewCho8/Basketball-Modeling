from doctest import master
from bs4 import BeautifulSoup as bs
import requests as rq
import pandas as pd
import unidecode as uc

# Constants
team_list_abb = ["ATL", "BRK", "BOS", "CHO", "CHI",
                 "CLE", "DAL", "DEN", "DET", "GSW",
                 "HOU", "IND", "LAC", "LAL", "MEM",
                 "MIA", "MIL", "MIN", "NOP", "NYK",
                 "OKC", "ORL", "PHI", "PHO", "POR",
                 "SAC", "SAS", "TOR", "UTA", "WAS"]

def get_team_rosters(team_list, year):
    team_url = "https://www.basketball-reference.com/teams/"
    master_df = pd.DataFrame(columns=['Team', 'Player', 'Reference'])

    for team in team_list:
        team_id = str(team) + "/" + str(year) + ".html"
        full_url = team_url + team_id

        soup_obj = bs(rq.get(full_url).content, "lxml")
        roster_table = soup_obj.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="roster")
        player_names = roster_table.find_all(attrs={"data-stat": "player"})
        roster_list = []
        url_list = []
        team_name_list = []
        for player in player_names:
            try:
                roster_list.append(uc.unidecode(player.find(href=True).text))
                url_list.append("https://www.basketball-reference.com" + str(player.find(href=True)).split('"')[1::2][0])
            except:
                continue
        
        team_name_list += [team] * len(roster_list)
        
        dict_to_append = {"Team" : team_name_list, "Player" : roster_list, "Reference" : url_list}
        temp_df = pd.DataFrame().from_dict(dict_to_append)
        master_df = master_df.append(temp_df, ignore_index=True).reset_index(drop=True)


    master_df.to_csv("NBA Rosters/NBA_roster_" + str(year) + ".csv", index=False)

def get_injury_report():
    injury_url = "https://www.basketball-reference.com/friv/injuries.fcgi"
    soup_obj = bs(rq.get(injury_url).content, "lxml")
    injury_table = soup_obj.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="injuries")
    injury_list = injury_table.find_all("tr")

    injured_player_list = []
    injury_report_list = []

    for injury in injury_list:
        try:
            temp = injury.find_all(attrs={"data-stat": "player"})
            player_name = str(temp[0].text)
            if player_name == 'Player':
                continue
            temp1 = injury.find_all(attrs={"data-stat": "date_update"})
            date = str(temp1[0].text)
            temp2 = injury.find_all(attrs={"data-stat": "note"})
            description = str(temp2[0].text)
            injury_report = date + ": " + description
            injured_player_list.append(uc.unidecode(player_name))
            injury_report_list.append(uc.unidecode(injury_report))
        except:
            continue
    
    output_dictionary = dict(zip(injured_player_list, injury_report_list))
    return output_dictionary

def create_daily_roster(year):
    cur_roster_path = r"NBA Rosters/NBA_roster_" + str(year) + ".csv"
    master_df = pd.read_csv(cur_roster_path)
    injury_dict = get_injury_report()
    injury_col_to_add = []

    for index, row in master_df.iterrows():
        cur_player = row['Player']
        if injury_dict.get(cur_player) != 'None':
            injury_col_to_add.append(injury_dict.get(cur_player))
        else:
            injury_col_to_add.append("")

    new_df = master_df
    new_df['Injury'] = injury_col_to_add
    new_df.to_csv(r"NBA Rosters/daily_roster_" + str(year) + ".csv", index=None)


#get_injury_report()
create_daily_roster("2022")
#get_team_rosters(team_list_abb, 2022)