from bs4 import BeautifulSoup
import urllib.request, requests, time

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8', 'Connection': 'keep-alive'}         


def sendDiscordMsg(webhook_url, content):
    data = {
        "content": content
    }
    r = requests.post(webhook_url, json=data)
    return r

# ================= 사용 전 직접 설정해 주어야 하는 부분 =================

discord_webhook_url = "https://discord.com/api/webhooks/"
gallery = {'gallid':0}
updTime = 60 

# ========================================================================


tType = "%Y-%m-%d %H-%M-%S"
print("========DCBELL 설정 값========")
print("Discord 웹후크   URL: " + discord_webhook_url)
print("업데이트 간격: " + str(updTime) + "초")
print("==============================")


while(1):

    print("[" + time.strftime(tType) + "] 요청 시작...")

    try:
        
        for g in gallery.items():
            
            gallid = g[0]
            prev_postnum = g[1]

            print("[" + time.strftime(tType) + "] " + gallid + " 조회 시작...")

            link = 'https://gall.dcinside.com/board/lists/?id=' + gallid
            r = requests.get(link, headers = header).text
            print('갤러리 형식:', end=' ')

            if 'location.replace' in r: link = link.replace('board/','mgallery/board/'); print('마이너')
            else: print('정식')
                      
            req = urllib.request.Request(link, headers = header)
            html = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(html, "html.parser")
            link = soup.find_all("tr", { "class" : "ub-content us-post"})

            for m in link:

                tmp = m.find("td", { "class" : "gall_tit ub-word"})

                if "<b>" not in str(tmp):
                    title = tmp.a.text.strip()
                    postnum = m.find("td", { "class" : "gall_num"}).text
                    tmp = m.find("td", { "class" : "gall_writer ub-writer"})
                    name = tmp.find("em").text
                    ip = tmp.find("span", { "class" : "ip"})

                    if ip is not None: ip = ip.text
                    else: ip = "고닉"

                    if (int(postnum) > int(prev_postnum)):
                        print ("======새 글이 있습니다!=======")
                        print ("│갤러리: " + gallid)
                        print ("│글번호: " + postnum)
                        print ("│글제목: " + title)
                        print ("│닉네임(아이피): " + name + " (" + ip + ")")
                        
                        if prev_postnum == 0:
                            print('│(최초 요청이므로 푸시를 보내지 않습니다)')
                        else:
                            print ("│푸시 보내는 중...")
                            sendDiscordMsg(discord_webhook_url, f"{gallid} 갤러리 새 글\n글번호:{postnum}\n====세부정보====\n{title} - {name}({ip})\n[링크](https://gall.dcinside.com/{gallid}/{postnum})")
                            print ("│보내기 완료")
                            
                        gallery[gallid] = postnum
                        print ("===========작업 끝============")
                        break

            time.sleep(1)

    except Exception as ex: print("[" + time.strftime(tType) + "] [오류 발생] 다시 시도합니다.", ex)

    print("[" + time.strftime(tType) + "] 대기 중... (" + str(updTime) + "초)")
    time.sleep(updTime)
