import sys
import yaml
from pathlib import Path
PROJ_ROOT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(PROJ_ROOT_PATH.__str__())
from typing import Dict, Any, Optional, List
from elasticsearch import Elasticsearch as ES
import warnings
from elasticsearch.exceptions import ElasticsearchWarning
warnings.simplefilter('ignore', ElasticsearchWarning)
from elasticsearch.exceptions import ConnectionTimeout, ConnectionError
from urllib3.exceptions import NewConnectionError
from service.es_service import EsService
from batch_exception.es_error import *
'''
@author Teddy
'''
class EsClient:
    
    @classmethod 
    def get_es_client(cls)-> ES:
        '''
        :param:
        :return:
        '''
        es_conn_filepath :Path= PROJ_ROOT_PATH.joinpath("config/client/es-conn.yaml")
        if not es_conn_filepath.exists():
            raise FileNotFoundError(f"파일({es_conn_filepath})이 존재하지 않습니다.")

        try:
            with es_conn_filepath.open("r", encoding="utf-8") as fr:
                es_conn :Dict[str, Any]= yaml.safe_load(fr)
                
                schema :Optional[str]= es_conn.get("schema")
                port :Optional[int]= es_conn.get("port")
                hosts :Optional[List[str]]= es_conn.get("hosts")
                
                if not all([schema, port, hosts]):
                    raise ValueError(f"설정값의 누락이 있습니다. schema-> {schema}, port-> {port}, hosts-> {hosts}")
                es_client = ES([f"{schema}://{eh}:{port}" for eh in hosts])
                if EsService.es_cluster_health_check(es_client):
                    return es_client
                else:
                    raise EsClusterError(f"ES cluster healt에 문제가 있는 것으로 보입니다.")
        except yaml.YAMLError as err:
            print(err)
        except (ConnectionTimeout, ConnectionError, NewConnectionError, ConnectionRefusedError) as err:
            print(err)