#coding=utf-8
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ytproject.settings")

import django
django.setup()

from yt.models import YoutubeAccount, YoutubeVideo, YoutubeComment
from yt import models

from selenium import webdriver
import csv
from bs4 import BeautifulSoup
import  time
import tkinter # 使用了 python gui 图形开发界面的库
import tkinter.messagebox #引入提示框组件
import threading #引入 线程库
import pymysql
import json,re
import pandas as pd
import datetime


sub_root_path = r"E:\zh\project\youtube\data"
video_scale = 10    #该参数越大，爬取的视频量越大
comment_scale = 50
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_setting.images": 2}#selenium爬虫：设定配置文件，不加载图片，加快爬虫效率
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.set_page_load_timeout(1200) # 设置页面加载超时
driver.set_script_timeout(1200) # 设置页面异步js执行超时
#上面都是chrome的基本配置

def StringToNum(string):
    string = re.findall("[0-9\.万\,]+", string)[0]
    string = string.replace(",", "")
    if "万"in string:
        string = float(string.replace("万","").strip(" "))*10000
    else:
        try:
            string = float(string)
        except:
            print("转化出错")
            print(string)
    return int(string)

def urlToCsv(data,key_word): #生成csv文件
    with open('./data/'+key_word+'/crawed_url_'+key_word+'.csv', 'a+', encoding='utf8', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, dialect='excel')
        spamwriter.writerow(data)

def InfotoJson(data,key_word,counter,sub_path): #生成csv文件
    with open(sub_path+'/crawed_data_'+key_word+"_"+str(counter)+'.json',"w",encoding = "utf8") as f:
        json.dump(data,f,ensure_ascii=False)
        print(key_word+"写入json入文件完成...")

