from abc import ABC, abstractmethod

'''
'''
class CodeSkeleton(ABC):
    
    @abstractmethod
    def set_config_file_path(self):
        pass
    
    @abstractmethod
    def get_detail_info_from_html(self, bs_obj):
        pass
    
    @abstractmethod
    def data_insert_to_es(self):
        pass
    
    @abstractmethod
    def player_img_download(self):
        pass