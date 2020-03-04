import sys, xbmcgui, xbmcplugin, xbmcaddon
import os, requests, re, json
from urllib import urlencode, quote_plus
from urlparse import parse_qsl
import pickle
#from http import cookiejar Changed to python 2.7 cookiejar
from bs4 import BeautifulSoup
import cookielib  ##python 2.7 cookiejar

addon           = xbmcaddon.Addon(id='plugin.video.gg')
addon_url       = sys.argv[0]
addon_handle    = int(sys.argv[1])
addon_icon      = addon.getAddonInfo('icon')
addon_BASE_PATH = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))

#MENU_DATA = os.path.join("/tmp/","gg_menu_data.txt")
#COOKIE_DATA = os.path.join("/tmp/","gg_cookie_data.txt")


MENU_DATA = xbmc.translatePath(os.path.join('special://temp','gg_menu_data.txt'))
COOKIE_DATA = xbmc.translatePath(os.path.join('special://temp','gg_cookie_data.tx'))


login_url = "https://grapplersguide.com/amember/login"

base_url = "https://grapplersguide.com/portal/"

sections_url = "https://grapplersguide.com/portal/sections/"

##Global cookieJar
#CJ = cookiejar.CookieJar()
CJ = cookielib.CookieJar()  ##Changed to python 2.7 Cookiejar


sections_dict = {}   # Dictionary for sections 


headers={
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
    "sec-fetch-mode":"cors",
    "x-requested-with": "XMLHttpRequest",
    "origin": "https://grapplersguide.com"
    }

headers3={'accept': 'text/html',
 'accept-encoding': 'identity',
 'accept-language': 'en-US,en;q=0.9',
 'cache-control': 'max-age=0',
 'cookie': '__cfduid=db82a001acc01246ede940f516b680ecb1582165298; _ga=GA1.2.1963097531.1582165303; xf_user=23458%2Caed033972162e6394f427aeb988b0bc2f6ad0520; wordpress_logged_in_f28d2f47e4b372540c35e8d9a3f5424c=frsty1%7C1587349527%7CTkRajPNagfxfEuHAia0UaT7pYbojjovHGVn7uE775Tr%7C25aa530c54e6cbd09505d6ac36b5b343f47a62d08da01d232557ddda847ff2b1; amember_ru=frsty1; amember_rp=ffca47197f156ae62204d25ec0a14aaa3149d844; xf_user=23458%2Caed033972162e6394f427aeb988b0bc2f6ad0520; elementor_split_test_client_id=4d9c3d16d-421f0b72-0438-4e7e-91d1-c4b7629c3bb7; rdt_uuid=7d44a6cc-3725-4f8c-ac7a-f978eb30ec93; ac_enable_tracking=1; _fbp=fb.1.1582512676562.1230514920; tve_leads_unique=1; tl_18219_18222_77=a%3A1%3A%7Bs%3A6%3A%22log_id%22%3Bi%3A108034%3B%7D; _gid=GA1.2.564871319.1582757120; xf_session=5beaa2c39bb4b0ed9976b494fc929c13; intercom-session-ipac5lbg=UThSU2Z3ajFGL1BmY3JrMGpFeEVER2tlOXcxSXk2dXQ3M1gvNzBXbXVXMVhrc3VVS1NtTjArNGVxZ01ZeG9TUy0tU0RaODYzNGdHcmNFNGZuczlPUnlDUT09--cc7a754f03517e32229d1dafecf3e726c55484d2; xf_mce_ccv=ForumCube_DownloadingLog_ControllerPublic_Download%2CSave%2C',
 'if-modified-since': 'Wed, 26 Feb 2020 23:25:17 GMT',
 'sec-fetch-mode': 'navigate',
 'sec-fetch-site': 'none',
 'sec-fetch-user': '?1',
 'upgrade-insecure-requests': '1',
 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}    
    
