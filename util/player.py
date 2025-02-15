from dataclasses import dataclass

@dataclass
class MySchool:
    primary_school: str ## 초등학교
    junior_high_school: str ## 중학교
    high_school: str ## 고등학교 
    college: str ## 대학교 
    
@dataclass
class Player:
    name: str
    position: str
    back_number: str
    birthday: str
    height: int 
    alma_mater: MySchool