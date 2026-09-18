import seaborn as sns
import matplotlib.pyplot as plt

flt = sns.load_dataset("flights")

flt_year = flt.groupby("year", as_index=False)["passengers"].sum()
print(flt_year)

sy = flt_year["year"].std()
sp = flt_year["passengers"].std()
cov = flt_year["year"].cov(flt_year["passengers"])
print(f'r : {cov/(sy*sp)}')
sns.barplot(data=flt_year, x="year", y="passengers")
plt.savefig("flights_barplot.png")

flt_pivot = flt.pivot(index="month", columns="year", values="passengers")
sns.heatmap(flt_pivot, annot=True, fmt="d", cmap="YlGnBu")
plt.savefig("flights_heatmap.png")