def get_creds():
    """Get username and password. Return dict of username and password"""

    if len(addon.getSetting('username')) == 0 or len(addon.getSetting('password')) == 0:
        return None

    return {
        'username': addon.getSetting('username'),
        'password': addon.getSetting('password')
    }

def authorize():
    """Take in the credentials as dict['username', 'password'] and update the cookieJar"""
    creds = get_creds()
    #credentials = json.dumps({"id":creds['username'],"secret":creds['password']})

    credentials = urlencode({"amember_login": creds['username'], "amember_pass": creds['password']})

    session = requests.session()
    session.headers = headers
    my_request = session.post(login_url, data=credentials)
    global CJ
    if my_request.status_code == 200:
        CJ = my_request.cookies
        pickle_out = open(COOKIE_DATA,"wb")
        pickle.dump(CJ, pickle_out)
        pickle_out.close()

        session.close()
        return True
    else:
        #CJ = my_request.cookies
        xbmc.log("Could not get Auth Token, Session text: {0}\r\nStatus Code: {1}".format(my_request.text.encode('utf-8'), my_request.status_code),level=xbmc.LOGERROR)
        return False


def get_section_data():
    """Get HTML data from the section website. Return this data to use in a function to build the menu items"""
    session = requests.session()
    session.cookies = CJ
    session.headers = headers

    response = session.get(sections_url, headers=headers)

    #xbmc.log("Cookie_data {0}\r\nResponse Code: {1}".format(str(session.cookies ),response.status_code),level=xbmc.LOGERROR)

    if response.status_code < 400:
        return response.text
    else:
        #xbmc.log("Could not get data, line 80. Response: {0}\r\nText: {1}".format(response.status_code, response.text.encode('utf-8')),level=xbmc.LOGERROR)
        return None


####UP TO HERE###

def router(paramstring):
    """Router for kodi to select the menu item and route appropriately. """
    params = dict(parse_qsl(paramstring))

    if params:
        action = params['action']
        if action == 'listing':
            build_menu(params.get("key0"),params.get("key1"),params.get("key2"),params.get("key3"))
            
        elif action == 'forum':
            build_forum_menu(params['u'],params['t'])
            
        elif action == 'play':
            play_video(params['u'],params['t'])

        else:
            pass
    else:
        global sections_dict
        website_section_data = get_section_data() ##get the data from the section menu
        #xbmc.log("Website Data: {0}".format(website_section_data.encode('utf-8')),level=xbmc.LOGERROR)
        sections_dict = get_categories(website_section_data) #parse the menu into a dict and put into the global variable
        
        ####Using a temp file instead to save the menu data:
        pickle_out = open(MENU_DATA,"wb")
        pickle.dump(sections_dict, pickle_out)        
        pickle_out.close()

        #xbmc.log("sections_dict: {0}".format(sections_dict),level=xbmc.LOGERROR)
        build_menu() ##Build menu top level, i.e. no keys
        




def get_categories(web_data):
    """Put items into readable nested dict, and return for building the menu"""
    
    soup = BeautifulSoup(web_data, 'html.parser')
   

    #xbmc.log("soup: {0}.".format(soup),level=xbmc.LOGERROR)
    
 
    ##Grab only the section list items:
    children = soup.findChildren("li")
    
    my_dict = {}


    for child in children:
        try:
            if child['class'][0] == "_depth0":
                
                key0 = child.text.lstrip(" ").encode('utf-8')
                
               
                my_href = child.find("a")["href"]
                if len(my_href) >0:
                    my_dict[key0] = my_href             
                else:
                    my_dict[key0] = {}
            
            
            
            elif child['class'][0] == "_depth1":
                
                key1 = child.text.lstrip(" ").encode('utf-8')
                
               
                my_href = child.find("a")["href"]
                if len(my_href) >0:
                    my_dict[key0][key1] = my_href             
                else:
                    my_dict[key0][key1] = {}
                    
            
            elif child['class'][0] == "_depth2":
                key2 = child.text.lstrip(" ").encode('utf-8')

                
                my_href = child.find("a")["href"]
                if len(my_href) >0:
                    
                    my_dict[key0][key1][key2] = my_href             
                else:
                    my_dict[key0][key1][key2] = {}

                    
            elif child['class'][0] == "_depth3":            
                key3 = child.text.lstrip(" ").encode('utf-8')

                
                my_href = child.find("a")["href"]
                if len(my_href) >0:
                   
                    my_dict[key0][key1][key2][key3] = my_href                        
            else:
                pass            

           
        except:
            pass
    
    #xbmc.log("My_dict: {0}".format(my_dict),level=xbmc.LOGERROR)
    
    return my_dict




