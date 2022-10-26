import requests
from bs4 import BeautifulSoup
import json

class IDOS():
    # Class variables
    # SITE DATA
    DEPARTURES = "https://idos.idnes.cz/vlakyautobusymhdvse/odjezdy/"
    CONNECTION = "https://idos.idnes.cz/vlakyautobusymhdvse/spojeni/"

    def __init__(self):
        if not self._is_up():
            print("ERR: IDOS SITE DOWN")
            print("EXITING")
            quit()

    def _is_up(self):
        OK_STATUS = 200
        if requests.get(self.CONNECTION).status_code != OK_STATUS:
            return False
        return True
    
    def get_site_html(self,site):
        return requests.get(site).text

    def get_departures(self,stop:str):
        stop = stop.replace(" ","+")
        req_url = self.DEPARTURES + f"vysledky/?f={stop}&fc=302003"
        # print(req_url)
        html = self.get_site_html(req_url)
        parser = BeautifulSoup(html,"html.parser")
        try:
            rows = parser.find(id="col-content").find("tbody").find_all("tr",{"class":"dep-row-first"})
            outputList = list()
            for row in rows:
                data = row.find_all("h3")
                direction = str(data[0].text).strip()
                route_num = str(data[1].text).strip()
                departure_time = str(data[2].text).strip()
                outputList.append([direction,route_num,departure_time])
            return outputList
        except:
            print(f"Departures for {stop} not found")
            return False
    
    def get_connection(self,start_stop:str,end_stop:str):
        start_stop = start_stop.replace(" ","+")
        end_stop = end_stop.replace(" ","+")
        req_url = self.CONNECTION + f"vysledky/?f={start_stop}&t={end_stop}&fc=302003&tc=302003"
        print(req_url)
        html = self.get_site_html(req_url)
        parser = BeautifulSoup(html,"html.parser")
        try:
            boxes = parser.find(id="col-content").find_all("div",{"class":"detail-box"})
            output_data = list()
            for box in boxes:
                connection = {}
                departure_info = box.find("h2").text
                connection["departure_info"] = departure_info
                print(departure_info)
                box_info = box.find("div",{"class","line-item"}).find_all("div",{"class":"outside-of-popup"})
                for item in box_info:
                    connection_name = item.find("div",{"class":"line-title"}).find("h3").text.strip()
                    connection_info = item.find("ul").find_all("li")
                    connection_data = []
                    data_sub = {
                        "connection_name":connection_name,
                        "start_end_stops":[],
                        "start_end_times":[]
                    }
                    print(connection_name)
                    for entry in connection_info:
                        time = entry.find("p",{"class":"time"}).text
                        station = entry.find("p",{"class":"station"}).text.split("  ")[0]
                        data_sub ["start_end_stops"].append(station)
                        data_sub ["start_end_times"].append(time)
                        print(time,station)
                    connection_data.append(data_sub)
                    connection["connection_data"] = connection_data
                output_data.append(connection)
                print()
            return output_data

        except Exception as e:
            print(e)
            return False
