from threading import Thread
import requests
import json
import time
import logging
import sys

logger = logging.getLogger(__name__)
file = logging.FileHandler(filename=__name__, mode='w')
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(message)s")

logger.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(file)
logger.addHandler(handler)


class Download:

  def __init__(self, targetUrl: str = None, targetPath: str = None, data: dict = None, rateLimit: int = 1) -> None:
      self.targetUrl = targetUrl
      self.targetPath = targetPath
      self.data = data
      self.results = []
      self.lastRequest = None
      self.rateLimit = rateLimit

  def start(self):
    logger.info('Starting...')
    self.lastRequest = time.time()
    response = requests.post(self.targetUrl, json=self.data)
    logger.info(f'Page 1: {response}')
    assert response.ok, (response.reason, response.headers)
    json = response.json()
    pageData = json['Pagination']
    pageTotal = pageData['PageTotal']
    results = json['Results']
    self.results.extend(results)

    ts = []
    for page in list(range(2,pageTotal+1)):
       t = Thread(target=self.worker, args=(page,))
       ts.append(t)

    for t in ts:
      self.wait()
      t.start()

    for t in ts:
      t.join()

    self.save()
    logger.info(f'Saved.')


  def save(self):
    with open(self.targetPath, 'w') as f:
      f.write(json.dumps(self.results))


  def worker(self, page: int = 0):
    self.lastRequest = time.time()
    data = self.data
    data['body']['from'] = (page-1) * data['body']['size']
    response = requests.post(self.targetUrl, json=self.data)
    logger.info(f'Page {page}: {response}')
    assert response.ok, (response.reason, response.headers)
    json = response.json()
    results = json['Results']
    self.results.extend(results)


  def wait(self):
    rate = 1 / (time.time() - self.lastRequest + 0.001)
    while rate > self.rateLimit:
      rate = 1 / (time.time() - self.lastRequest + 0.001)
    return True


if __name__ == "__main__":

  gearquery = {
  "indexes": "item",
  "columns": "Name,ItemSearchCategory.Category,ItemSearchCategory.Name,ItemSearchCategory.ID,Stats,LevelEquip,ItemKind.ID,ItemKind.Name,EquipSlotCategory,ClassJobCategory.ID,ClassJobCategory.Name",
  "body": {
    "query": {
      "bool": {
        "must": [
          {"range": {"EquipSlotCategory.ID": {"gt": "0"}}}
        ],
        "should": [
          {"range": {"Stats.Control.NQ": {"gt": "0"}}},
          {"range": {"Stats.Craftsmanship.NQ": {"gt": "0"}}},
          {"range": {"Stats.CP.NQ": {"gt": "0"}}}
        ],
        "minimum_should_match": 1
      }
    },
    "from": 0,
    "size": 100,
    "sort": "LevelEquip"
  }
}

  url = 'https://xivapi.com/search'

  dl = Download(targetUrl=url, targetPath='crafting/geardb.json', data=gearquery, rateLimit=5)
  dl.start()