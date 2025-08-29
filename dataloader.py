import pandas as pd

class Dataloader:

    def __init__(self,file_path):
        self.df=pd.read_csv(file_path)
    
        