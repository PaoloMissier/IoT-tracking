
import requests
from bs4 import BeautifulSoup


def main():
    l = ["created_at", "field1" , "field2", "name"]
    fieldList = [field for field in l if "field" in field]
    print(fieldList)


    # tag = 'temp'
    # # requests.get('https://github.com', verify='/path/to/certfile') // need to verify cert for later
    # fullList = list()
    # pageIncrement = 1
    # while True:
    #     pageList = list()
    #     url = 'https://thingspeak.com/channels/public?page={}&tag={}'.format(pageIncrement, tag)
    #     r = requests.get(url, verify=False) #skip cert check for now
    #     soup = BeautifulSoup(r.text, "html.parser")
    #     data = soup.find_all('a', class_='link-no-hover')
    #     for link in soup.find_all('a', class_='link-no-hover'):
    #         # get link only the channel link
    #         pageList.append(link.get('href'))
    #
    #     if not pageList:
    #         break
    #     fullList.extend(pageList)
    #     print(pageList)
    #     pageIncrement += 1
    #
    # print(fullList)[fieldList for fieldList in webCh["channel"].keys() if "field" not in fieldList]




if __name__ == '__main__':
    main()  # bring in ipaddress of the broker