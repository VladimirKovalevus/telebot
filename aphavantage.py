
import json
import requests
import numpy

class AlphaApiHelper:
    api_key = ''
    var10='TIME_SERIES_DAILY_ADJUSTED'

    def __init__(self,apikey) -> None:
        self.api_key = apikey
    
    def get_sheet_status(self,name):
        url = f"https://www.alphavantage.co/query?function={self.var10}&symbol={name}&apikey={self.api_key}"
        responce = requests.get(url=url)
        data = json.loads(responce.text)
        return data
    
    def analyze(self,data):
      last = 0;
      res = []
      for i in data:
        for j in data[i]['4. close']:
          if j.isdigit():
            if last==0:
              last = float(j)
            else:
              res.append((float(j)-last)/last)
      
      deviation = numpy.std(res)
      t = 0.03
      m = 0.05

      return (t/(deviation-m))


