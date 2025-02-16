import re
import sys
import yaml
from yaml.error import YAMLError
from pathlib import Path
PROJ_ROOT_PATH = Path(__file__).resolve().parents[1] 
sys.path.append(PROJ_ROOT_PATH.__str__())
from typing import Dict, Any, Optional, List
import bs4
import requests
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch as ES
from selenium.webdriver.chrome.webdriver import WebDriver
from engine.engine_selenium import EngineSelenium
from batch_exception.crwl_error import ElementNotFoundError
from util.request_util import RequestsUtil
from util.position_mapping import position_re_value_return
from util.player import Player, MySchool
from util.es_index import EsIndex
from client.es_client import EsClient
from service.es_service import EsService
from skeleton.code_skeleton import CodeSkeleton
'''
@author Teddy
'''
class Kixx(CodeSkeleton):
    
    TEAM_NAME = "kixx"
    def __init__(self):
        self.config :str= Kixx.set_config_file_path()
        self.img_file_path :str= PROJ_ROOT_PATH.joinpath(f'img/{Kixx.TEAM_NAME}').__str__()
        self.players :Optional[List[Dict[str, Dict[str, str]]]]= []
        self.birthday_format :str= r"(\d{4})년 (\d{2})월 (\d{2})일"
        self.es_client :ES= EsClient.get_es_client()
        self.es_index :str= EsIndex.woman_volleyball_es_index
        self.es_actions :List[Dict[str, Any]]= []
        
    def check_requests_status(self, response:requests.models.Response)-> bool:
        '''
        :param response:
        :return:
        '''
        if response.status_code == 200:
            return True
        else:
            return False
    
    def p_name_parcing(self, name: str)-> str:
        '''
        :param name:
        '''
        name :str= name.split(".")[1]
        name :str= name.strip()
        return name 
    
    def get_player_information(self):
        '''
        :param:
        :return:
        '''
        crwler :WebDriver= EngineSelenium.get_selenium_client()
        try:
            crwler.get(self.config.get('url'))
            bs_obj = BeautifulSoup(crwler.page_source ,"html.parser")
            ul_tag :Optional[bs4.element.Tag]= bs_obj.select_one("ul.teamListUl")
            if not ul_tag: 
                raise ElementNotFoundError(f"Expected 'ul.teamListUl' element not found") 
            li_tags :Optional[bs4.element.ResultSet]= ul_tag.select("li")
            for idx, l in enumerate(li_tags):
                l_tag :bs4.element.Tag= l
                href :Optional[str]= self.config.get("base_url") + l_tag.select_one("a").attrs['href']
                img :Optional[str]= l_tag.select_one("a > div.pPhotoWrap > img").attrs['src']
                p_name_tag :bs4.element.Tag= l_tag.select_one("a > div.pInfoWrap > span.pInfo")
                p_name :str= p_name_tag.string
                
                self.players.append({
                  f"{idx + 1}": {
                      "href": href,
                      "img": img,
                      "name": self.p_name_parcing(name= p_name)
                  }
                })
        except Exception as err:
            print(err)
        finally: 
            crwler.close()

    def player_img_download(self):
        '''
        :param:
        '''
        for i, p in enumerate(self.players):
            for k in p.keys():
                response = requests.get(
                            p[k]['img'],
                            headers= RequestsUtil.headers,
                            timeout= 10
                )
                if self.check_requests_status(response= response):
                    with open(f"{self.img_file_path:s}/{Kixx.TEAM_NAME:s}_{i+1:02d}_{p[k]['name']:s}.png", "wb") as file:
                        for chunk in response.iter_content(1024):  # 1KB씩 다운로드
                            file.write(chunk)
                else:
                    '''
                    '''
        
    def cllct_player_information(self):
        '''
        :param:
        :return:
        '''
        for i, p in enumerate(self.players):
            for k in p.keys():
                try:
                    response :requests.models.Response= requests.get(
                        p[k]['href'],
                        headers= RequestsUtil.headers,
                        timeout= 10
                    )
                    if not self.check_requests_status(response): pass
                    bs_obj = BeautifulSoup(response.text, "html.parser")
                    
                    self.es_actions.append({
                        "_index": self.es_index,
                        "_id": f"{Kixx.TEAM_NAME}_{i + 1}",
                        "_source": {**self.get_detail_info_from_html(bs_obj)}
                    })
                    
                except requests.exceptions.RequestException as err:
                    print(f"Request failed: {err}")
    
    def data_insert_to_es(self):
        '''
        :param:
        :return:
        '''
        EsService.do_bulk_insert(es_client= self.es_client, actions= self.es_actions)
  
    def get_detail_info_from_html(self, bs_obj: BeautifulSoup)-> Dict[str, Any]:
        '''
        :param bs_obj:
        :return:
        '''
        
        t_detail_info :bs4.element.Tag= bs_obj.select_one("div.tDetailInfo")
        datas_1 :Dict[str, Any]= self.get_data_tdi_1(t_detail_info)
        datas_2 :Dict[str, Any]= self.get_data_tdi_2(t_detail_info)
        datas_3 :Dict[str, Any]= self.get_data_tdi_3(t_detail_info)
        
        datas = {
            **datas_1,
            **datas_2,
            **datas_3
        }
        
        schools = datas.get("p_school") 
        women_player = Player(
            team_name= Kixx.TEAM_NAME,
            name= datas.get("p_player_name"),
            position= datas.get("p_position_name"),
            birthday= datas.get("p_birthday"),
            back_number= datas.get("p_back_number"),
            height=datas.get("p_height"),
            alma_mater= MySchool(
                primary_school= schools.get("primary_school"),
                junior_high_school= schools.get("junior_high_school"),
                high_school= schools.get("high_school"), 
                college= schools.get("college")
            )
        )
        
        result :Dict[str, Any]= asdict(women_player)
        return result
     
    def get_data_tdi_1(self, t_detail_info: BeautifulSoup)-> Dict[str, Any]:
        '''
        :param t_detail_info:
        :return:
        '''
        p = {
            "p_back_number": None,
            "p_position_name": None
        }
        
        tdi_1 :bs4.element.Tag= t_detail_info.select_one("div > div.tdi_1")
        div :bs4.element.ResultSet= tdi_1.select("div")

        for idx, d in enumerate(div):
            d_tag :bs4.element.Tag= d
            dl_tag = d_tag.select_one("dl")
            if idx == 0:
                dd_tag :bs4.element.Tag= dl_tag.select_one('dd.tDetailNumber')
                back_number :str= dd_tag.string
                p["p_back_number"] = back_number
                
            elif idx == 1:
                dd_tag :bs4.element.Tag= dl_tag.select_one('dd.tDetailPosition')            
                position_name :str= dd_tag.string
                p["p_position_name"] = position_re_value_return(position_name)
        
        return p
         
    def get_data_tdi_2(self, t_detail_info: BeautifulSoup)-> Dict[str, Any]:
        '''
        :param t_detail_info:
        :return: 
        '''
        p = {"p_player_name": None}
        tdi_2 :bs4.element.Tag= t_detail_info.select_one("div > div.tdi_2")
        strong_tag :bs4.element.Tag= tdi_2.select_one("strong")
        player_name = str(strong_tag.string).strip()
        p["p_player_name"] = player_name
        return p
        
    def get_data_tdi_3(self, t_detail_info: BeautifulSoup)-> Dict[str, Any]:
        '''
        :param t_detail_info: 
        '''
        p = {
                "p_birthday": None, 
                "p_school": {
                    "primary_school": None, 
                    "junior_high_school": None,
                    "high_school": None,
                    "college": None
                },
                "p_height": None
        }
        
        tdi_3 :bs4.element.Tag= t_detail_info.select_one("div > div.tdi_3") 
        dl_tags :bs4.element.ResultSet= tdi_3.select("dl")
        for d in dl_tags:
            d_tag :bs4.element.Tag= d
            dt_tag = d_tag.select_one("dt")
            if str(dt_tag.string).strip() == "생년월일":
                dd_tag = d_tag.select_one("dd")
                formatted_date :str= re.sub(self.birthday_format, r"\1-\2-\3", str(dd_tag.string).strip())
                p["p_birthday"] = formatted_date
            elif str(dt_tag.string).strip() == "출신교":
                dd_tag = d_tag.select_one("dd")
                schools :List[str]= [str(sch).strip() for sch in str(dd_tag.string ).strip().split("-") if sch]
                for s in schools:
                    if s[-1] == "초":
                        p["p_school"]["primary_school"] = s
                    elif s[-1] == "중":
                        p["p_school"]["junior_high_school"] = s 
                    elif s[-1] == "고":
                        p["p_school"]["high_school"] = s
                    elif s[-1] == "대":
                        p["p_school"]["college"] = s
            elif str(dt_tag.string).strip() == "신장":
                dd_tag = d_tag.select_one("dd")
                height = str(dd_tag.string).strip()
                height :str= height.replace("cm", "")
                p["p_height"] = int(height, base= 0xA)
        
        return p
 
    @classmethod
    def set_config_file_path(cls)-> Dict[str, Any]:
        '''
        :param:
        :return:
        '''
        config_file_path :Path= PROJ_ROOT_PATH.joinpath(f'config/team/{cls.TEAM_NAME}.yaml')
        if not config_file_path.exists:
            raise FileNotFoundError(f"파일({config_file_path})이 존재하지 않습니다.")
        
        try:
            with config_file_path.open("r", encoding="utf-8") as fr:
                _config :Dict[str, Any]= yaml.safe_load(fr)
                return _config
        except YAMLError as err:
            print(err)

    def __del__(self):
        try:
            self.es_client.close()
        except:
            pass
        
if __name__ == "__main__":
    o = Kixx()
    o.get_player_information()
    o.player_img_download()
    o.cllct_player_information()
    o.data_insert_to_es()