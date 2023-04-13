from bs4 import BeautifulSoup
import aiohttp
import asyncio

import datetime

import discord
from discord.ext import tasks

team_num = '8'

TOKEN = ''
team_name = '日本ハム'
def WinLose(team_num, soup, home_visiter):
    if home_visiter == 0:
        parse = soup.find('p', class_='bb-score__homeLogo bb-score__homeLogo--npbTeam{}'.format(team_num))\
            .find_parent('div').find_parent('a')
        score_of_home = int(parse.find('span', class_='bb-score__score bb-score__score--left').text)
        score_of_away = int(parse.find('span', class_='bb-score__score bb-score__score--right').text)

        if score_of_home > score_of_away:
            return 0
        elif score_of_home < score_of_away:
            return 1
        elif score_of_home == score_of_away:
            return 2
        else:
            return 3

    elif home_visiter == 1:
        parse = soup.find('p', class_='bb-score__awayLogo bb-score__awayLogo--npbTeam{}'.format(team_num))\
            .find_parent('div').find_parent('a')
        score_of_home = int(parse.find('span', class_='bb-score__score bb-score__score--left').text)
        score_of_away = int(parse.find('span', class_='bb-score__score bb-score__score--right').text)

        if score_of_home < score_of_away:
            return 0
        elif score_of_home > score_of_away:
            return 1
        elif score_of_home == score_of_away:
            return 2
        else:
            return 3

    else:
        return 3

def GetOpponentName(home_visiter, team_num, soup):
    if home_visiter == 0:
        parse = soup.find('p', class_='bb-score__homeLogo bb-score__homeLogo--npbTeam{}'
                          .format(team_num)).find_next_siblings("p")
        return parse[0].text

    elif home_visiter == 1:
        parse = soup.find('p', class_='bb-score__awayLogo bb-score__awayLogo--npbTeam{}'
                          .format(team_num)).find_previous_siblings("p")
        return parse[0].text


client = discord.Client(intents=discord.Intents.all())


