class Maker():

    cash : float 
    asset : float

    def __init__(self) -> None:
        self.cash = 0 
        self.asset = 0

    def __str__(self) -> str:
        return "[maker] cash:{cash} asset:{asset}".format(cash = self.cash, asset = self.asset)
        
    