def build_menu(key0=None,key1=None,key2=None,key3=None):
    """ Build menu based on the keys. If item"""

    
    #xbmc.log("Session text: {0}".format(sections_dict),level=xbmc.LOGERROR)
    pickle_in = open(MENU_DATA,"rb")
    whole_dictionary = pickle.load(pickle_in)
 
    
    smaller_dict = return_small_dict(whole_dictionary, key0,key1,key2,key3)

    #xbmc.log("Smaller_dict type: {0}".format(str(type(smaller_dict))),level=xbmc.LOGERROR)   
    
    for my_item in smaller_dict:
        #xbmc.log("217: key0:{0}, key1:{1}, key2:{2},key3{3} ".format(key0,key1,key2,key3),level=xbmc.LOGERROR)
        #xbmc.log("my_item type: {0}".format(str(smaller_dict[my_item])),level=xbmc.LOGERROR)
        if not isinstance(smaller_dict[my_item], dict):
            ##check to see if it's a string, if so this means it's the last of the chain before the forum page of videos.
            ##If it's the last in the chain. Give it a different action so we can deal with it in a different method
            
            kodi_item = xbmcgui.ListItem(label=my_item)
            #kodi_item.setInfo(type='video', infoLabels=video_info)

            url = '{0}?action=forum&u={1}&t={2}'.format(addon_url, smaller_dict[my_item].encode('utf-8'), quote_plus(my_item))
            xbmcplugin.addDirectoryItem(addon_handle, url, kodi_item, isFolder=True)
            #xbmc.log("at last menu",level=xbmc.LOGERROR) 

        else:
            #else if it's a dict, then return the keys it is up to
            key_dict = return_key_dict(my_item, key0,key1,key2,key3)
            encoded_keys = urlencode(key_dict)
            kodi_item = xbmcgui.ListItem(label=my_item)

            #url_for_getting_data = playlist_url.format(my_item["id"])
            url = '{0}?action=listing&{1}'.format(addon_url, encoded_keys)
            xbmcplugin.addDirectoryItem(addon_handle, url, kodi_item, isFolder=True)

    ###Thats it create the folder structure
    xbmcplugin.endOfDirectory(addon_handle)



def return_key_dict(my_item, key0=None,key1=None,key2=None,key3=None):
    """Returns the key values and add my_item name to the rightmost key to allow for exploring the next menu item"""
    if not key0:
        return {"key0": my_item, "key1":None,"key2":None,"key3":None}
    elif "None" in key1:
        return {"key0": key0, "key1":my_item,"key2":None,"key3":None}
    elif "None" in key2:
        return {"key0": key0, "key1":key1,"key2":my_item,"key3":None}
    elif "None" in key3:
        return {"key0": key0, "key1":key1,"key2":key2,"key3":my_item}


def return_small_dict(whole_dictionary, key0=None,key1=None,key2=None,key3=None):
    """Takes in the entire dictionary, returns the sub dictionary based on the keys"""
    #xbmc.log("Key0:{0} Key1:'{1}', Key2:{2}, Key3:{3}".format(key0,key1,key2,key3),level=xbmc.LOGERROR) 
   
    if not key0:
        return whole_dictionary    
    elif "None" in key1:
        return whole_dictionary[key0]
    elif "None" in key2:
        return whole_dictionary[key0][key1]
    elif "None" in key3:
        return whole_dictionary[key0][key1][key2]
    else:
        return whole_dictionary[key0][key1][key2][key3]
    
    
    



