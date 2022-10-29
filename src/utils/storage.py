from threading import Thread
from typing import Any
import datetime
import time


class Storage(dict):
    class __Item:
        def __init__(self, value: Any, ttl: int | float) -> None:
            self.value = value
            self.life_time = datetime.datetime.now() + datetime.timedelta(seconds=ttl)

        def __repr__(self) -> str:
            return f"{self.value} (expires in {self.life_time.strftime('%I:%M:%S')})"

    def __init__(self, *args, **kwargs):
        object = {}
        self.life_time: int | float = kwargs.pop("life_time", 60)

        if args and all(isinstance(x, dict) for x in args):
            for arg in args:
                for key, value in arg.items():
                    object[key] = self.__Item(value, self.life_time)
            if kwargs:
                for key, value in kwargs.items():
                    object[key] = self.__Item(value, self.life_time)

        elif kwargs:
            for key, value in kwargs.items():
                object[key] = self.__Item(value, self.life_time)

        super().__init__(object)
        Thread(target=self.__expire, daemon=True).start()

    def __expire(self) -> None:
        while True:
            for key, value in self.items():
                if value.life_time.timestamp() <= time.time():
                    del self[key]
                    break

    def __setitem__(self, key, value):
        return super().__setitem__(key, self.__Item(value, self.life_time))
    
    def __getitem__(self, key):
        return super().__getitem__(key).value
