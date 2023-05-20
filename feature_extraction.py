import ipaddress
import re
import urllib.request
from bs4 import BeautifulSoup
import socket
import requests
from googlesearch import search
import whois
from datetime import datetime,date
import time
from dateutil.parser import parse as date_parse


# Months_calculating
def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

# Generate data set by extracting the features from the URL
def generate_data_set(URL):

    data_set = []

    # Converts the given URL into standard format
    if not re.match(r"^https?", URL):
        URL = "http://" + URL


    # Stores the response of the given URL
    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, 'html.parser')
    except:
        response = ""
        soup = -999


    # Extracts domain from the given URL
    domain = re.findall(r"://([^/]+)/?", URL)[0]
    if re.match(r"^www.",domain):
        domain = domain.replace("www.","")

    # Requests all the information about the domain
    whois_response = whois.whois(domain)

    rank_checker_response = requests.post("https://www.checkpagerank.net/index.php", {
        "name": domain
    })

    # Extracts global rank of the website
    try:
        global_rank = int(re.findall(r"Global Rank: ([0-9]+)", rank_checker_response.text)[0])
    except:
        global_rank = -1

    # 1.Has_IP_Address
    try:
        ipaddress.ip_address(URL)
        data_set.append(-1)
    except:
        data_set.append(1)

    # 2.Length of_URL
    if len(URL) < 54:
        data_set.append(1)
    elif len(URL) >= 54 and len(URL) <= 75:
        data_set.append(0)
    else:
        data_set.append(-1)

    # 3.uses_shorting_Service
    match=re.search('bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                    'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                    'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                    'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                    'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                    'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
                    'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|tr\.im|link\.zip\.net',URL)
    if match:
        data_set.append(-1)
    else:
        data_set.append(1)

    # 4.has_At_Symbol
    if re.findall("@", URL):
        data_set.append(-1)
    else:
        data_set.append(1)

    # 5.Has_double_slash_redirecting
    list=[x.start(0) for x in re.finditer('//', URL)]
    if list[len(list)-1]>6:
        data_set.append(-1)
    else:
        data_set.append(1)

    # 6.Has_prefix_Suffix
    if re.findall(r"https?://[^\-]+-[^\-]+/", URL):
        data_set.append(-1)
    else:
        data_set.append(1)

    # 7.Has_Sub_Domain
    if len(re.findall("\.", URL)) == 1:
        data_set.append(1)
    elif len(re.findall("\.", URL)) == 2:
        data_set.append(0)
    else:
        data_set.append(-1)

    # 8.ssl_State
    try:
        if response.text:
            data_set.append(1)
    except:
        data_set.append(-1)

    # 9.domain_reg_length
    expiration_date = whois_response.expiration_date
    registration_length = 0
    try:
        expiration_date = min(expiration_date)
        today = time.strftime('%Y-%m-%d')
        today = datetime.strptime(today, '%Y-%m-%d')
        registration_length = abs((expiration_date - today).days)

        if registration_length / 365 <= 1:
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(-1)

    # 10.Has_favicon
    if soup == -999:
        data_set.append(-1)
    else:
        try:
            for head in soup.find_all('head'):
                for head.link in soup.find_all('link', href=True):
                    dots = [x.start(0) for x in re.finditer('\.', head.link['href'])]
                    if URL in head.link['href'] or len(dots) == 1 or domain in head.link['href']:
                        data_set.append(1)
                        raise StopIteration
                    else:
                        data_set.append(-1)
                        raise StopIteration
        except StopIteration:
            pass

    #11. Uses_port
    try:
        port = domain.split(":")[1]
        if port:
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(1)

    #12. Has_HTTPS_token
    if re.findall(r"^https://", URL):
        data_set.append(1)
    else:
        data_set.append(-1)

    #13. Uses_Request_URL
    i = 0
    success = 0
    if soup == -999:
        data_set.append(-1)
    else:
        for img in soup.find_all('img', src= True):
           dots= [x.start(0) for x in re.finditer('\.', img['src'])]
           if URL in img['src'] or domain in img['src'] or len(dots)==1:
              success = success + 1
           i=i+1

        for audio in soup.find_all('audio', src= True):
           dots = [x.start(0) for x in re.finditer('\.', audio['src'])]
           if URL in audio['src'] or domain in audio['src'] or len(dots)==1:
              success = success + 1
           i=i+1

        for embed in soup.find_all('embed', src= True):
           dots=[x.start(0) for x in re.finditer('\.',embed['src'])]
           if URL in embed['src'] or domain in embed['src'] or len(dots)==1:
              success = success + 1
           i=i+1

        for iframe in soup.find_all('iframe', src= True):
           dots=[x.start(0) for x in re.finditer('\.',iframe['src'])]
           if URL in iframe['src'] or domain in iframe['src'] or len(dots)==1:
              success = success + 1
           i=i+1

        try:
           percentage = success/float(i) * 100
           if percentage < 22.0 :
              data_set.append(1)
           elif((percentage >= 22.0) and (percentage < 61.0)) :
              data_set.append(0)
           else :
              data_set.append(-1)
        except:
            data_set.append(1)



    #14. Has_URL_of_Anchor
    percentage = 0
    i = 0
    unsafe=0
    if soup == -999:
        data_set.append(-1)
    else:
        for a in soup.find_all('a', href=True):
       
            if "#" in a['href'] or "javascript" in a['href'].lower() or "mailto" in a['href'].lower() or not (URL in a['href'] or domain in a['href']):
                unsafe = unsafe + 1
            i = i + 1


        try:
            percentage = unsafe / float(i) * 100
        except:
            data_set.append(1)

        if percentage < 31.0:
            data_set.append(1)
        elif ((percentage >= 31.0) and (percentage < 67.0)):
            data_set.append(0)
        else:
            data_set.append(-1)

    #15. Has_Links_in_tags
    i=0
    success =0
    if soup == -999:
        data_set.append(-1)
    else:
        for link in soup.find_all('link', href= True):
           dots=[x.start(0) for x in re.finditer('\.',link['href'])]
           if URL in link['href'] or domain in link['href'] or len(dots)==1:
              success = success + 1
           i=i+1

        for script in soup.find_all('script', src= True):
           dots=[x.start(0) for x in re.finditer('\.',script['src'])]
           if URL in script['src'] or domain in script['src'] or len(dots)==1 :
              success = success + 1
           i=i+1
        try:
            percentage = success / float(i) * 100
        except:
            data_set.append(1)

        if percentage < 17.0 :
           data_set.append(1)
        elif((percentage >= 17.0) and (percentage < 81.0)) :
           data_set.append(0)
        else :
           data_set.append(-1)

        #16. SFH
        for form in soup.find_all('form', action= True):
           if form['action'] =="" or form['action'] == "about:blank" :
              data_set.append(-1)
              break
           elif URL not in form['action'] and domain not in form['action']:
               data_set.append(0)
               break
           else:
                 data_set.append(1)
                 break

    #17. Submits_to_email
    if response == "":
        data_set.append(-1)
    else:
        if re.findall(r"[mail\(\)|mailto:?]", response.text):
            data_set.append(1)
        else:
            data_set.append(-1)

    #18.  Has_Abnormal_URL
    if response == "":
        data_set.append(-1)
    else:
        if response.text == "":
            data_set.append(1)
        else:
            data_set.append(-1)

    #19.Has_Redirect
    if response == "":
        data_set.append(-1)
    else:
        if len(response.history) <= 1:
            data_set.append(-1)
        elif len(response.history) <= 4:
            data_set.append(0)
        else:
            data_set.append(1)

    #20. Has_on_mouseover
    if response == "" :
        data_set.append(-1)
    else:
        if re.findall("<script>.+onmouseover.+</script>", response.text):
            data_set.append(1)
        else:
            data_set.append(-1)

    #21. Allows_RightClick
    if response == "":
        data_set.append(-1)
    else:
        if re.findall(r"event.button ?== ?2", response.text):
            data_set.append(1)
        else:
            data_set.append(-1)

    #22. Has_popUpWidnow
    if response == "":
        data_set.append(-1)
    else:
        if re.findall(r"alert\(", response.text):
            data_set.append(1)
        else:
            data_set.append(-1)

    #23. Has_Iframe
    if response == "":
        data_set.append(-1)
    else:
        if re.findall(r"[<iframe>|<frameBorder>]", response.text):
            data_set.append(1)
        else:
            data_set.append(-1)

    #24. Domain_age
    if response == "":
        data_set.append(-1)
    else:
        try:
            registration_date = re.findall(r'Registration Date:</div><div class="df-value">([^<]+)</div>', whois_response.text)[0]
            if diff_month(date.today(), date_parse(registration_date)) >= 6:
                data_set.append(-1)
            else:
                data_set.append(1)
        except:
            data_set.append(1)

    #25. Has_DNSRecord
    dns = 1
    try:
        dns = whois.whois(domain)
    except:
        dns=-1
    if dns == -1:
        data_set.append(-1)
    else:
        if registration_length / 365 <= 1:
            data_set.append(-1)
        else:
            data_set.append(1)

    #26. Has_web_traffic
    try:
        if global_rank> 0 and global_rank < 100000:
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(1)

    

    #27. page_Rank
    try:
        if global_rank > 0 and global_rank < 100000:
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(1)

    #28. _Google_Indexed
    site=search(URL, 5)
    if site:
        data_set.append(1)
    else:
        data_set.append(-1)

    #29. Has_Links_pointing_to_page
    if response == "":
        data_set.append(-1)
    else:
        number_of_links = len(re.findall(r"<a href=", response.text))
        if number_of_links == 0:
            data_set.append(1)
        elif number_of_links <= 2:
            data_set.append(0)
        else:
            data_set.append(-1)

    #30. Has_Statistical_report
    URL_match=re.search('at\.ua|usa\.cc|baltazarpresentes\.com\.br|pe\.hu|esy\.es|hol\.es|sweddy\.com|myjino\.ru|96\.lt|ow\.ly',URL)
    try:
        ip_address=socket.gethostbyname(domain)
        ip_match=re.search('146\.112\.61\.108|213\.174\.157\.151|121\.50\.168\.88|192\.185\.217\.116|78\.46\.211\.158|181\.174\.165\.13|46\.242\.145\.103|121\.50\.168\.40|83\.125\.22\.219|46\.242\.145\.98|'
                           '107\.151\.148\.44|107\.151\.148\.107|64\.70\.19\.203|199\.184\.144\.27|107\.151\.148\.108|107\.151\.148\.109|119\.28\.52\.61|54\.83\.43\.69|52\.69\.166\.231|216\.58\.192\.225|'
                           '118\.184\.25\.86|67\.208\.74\.71|23\.253\.126\.58|104\.239\.157\.210|175\.126\.123\.219|141\.8\.224\.221|10\.10\.10\.10|43\.229\.108\.32|103\.232\.215\.140|69\.172\.201\.153|'
                           '216\.218\.185\.162|54\.225\.104\.146|103\.243\.24\.98|199\.59\.243\.120|31\.170\.160\.61|213\.19\.128\.77|62\.113\.226\.131|208\.100\.26\.234|195\.16\.127\.102|195\.16\.127\.157|'
                           '34\.196\.13\.28|103\.224\.212\.222|172\.217\.4\.225|54\.72\.9\.51|192\.64\.147\.141|198\.200\.56\.183|23\.253\.164\.103|52\.48\.191\.26|52\.214\.197\.72|87\.98\.255\.18|209\.99\.17\.27|'
                           '216\.38\.62\.18|104\.130\.124\.96|47\.89\.58\.141|78\.46\.211\.158|54\.86\.225\.156|54\.82\.156\.19|37\.157\.192\.102|204\.11\.56\.48|110\.34\.231\.42',ip_address)
        if URL_match:
            data_set.append(-1)
        elif ip_match:
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        print ('Connection problem. Please check your internet connection!')


    print (data_set)
    return data_set
