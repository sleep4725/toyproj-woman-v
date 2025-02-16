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
@email sleep4725@naver.com
'''
class AiPeppers:
    
    TEAM_NAME = "aipeppers"
    def __init__(self):
        self.config :str= AiPeppers.set_config_file_path()

    @classmethod
    def set_config_file_path(cls)-> Dict[str, Any]:
        '''
        :param:
        :return:
        '''
        config_file_path :Path= PROJ_ROOT_PATH.joinpath(f'config/{cls.TEAM_NAME}.yaml')
        if not config_file_path.exists:
            raise FileNotFoundError(f"파일({config_file_path})이 존재하지 않습니다.")
        
        try:
            with config_file_path.open("r", encoding="utf-8") as fr:
                _config :Dict[str, Any]= yaml.safe_load(fr)
                return _config
        except YAMLError as err:
            print(err)