def build_forum_menu(site_url,title):
    
    full_url = base_url+site_url

    forum_data = get_forum_data(site_url)
    
    
    soup = BeautifulSoup(forum_data, 'html.parser')


    forum_list = soup.findAll("a",target="_blank", href=True)    
   

    for item in forum_list:
        url_end = item["href"]
        pattern= "threads/([\w|\-|\_]+)"
        my_match = re.match(pattern,item["href"])
        name = my_match.group(1).capitalize()

        kodi_item = xbmcgui.ListItem(label=name)
        #kodi_item.setInfo(type='video', infoLabels={'genre': 'BJJ', 'plot': 'BJJ Tutorials'} )
        
        url = '{0}?action=play&u={1}&t={2}'.format(addon_url, base_url+url_end, quote_plus(name))
        xbmcplugin.addDirectoryItem(addon_handle, url, kodi_item, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)

 

def get_forum_data(site_url):

    pickle_in = open(COOKIE_DATA,"rb")
    CJ = pickle.load(pickle_in)

    session2 = requests.session()
    session2.headers = headers
    session2.cookies = CJ
    my_request2 = session2.get(site_url)

    return my_request2.text.encode('utf-8')



def play_video(r_url, title):

    url = get_video_url(r_url)

    encode_string = {}
    #encode_string = headers
    encode_string["cookie"] = create_coookie_string(CJ) 

    my_encoding = urlencode(encode_string)

    if "youtube" in url:
        #xbmc.log("Handle id: {0}".format(int(sys.argv[1])),level=xbmc.LOGERROR) 
        pattern = 'https://www.youtube.com/\w+/(\w+)\?'
        video_id = re.match(pattern, url).group(1)
        youtube_addon_url = "plugin://plugin.video.youtube/play/?video_id=" + video_id
        kodi_item = xbmcgui.ListItem(label=title,path=youtube_addon_url)
        kodi_item.setProperty('IsPlayable','True')
        kodi_item.setProperty('IsFolder','False')
        #xbmcplugin.endOfDirectory(addon_handle)
        #xbmcplugin.setResolvedUrl(addon_handle, True, kodi_item)
        #xbmc.executebuiltin("ActivateWindow(10025,{0},return)".format(youtube_addon_url))
        xbmc.executebuiltin('RunPlugin("{0}")'.format(youtube_addon_url))

    else:
        stream = url.rstrip("/") + "|" + my_encoding
        kodi_item = xbmcgui.ListItem(label=title)
        xbmc.Player().play(stream, kodi_item)


def get_video_url(r_url):
    pickle_in = open(COOKIE_DATA,"rb")
    CJ = pickle.load(pickle_in)

    session3 = requests.session()
    session3.headers = headers3
    session3.cookies = CJ
    my_request3 = session3.get(r_url)

    #xbmc.log("Request3: {0}".format(str(my_request3.text).encode('utf-8')),level=xbmc.LOGERROR)

    soup3 = BeautifulSoup(my_request3.text.encode('utf-8'),'html.parser' )
    my_find = soup3.find("a", class_="addvidnodedownload")

    if my_find:
        return my_find["href"] ##For normal forum video post with mp4 link
    else:
        return soup3.find("iframe")["src"]  ###return the youtube link instead



def create_coookie_string(cookie_jar_var):
    """takes in cookie jar item and returns a string of cookies to use in the url"""
    cookie_string = ""
    for item in cookie_jar_var.get_dict():
        cookie_string = cookie_string + item + "=" +cookie_jar_var.get_dict()[item] + "; "
    
    return cookie_string



if __name__ == '__main__':
    authorize() ##Authorize in the website first. And add the CJ data to the cookie jar (done in the method)
    router(sys.argv[2][1:])

