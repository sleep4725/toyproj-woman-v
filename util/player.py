from dataclasses import dataclass

'''
@author Teddy
'''
@dataclass
class MySchool:
    primary_school: str ## 초등학교
    junior_high_school: str ## 중학교
    high_school: str ## 고등학교 
    college: str ## 대학교 
    
@dataclass
class Player:
    team_name: str
    name: str
    position: str
    back_number: str
    birthday: str
    height: int 
    alma_mater: MySchool