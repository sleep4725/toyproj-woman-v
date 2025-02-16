from typing import List, Any, Dict
from elasticsearch import Elasticsearch as ES
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import RequestError, ConnectionTimeout
'''
@author Teddy
@email sleep4725@naver.com
'''
class EsService:
    
    @classmethod 
    def es_cluster_health_check(cls, es_client: ES):
        ''' es cluster의 health 를 확인하는 함수 
        (1) 'yellow' or 'green' 인 경우 정상 
        (2) 'red' 인 경우 문제 
        
        :param es_client:
        :return:
        '''
        try:
            response = es_client.cluster.health()
            health_color :str= response.get('status', 'error')
            if health_color in ["yellow", "green"]:
                return True
            elif health_color == "red":
                return False
            else:
                raise ValueError(f"Unexpected response status: {health_color}") 
        except (ConnectionTimeout, RequestError) as err:
            print(err)
            return False
    
    @classmethod 
    def do_bulk_insert(cls, es_client: ES, actions: List[Dict[str, Any]]):
        '''
        :param es_client:
        :param actions:
        '''
        try:
            bulk(es_client, actions)
        except:
            pass