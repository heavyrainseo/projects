import seaborn as sns
import matplotlib.pyplot as plt

flt = sns.load_dataset("flights")
sns.lineplot(data=flt, x="year", y="passengers", hue="month")
plt.show()

flt_year = flt.groupby("year", as_index=False)["passengers"].sum()
sns.barplot(data=flt_year, x="year", y="passengers")
plt.show() 