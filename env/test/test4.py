import HeaterClass
import ConfigClass


c = ConfigClass.ConfigClass()

t = HeaterClass.HeaterClass()


a= t.getCurrentTemperature()
print(a['tempInside'])
print(a['tempOutside'])


