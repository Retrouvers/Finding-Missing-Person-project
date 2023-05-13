import matplotlib.pyplot as plt
from scipy import stats
x=[0,6,11,14,22]
y=[1,7,12,15,21]
slope, intercept, r,p,str_err=stats.linregress(x,y)
def myfunc(x):
    return slope*x+intercept;
mymodel= list(map(myfunc,x))
plt.scatter(x,y)
plt.plot(x,mymodel)
plt.show()