def getVideoDetail(url):
    def get_Comment_detail(soup, driver1,video, level=1):
        index = 1
        for num in range(0, comment_scale):
            index += 1
            js = "window.scrollTo(0, " + str(200 * (index * 2)) + ");"
            driver1.execute_script(js)
            time.sleep(3)
        time.sleep(10)
        try:
            items = soup.find("ytd-comments", id="comments").find("div", id="contents").find_all(
                "ytd-comment-thread-renderer", class_="style-scope ytd-item-section-renderer")
        except:
            items = []
        print(len(items))
        comments_info = []
        print("******************************************************************")
        for item in items:
            #评论文本信息
            try:
                comment = item.find("ytd-expander", id="expander").find("div", id="content").find("yt-formatted-string",id="content-text").get_text()
            except:
                try:
                    comment_containers = item.find("ytd-expander", id="expander").find("div", id="content").find(
                        "yt-formatted-string",
                        id="content-text").find_all("span", class_="style-scope yt-formatted-string")
                    comment = "".join([i.get_text() for i in comment_containers])
                    print("获取分段comment文本")
                except:
                    print("comments 没有采到！！！！！！！")
                    comment = ""
            print(comment)
            #channel_url
            try:
                channel_url = "https://www.youtube.com/" + item.find("div", id="author-thumbnail").find("a",
                                                                                                        "yt-simple-endpoint style-scope ytd-comment-renderer")[
                    "href"]
                print("channel_url", channel_url)
            except:
                channel_url = ""
                print("channel_url没有采到")
            #icon_url
            try:
                icon_url = item.find("div", id="author-thumbnail").find("yt-img-shadow",
                                                                        class_="style-scope ytd-comment-renderer no-transition").find(
                    "img", id="img")["src"]
                print("icon_url", icon_url)
            except:
                icon_url = ""
                print("用户头像url 没有采到")
            #commenter_name
            try:
                commenter_name = item.find("div", id="author-thumbnail").find("yt-img-shadow",
                                                                              class_="style-scope ytd-comment-renderer no-transition").find(
                    "img", id="img")["alt"]
                print("commenter_name: ", commenter_name)
            except:
                commenter_name = ""
                print("用户名 没有采到")
            #relative_time
            try:
                relative_time = item.find("yt-formatted-string",
                                          class_="published-time-text above-comment style-scope ytd-comment-renderer").find(
                    "a", class_="yt-simple-endpoint style-scope yt-formatted-string").get_text()
                print("relative_time", relative_time)
            except:
                relative_time = ""
                print("评论的相对时间 没有采到")
            #commenter_ytid
            try:
                commenter_ytid = item.find("a",id = "author-text")["href"].replace("/channel/","")
            except:
                commenter_ytid = ""
            #likes
            try:
                likes = item.find("div", id="toolbar").find("span", id="vote-count-middle")["aria-label"]
                likes = StringToNum(likes)
                print("likes", likes)
            except:
                likes = 0
                print("评论的点赞数 没有采到")
            '''
            try:
                if item.find("div", id="replies").find("div",id = "expander")!=None:
                    #driver1.find_element_by_xpath('//*[@id="button"]/paper-ripple').click()
                    driver1.find_element_by_id('more-replies').click()
                    print("点击成功了")
                    time.sleep(1)
                    print("正在爬取该评论的回复")
                    sub_items = item.find("div",id = "loaded-replies").find_all("ytb-comment-renderer",class_ = "style-scope ytd-comment-replies-renderer")
                    for sub_item in sub_items:
                        if level >1:
                            sub_item_info = {}
                            break
                        else:
                            level += 1
                            sub_item_info= get_Comment_detail(driver1,sub_item,level)
                            print(sub_item_info)
                else:
                    print("该评论没有回复")
                    sub_item_info = {}
            except Exception as e:
                sub_item_info = {}
                print("评论的回复信息爬取失败",e)
            '''
            comment_info = {
                "comment": comment,
                "channel_url": channel_url,
                "icon_url": icon_url,
                "commenter_name": commenter_name,
                "relative_time": relative_time,
                "likes": likes,
                # "sub_item_info":sub_item_info,
            }
            print("*******************************************************************")
            comments_info.append(comment_info)
            ids = [i[0] for i in models.YoutubeAccount.objects.distinct().values_list('ytid')]
            if commenter_ytid not in ids:
                commenter = YoutubeAccount(name = commenter_name,avatar_url = icon_url,home_url = channel_url,ytid = commenter_ytid)
            else:
                commenter = YoutubeAccount.objects.get(ytid= commenter_ytid)
            commentation = YoutubeComment(video = video,commenter = commenter,up_count = likes,comment_date_str = relative_time,commenter_name = commenter_name,comment_content = comment)
            commenter.save()
            commentation.save()
        return comments_info

    def getYoutuberInfo(user):
        user_Url = user["home_url"]
        try:
            chrome_options = webdriver.ChromeOptions()
            prefs = {"profile.managed_default_content_setting.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)
            driver1 = webdriver.Chrome(chrome_options=chrome_options)
            driver1.set_page_load_timeout(1200)
            driver1.set_script_timeout(1200)
            driver1.get(user_Url)
            driver1.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
        except TimeoutException as e:
            print('超时啦')
        driver1.execute_script('window.stop()')  # 终止页面加载
        driver1.find_element_by_xpath('//*[@id="tabsContent"]/paper-tab[6]').click()
        time.sleep(2)
        res = driver1.page_source
        soup = BeautifulSoup(res, 'html.parser')
        try:
            text = soup.find("yt-formatted-string", id="description").get_text()  # find("yt-formatted-string",text = "说明").
        except:
            text = ""
            print("该博主没有说明信息")
        #print(text)
        try:
            icon_url = soup.find("div", id="channel-header").find("img", id="img")["src"]
        except:
            print("icon_url没有采到")
            icon_url = ""
        try:
            tem_email = [i["href"] for i in soup.find_all("a", id="email")]
            real_email = []
            for each in tem_email:
                if "undefined" not in each:
                    real_email.append(each)
            real_email = "\n".join(real_email)
            print(real_email)
        except:
            real_email = ""
            print("no emil")


        try:
            tem_links = soup.find("div", id="link-list-container").find_all("a",class_="yt-simple-endpoint style-scope ytd-channel-about-metadata-renderer")
            real_links,links = [],[]
            for each in tem_links:
                try:
                    links.append((each.find("yt-formatted-string",
                                            class_="info-text style-scope ytd-channel-about-metadata-renderer").get_text(),
                                  each["href"]))
                except:
                    pass
            for each in links:
                real_links.append(each[0]+" ： "+each[1])
            "\n".join(real_links)

        except:
            real_links = ""
            print("no links")


        try:
            info = []  # 该youtuber的账号信息
            tem_info = soup.find("div", id="right-column").find_all("yt-formatted-string",
                                                                    class_="style-scope ytd-channel-about-metadata-renderer")
            for each in tem_info:
                try:
                    if each.get_text() == '统计信息':
                        reguster_date = each.find("span", class_="style-scope yt-formatted-string").get_text()
                        info.append(reguster_date)
                    else:
                        info.append(each.get_text())
                except:
                    pass
            info = "\n".join(info)
        except Exception as e:
            print(e)
            print("no info")
            info = ""

        related_channels = []
        try:
            tem = soup.find("ytd-vertical-channel-section-renderer",
                            class_="style-scope ytd-browse-secondary-contents-renderer").find("div",
                                                                                              id="items").find_all("a",
                                                                                                                   id="channel-info")
            for each in tem:
                url = "https://www.youtube.com/user/" + each["href"]
                try:
                    name = each.find("span", class_='title style-scope ytd-mini-channel-renderer').get_text()
                except:
                    name = ""
                related_channels.append((name,url))
            related_channels = [each[0]+" : " +each[1] for each in related_channels]
            related_channels = "\n".join(related_channels)
        except:
            print("no related channels")
            related_channels = ""
        user_info = {"description": text,
                     "subscribe_count":user["subscribe_num"],
                     "home_url": user["home_url"],
                     "name": user["uploader"],
                     "icon_url": icon_url,
                     "email": real_email,
                     "links": real_links,
                     "info": info,
                     "related_channels": related_channels}
        print(user_info)

        uploader_account = YoutubeAccount(name=user["uploader"], subscribe_count=user["subscribe_num"],
                                          home_url=user["home_url"],avatar_url = user_info["icon_url"],ytid = user["yter_id"],email = user_info["email"],
                                          info = user_info["info"],description = user_info["description"],related_channels = user_info["related_channels"])
        uploader_account.save()
        driver1.quit()
        return uploader_account

    data_arr = {} #存储标题，观看量，点赞，踩数，上传作者，和订阅量的一个数组
    data_arr["video_url"] = url
    data_arr["ytid"] = url.replace("https://www.youtube.com/watch?v=", "")
    ids = [i[0] for i in models.YoutubeVideo.objects.distinct().values_list('ytid')]
    if data_arr["ytid"] in ids:
        print("这个视频爬过了")
        pass
    else:
        try:
            chrome_options = webdriver.ChromeOptions()
            prefs = {"profile.managed_default_content_setting.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)
            driver1 = webdriver.Chrome(chrome_options=chrome_options)
            driver1.set_page_load_timeout(1200)
            driver1.set_script_timeout(1200)
            driver1.get(url)
            #js="var q=document.documentElement.scrollTop=100000"
            #driver1.execute_script(js)
            driver1.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(5)
        except TimeoutException as e:
            print('超时啦')
            driver1.execute_script('window.stop()')  # 终止页面加载

        arr =[] #存储评论（json格式）的一个数组
        index = 0
        js = "window.scrollTo(0, 2000000000);"
        driver1.execute_script(js)
        time.sleep(5)
        res1 = driver1.page_source
        soup1 = BeautifulSoup(res1, 'html.parser')
        # title
        try:
            title = soup1.find("div", id="info-contents").find("h1").get_text()#视频标题
            print("title:"+title)
            data_arr["title"] = title
        except:
            print("title 没有采到！！！！！！！")
            data_arr["title"] = ""
        #watch_num
        try:
            watch_num = soup1.find("div", id="info-contents").find("span",class_="view-count style-scope yt-view-count-renderer").get_text() #观看数
            watch_num = StringToNum(watch_num)
            print("watch_num:" ,watch_num)
            data_arr["watch_num"] = watch_num
        except:
            print("watch_num 没有采到！！！！！！！")
            data_arr["watch_num"] = 0
        #date
        try:
            date = soup1.find("div", id="date").find("yt-formatted-string").get_text() #上传日期
            print("date:" + date)
            data_arr["date"] = date
        except:
            print("date 没有采到！！！！！！！")
            data_arr["date"] = ""
        #up_num
        try:
            up_num = soup1.find("div",id = "menu-container").find_all("a", class_="yt-simple-endpoint style-scope ytd-toggle-button-renderer")[0].find("yt-formatted-string", id="text").get_text() #喜欢数
            up_num = StringToNum(up_num)
            print("up_num:" ,up_num)
            data_arr["up_num"] = up_num
        except:
            print("up_num 没有采到！！！！！！！")
            data_arr["up_num"] = 0
        #down_num
        try:
            down_num = soup1.find("div",id = "menu-container").find_all("a", class_="yt-simple-endpoint style-scope ytd-toggle-button-renderer")[1].find("yt-formatted-string", id="text").get_text() #踩数
            down_num = StringToNum(down_num)
            print("down_num:" ,down_num)
            data_arr["down_num"] = down_num
        except:
            print("down_num 没有采到！！！！！！！")
            data_arr["down_num"] = 0
        #uploader info
        uploader_info = {}
        try:
            uploader = soup1.find("div", id="meta").find("div", id="text-container").find("a",class_="yt-simple-endpoint style-scope yt-formatted-string").get_text()
            home_url = "https://www.youtube.com/user/"+uploader
            print("uploader:" + uploader) #上传作者
            uploader_info["uploader"] = uploader
            uploader_info["home_url"] = home_url
        except:
            print("uploader 没有采到！！！！！！！")
            uploader_info["uploader"] = ""
            uploader_info["home_url"] = ""
        #subscribe_num
        try:
            subscribe_num = soup1.find("div", id="meta").find("yt-formatted-string", id="owner-sub-count").get_text()
            print("subscribe_num:",subscribe_num) #订阅数
            subscribe_num = StringToNum(subscribe_num)
            uploader_info["subscribe_num"] = subscribe_num
        except:
            print("subscribe_num 没有采到！！！！！！！")
            uploader_info["subscribe_num"] = ""
        #ytid
        try:
            uploader_info["yter_id"] = soup1.find("ytd-video-secondary-info-renderer",class_ = "style-scope ytd-watch-flexy").find("div",id = "upload-info")\
                .find("a",class_ = "yt-simple-endpoint style-scope yt-formatted-string")["href"].replace("/channel/","")
        except:
            uploader_info["yter_id"] = ""
        #comment_num
        try:
            comment_num = soup1.find("ytd-comments",id="comments").find("ytd-item-section-renderer",id="sections").find("yt-formatted-string",class_="count-text style-scope ytd-comments-header-renderer").get_text()
            print("comment_num:" + comment_num) #评论
            comment_num = StringToNum(comment_num)
            data_arr["comment_num"] = comment_num
        except:
            print("comment_num 没有采到！！！！！！！")
            data_arr["comment_num"] = 0
        #爬取每个视频下方的评论信息
        for num in range(0, comment_scale):
            index += 1
            js = "window.scrollTo(0, " + str(200 * (index * 2)) + ");"
            driver1.execute_script(js)
            time.sleep(1)
        res = driver1.page_source
        soup = BeautifulSoup(res, 'html.parser')

        ids = [i[0] for i in models.YoutubeAccount.objects.distinct().values_list('ytid')]
        if uploader_info["yter_id"] not in ids:
        #爬取每个视频发布者的信息
            uploader_account = getYoutuberInfo(uploader_info)
        else:
            print("这个博主已经爬过了")
            uploader_account = YoutubeAccount.objects.get(ytid=uploader_info["yter_id"])
        data_arr["uploader_info"] = uploader_info

        video = YoutubeVideo(uploader = uploader_account,ytid = data_arr["ytid"],title=data_arr["title"],watch_count = data_arr["watch_num"],upload_date = data_arr["date"],
                             up_count = data_arr["up_num"],down_count = data_arr["down_num"],comment_count = data_arr["comment_num"],url = data_arr["video_url"])
        video.save()
        comments_info = get_Comment_detail(soup,driver1,video)
        data_arr["comments_info"] = comments_info
        driver1.quit()

def getVideoUrl(key_word):
    query_url = 'https://www.youtube.com/results?search_query='+key_word #新加坡冠状病毒 过滤从最高播放量排序
    try:
        driver.get(query_url)
    except TimeoutException as e:
        print(query_url,"失败了")
        driver.execute_script('window.stop()')  # 终止页面加载
    index = 0
    for num in range(0,video_scale):
        index +=1
        js = "window.scrollTo(0, "+str(200*(index*2))+");"
        driver.execute_script(js)
        time.sleep(1)
    arr_urls = []                                       #存储视频链接的数组
    res = driver.page_source
    soup = BeautifulSoup(res, 'html.parser')
    try:
        items = soup.find('div', id='contents').find_all("ytd-video-renderer",class_="style-scope ytd-item-section-renderer")
        for item in items:
            try:
                url = "https://www.youtube.com"+item.find("a", id="thumbnail").attrs["href"]  #获得视频的url
                arr_urls.append(url)
            except:
                pass
    except Exception as e:
        print(e)
    print("got all movie urls")
    urlToCsv(arr_urls, key_word)

    driver.quit()
    return arr_urls



if __name__ == '__main__':
    key_words = open("./keywords.txt",encoding = "utf8").readlines()
    key_words = [i.strip() for i in key_words]
    for key_word in key_words:
        sub_path = "./data/"+key_word+"/"
        if os.path.exists(sub_path)==False:              
            os.mkdir(sub_path, mode=0o777)
        start1 = datetime.datetime.now()
        arr_urls = getVideoUrl(key_word)
        ################################################################################################################
        for counter, url in enumerate(arr_urls):#根据视频URL爬取每个视频的详细信息（包含评论信息）。
            getVideoDetail(url)
        ################################################################################################################
        end1 = datetime.datetime.now()
        print('爬取'+key_word+'数据完成 总计用时 ：')
        print(end1-start1)