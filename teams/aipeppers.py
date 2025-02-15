import yaml
from yaml.error import YAMLError
from pathlib import Path
PROJ_ROOT_PATH = Path(__file__).resolve().parents[1] 
from typing import Dict, Any
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