#!/usr/bin/env python3
import sys, os, requests, json, pickle, data, utils
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()



##############
#    URLs    #
##############
LWL_BASE = 'https://leftwinglock.com'
LWL_LOGIN = '/forum/index.php?login/login'
LWL_LINES = '/line-combinations/{TEAM_SLUG}/?team={TEAM_SLUG}&strength={STRENGTH}&gametype={GAMETYPE}'




#######################
#    Main function    #
#######################

# Call utils.return_alt to return a team's slug from data.NHL_TEAMS
def get_lines(team_slug, *args):
    strength = 'EV' # Set default  
    gametype = 'GD' # Set default
    gametypes = ['GD', '1', '3', '10'] # Gameday | Most recent game | Last 3 games | Last 10 games
    strengths = ['EV', 'PP', 'SH'] # Even stregnth | Powerplay | PenaltyKill('ShortHanded')
    
    # Check args for a gametype or strength
    for arg in args:
        if arg in gametypes:
            gametype = arg
        elif arg in strengths:
            strength = arg
    
    # Login URL
    login_url = LWL_BASE + LWL_LOGIN
    
    # Lines URL
    lines_url = LWL_BASE + LWL_LINES.format(
        TEAM_SLUG = team_slug,
        STRENGTH = strength, 
        GAMETYPE = gametype 
    )

    # Request helpers
    payload = {
        'login': os.getenv('LWL_USER'),
        'password': os.getenv('LWL_PASS')
    }
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0'}



    #
    with requests.Session() as session:
        lines = {}
        session.headers = headers
        post = session.post(login_url, data=payload)
        response = session.get(lines_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Scrape timestamp
        ts = soup.find('div', {'class': 'goalies__time'})
        lines['last_updated'] = ts.text


        # Even strength lines
        if strength is "EV":
            counter, line_counter, tmp = 1, 1, {}
            team_div = soup.find('ul', {'class': 'team__players'})

            # **Two different digs due to LWL putting Line 1 in those jersey images.

            # Scrape the jerseys
            for r in team_div.find_all('div', {'class': 'team__shirt-name'}):
                for name in r.find_all('a', href=True):
                    x = utils.parse_link(name['href'])
                    tmp[counter] = x
                    counter += 1
            lines[line_counter] = tmp
            counter = 1

            # Scrape the next 3 lines
            for i in range(3):
                line_counter = i + 2            
                tmp, counter = {}, 1
                for x in team_div.find_all('li', {'class': 'team__position'}):
                    for t in x.find_all('li', {'class': 'team__players-list-item'})[i]:
                        x = utils.parse_link(t['href'])
                        tmp[counter] = x
                        counter += 1
                lines[line_counter] = tmp
                line_counter += 1
            return lines

        # Powerplay lines    
        elif strength is "PP":
            counter, line_counter, tmp, players = 1, 1, {}, []
            team_div = soup.find('div', {'class': 'team gutter'})  

            # (Probably a better way to do this)
            #  -> Scrape all 10 players on the PP (in order) and append to a list.
            #  -> Cut list in half to get PP1 and PP2; return both PP units in a dict
            for r in team_div.find_all('div', {'class': 'team__group'}):
                for x in r.find_all('a', href=True):
                    players.append(utils.parse_link(x['href']))
            pp1 = players[:len(players)//2]
            pp2 = players[len(players)//2:]
            units = [pp1, pp2]
            line_counter = 1
            for unit in units:
                counter, tmp = 1, {}
                for player in unit:
                    tmp[counter] = player
                    counter += 1
                lines[line_counter] = tmp 
                line_counter += 1
            return lines