# 1日に一回ループ
@tasks.loop()
async def loop():
    now = datetime.datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    oclock = now.strftime('%H')
    minmin = now.strftime('%M')

    print('Loop resumed at {}:{}:{}:{}:{}'.format(year, month, day, oclock, minmin))

    yahoo_url = 'https://baseball.yahoo.co.jp/npb/schedule/?date='

    access_url = yahoo_url + year + '-' + month + '-' + day

    async with aiohttp.ClientSession() as session:
        async with session.get(access_url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            home = soup.find_all('p', class_='bb-score__homeLogo bb-score__homeLogo--npbTeam{}'.format(team_num))
            away = soup.find_all('p', class_='bb-score__awayLogo bb-score__awayLogo--npbTeam{}'.format(team_num))

    if len(home) == 1:
        try:
            parse = soup.find('p', class_='bb-score__homeLogo bb-score__homeLogo--npbTeam{}'
                              .format(team_num)).find_parent('div').find_parent('a')
            start_time = parse.find('time', class_='bb-score__status').text
            start_hour = start_time[:2]
            start_minutes = start_time[:2]
            game_start = now.replace(hour=int(start_hour), minute=int(start_minutes), second=0, microsecond=0)
            process_start = game_start + datetime.timedelta(hours=2)
            sleep_time = (process_start - now).total_seconds()
            for member in client.get_all_members():
                if not member.bot:
                    try:
                        await member.send('試合開始まで{}秒間スリープします'.format(sleep_time))
                    except:
                        pass
            print('Start Short Sleep at {}:{}:{}:{}:{} for {}seconds'.format(year, month, day, oclock, minmin, sleep_time))
            await asyncio.sleep(sleep_time)
            status = parse.find('p', class_='bb-score__link').text
            loop_flag = 0
        except:
            loop_flag = 1
            status = '試合無し'
            parse = ''

        while(loop_flag == 0):
            if status == '試合終了':
                win_lose = WinLose(team_num=team_num, soup=soup, home_visiter=0)

                if win_lose == 0:
                    score_of_home = int(parse.find('span', class_='bb-score__score bb-score__score--left').text)
                    score_of_away = int(parse.find('span', class_='bb-score__score bb-score__score--right').text)

                    score = '{}-{}'.format(score_of_home, score_of_away)

                    opponent_name = GetOpponentName(home_visiter=0, team_num=team_num, soup=soup)

                    for member in client.get_all_members():
                        if not member.bot:
                            try:
                                await member.send('--------【速報】--------\n{}が{}に{}で勝利しました！！'
                                                  .format(team_name, opponent_name, score))
                            except:
                                pass
                    loop_flag = 1

                elif win_lose == 1: #負けた時
                    score_of_home = int(parse.find('span', class_='bb-score__score bb-score__score--left').text)
                    score_of_away = int(parse.find('span', class_='bb-score__score bb-score__score--right').text)

                    score = '{}-{}'.format(score_of_home, score_of_away)

                    opponent_name = GetOpponentName(home_visiter=0, team_num=team_num, soup=soup)

                    for member in client.get_all_members():
                        if not member.bot:
                            try:
                                await member.send('--------【速報】--------\n{}が{}に{}で敗北しました！！'
                                                  .format(team_name, opponent_name, score))
                            except:
                                pass
                    loop_flag = 1

                elif win_lose == 2: #引き分けた時
                    score_of_home = int(parse.find('span', class_='bb-score__score bb-score__score--left').text)
                    score_of_away = int(parse.find('span', class_='bb-score__score bb-score__score--right').text)

                    score = '{}-{}'.format(score_of_home, score_of_away)

                    opponent_name = GetOpponentName(home_visiter=0, team_num=team_num, soup=soup)

                    for member in client.get_all_members():
                        if not member.bot:
                            try:
                                await member.send('--------【速報】--------\n{}が{}に{}で引き分けました！！'
                                                  .format(team_name, opponent_name, score))
                            except:
                                pass
                    loop_flag = 1
                else:
                    for member in client.get_all_members():
                        if not member.bot:
                            try:
                                await member.send('試合結果の取得にエラーが発生した可能性があります')
                            except:
                                pass
                    loop_flag = 1
            elif '回' in status:
                await asyncio.sleep(300)
                for member in client.get_all_members():
                    if not member.bot:
                        try:
                            await member.send('結果を待つために5分休止します')
                        except:
                            pass
            else:
                opponent_name = GetOpponentName(home_visiter=0, team_num=team_num, soup=soup)
                for member in client.get_all_members():
                    if not member.bot:
                        try:
                            await member.send('本日の{}と{}の試合は中止になりました'.format(team_name, opponent_name))
                        except:
                            pass
                loop_flag = 1

    elif len(away) == 1:
        try:
            parse = soup.find('p', class_='bb-score__awayLogo bb-score__awayLogo--npbTeam{}'
                              .format(team_num)).find_parent('div').find_parent('a')
            start_time = parse.find('time', class_='bb-score__status').text
            start_hour = start_time[:2]
            start_minutes = start_time[:2]
            game_start = now.replace(hour=int(start_hour), minute=int(start_minutes), second=0, microsecond=0)
            process_start = game_start + datetime.timedelta(hours=2)
            sleep_time = (process_start - now).total_seconds()
            for member in client.get_all_members():
                if not member.bot:
                    try:
                        await member.send('試合開始まで{}秒間スリープします'.format(sleep_time))
                    except:
                        pass
            print('Start Short Sleep at {}:{}:{}:{}:{} for {}seconds'.format(year, month, day, oclock, minmin, sleep_time))
            await asyncio.sleep(sleep_time)
            status = parse.find('p', class_='bb-score__link').text
            loop_flag = 0
        except:
            status = '試合無し'
            loop_flag = 1
            parse = ''

        while(loop_flag == 0):
            if status == '試合終了':
                win_lose = WinLose(team_num=team_num, soup=soup, home_visiter=1)
                if win_lose == 0: #勝った時
                    score_of_home = int(parse.find('span', class_='bb-score__score bb-score__score--left').text)
                    score_of_away = int(parse.find('span', class_='bb-score__score bb-score__score--right').text)

                    score = '{}-{}'.format(score_of_away, score_of_home)

                    opponent_name = GetOpponentName(home_visiter=1, team_num=team_num, soup=soup)

                    for member in client.get_all_members():
                        if not member.bot:
                            try:
                                await member.send('--------【速報】--------\n{}が{}に{}で勝利しました！！'
                                                  .format(team_name, opponent_name, score))
                            except:
                                pass

                    loop_flag = 1

                elif win_lose == 1: #負けた時
                    score_of_home = int(parse.find('span', class_='bb-score__score bb-score__score--left').text)
                    score_of_away = int(parse.find('span', class_='bb-score__score bb-score__score--right').text)

                    score = '{}-{}'.format(score_of_away, score_of_home)

                    opponent_name = GetOpponentName(home_visiter=1, team_num=team_num, soup=soup)

                    for member in client.get_all_members():
                        if not member.bot:
                            try:
                                await member.send('--------【速報】--------\n{}が{}に{}で敗北しました！！'
                                                  .format(team_name, opponent_name, score))
                            except:
                                pass
                    loop_flag = 1

                elif win_lose == 2: #引き分けた時
                    score_of_home = int(parse.find('span', class_='bb-score__score bb-score__score--left').text)
                    score_of_away = int(parse.find('span', class_='bb-score__score bb-score__score--right').text)

                    score = '{}-{}'.format(score_of_home, score_of_away)

                    opponent_name = GetOpponentName(home_visiter=1, team_num=team_num, soup=soup)

                    for member in client.get_all_members():
                        if not member.bot:
                            try:
                                await member.send('--------【速報】--------\n{}が{}に{}で引き分けました！！'
                                                  .format(team_name, opponent_name, score))
                            except:
                                pass
                    loop_flag = 1
                else:
                    loop_flag = 1
                    for member in client.get_all_members():
                        if not member.bot:
                            try:
                                await member.send('試合結果の取得にエラーが発生した可能性があります')
                            except:
                                pass
            elif '回' in status:
                await asyncio.sleep(300)
                for member in client.get_all_members():
                    if not member.bot:
                        try:
                            await member.send('結果を待つために5分休止します')
                        except:
                            pass
            else:
                opponent_name = GetOpponentName(home_visiter=1, team_num=team_num, soup=soup)
                for member in client.get_all_members():
                    if not member.bot:
                        try:
                            await member.send('本日の{}と{}の試合は中止になりました'.format(team_name, opponent_name))
                        except:
                            pass
                loop_flag = 1
    else:
        for member in client.get_all_members():
            if not member.bot:
                try:
                    await member.send('本日は試合がありません')
                except:
                    pass
    # await asyncio.sleep(30) #実験用 実装時は消す

    now = datetime.datetime.now()
    target_time = datetime.datetime(now.year, now.month, now.day, 12, 0, 0) # 今日の12時
    if now > target_time:
        # 今日の12時を過ぎている場合、明日の12時まで待機
        target_time += datetime.timedelta(days=1)
    wait_seconds = (target_time - now).total_seconds()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    oclock = now.strftime('%H')
    minmin = now.strftime('%M')
    for member in client.get_all_members():
        if not member.bot:
            try:
                await member.send('{}年{}月{}日{}時{}分から{}秒間スリープします'.format(year, month, day, oclock, minmin, wait_seconds))
            except:
                pass
    print('Start Long Sleep at {}:{}:{}:{}:{} for {}seconds'.format(year, month, day, oclock, minmin, wait_seconds))
    await asyncio.sleep(wait_seconds)


#ループ処理実行
@client.event
async def on_ready():
    print("logged in as " + client.user.name)
    for member in client.get_all_members():
        if not member.bot:
            try:
                await member.send('-------------{}速報Bot起動-------------'.format(team_name))
            except:
                pass
    loop.start()

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)