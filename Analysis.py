import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from datetime import datetime
import glob
import os
import time

start_time = time.time()

files = glob.glob("PRSA_Data_*.csv")
chunksize = 50000
frames = []
total_rows = 0

print("Starting data ingestion")
print(f"Chunk size: {chunksize}")

for f in files:
    print(f"Reading file: {f}")
    for chunk in pd.read_csv(f, chunksize=chunksize):
        frames.append(chunk)
        total_rows += len(chunk)
        print(f"Processed rows: {total_rows} | Elapsed: {time.time()-start_time:.2f}s")

df = pd.concat(frames, ignore_index=True)

df["datetime"] = pd.to_datetime(df[["year","month","day","hour"]])
df.drop(columns=["No"], inplace=True)
df = df.drop_duplicates()
df = df.sort_values("datetime", kind="mergesort")
df = df.sort_values("station", kind="mergesort")

cols = ["PM2.5","PM10","SO2","NO2","CO","O3"]
df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")

print("Filling missing values station-wise")
for c in cols:
    df[c] = (
        df.groupby("station", sort=False)[c]
        .apply(lambda s: s.ffill().bfill())
        .values
    )

def iqr_bounds(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr

bounds = {}
for c in cols:
    lb, ub = iqr_bounds(df[c])
    bounds[c] = (lb, ub)
    df[c+"_anomaly"] = (df[c] < lb) | (df[c] > ub)

os.makedirs("images", exist_ok=True)

for c in cols:
    plt.figure(figsize=(10,4))
    plt.plot(df["datetime"], df[c], linewidth=0.6, label="Observed")
    plt.scatter(df.loc[df[c+"_anomaly"],"datetime"], df.loc[df[c+"_anomaly"],c], s=6, label="Anomaly")
    plt.title(f"{c} Concentration Over Time")
    plt.xlabel("Time")
    plt.ylabel(c)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"images/{c}_timeseries.png")
    plt.close()

for c in cols:
    plt.figure(figsize=(6,4))
    plt.hist(df[c], bins=60)
    plt.title(f"{c} Distribution")
    plt.xlabel(c)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(f"images/{c}_hist.png")
    plt.close()

plt.figure(figsize=(8,4))
df[cols].boxplot()
plt.title("Pollutant Spread and Outliers")
plt.ylabel("Concentration")
plt.tight_layout()
plt.savefig("images/boxplot.png")
plt.close()

corr = df[cols].corr()
plt.figure(figsize=(6,5))
plt.imshow(corr)
plt.colorbar(label="Correlation Coefficient")
plt.xticks(range(len(cols)), cols, rotation=45)
plt.yticks(range(len(cols)), cols)
plt.title("Inter-Pollutant Correlation Matrix")
plt.tight_layout()
plt.savefig("images/correlation.png")
plt.close()

station_mean = df.groupby("station")[cols].mean()
station_mean.plot(kind="bar", figsize=(11,4))
plt.title("Average Pollutant Levels by Monitoring Station")
plt.xlabel("Station")
plt.ylabel("Mean Concentration")
plt.tight_layout()
plt.savefig("images/station_mean.png")
plt.close()

summary = df[cols].describe().round(2)
anomaly_counts = df[[c+"_anomaly" for c in cols]].sum()

pdf = SimpleDocTemplate("Beijing_Air_Quality_Analytical_Report.pdf", pagesize=A4)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph("Beijing Multi-Station Air Quality Analysis Report", styles["Title"]))
story.append(Spacer(1,0.3*inch))
story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
story.append(Spacer(1,0.3*inch))

story.append(Paragraph("<b>1. Dataset Overview</b>", styles["Heading2"]))
story.append(Paragraph(
    "This report analyses the Beijing Multi-Station Air Quality Dataset obtained from publicly available monitoring stations. "
    "The dataset contains hourly measurements of major atmospheric pollutants across multiple locations over several years.",
    styles["Normal"]
))

story.append(Spacer(1,0.2*inch))
story.append(Paragraph("<b>2. Data Processing</b>", styles["Heading2"]))
story.append(Paragraph(
    f"A total of {total_rows} records were processed using chunk-based ingestion (chunk size = {chunksize}). "
    "Duplicate records were removed, timestamps were reconstructed, and missing values were handled station-wise.",
    styles["Normal"]
))

story.append(Spacer(1,0.2*inch))
story.append(Paragraph("<b>3. Anomaly Detection</b>", styles["Heading2"]))
story.append(Paragraph(
    "Anomalies were detected using an Interquartile Range (IQR) based method. "
    "Values lying significantly outside the normal statistical range were flagged as anomalous.",
    styles["Normal"]
))

story.append(PageBreak())
story.append(Paragraph("<b>4. Statistical Summary</b>", styles["Heading2"]))

for c in cols:
    story.append(Paragraph(
        f"{c}: Mean={summary[c]['mean']}, Min={summary[c]['min']}, "
        f"Max={summary[c]['max']}, Std={summary[c]['std']}, "
        f"Detected Anomalies={int(anomaly_counts[c+'_anomaly'])}",
        styles["Normal"]
    ))

story.append(PageBreak())
story.append(Paragraph("<b>5. Time Series Analysis</b>", styles["Heading2"]))
story.append(Paragraph(
    "Time series plots illustrate pollutant behavior over time. "
    "Anomalies are highlighted to indicate extreme pollution episodes.",
    styles["Normal"]
))

for c in cols:
    story.append(Image(f"images/{c}_timeseries.png", 6*inch, 3*inch))
    story.append(Spacer(1,0.2*inch))

story.append(PageBreak())
story.append(Paragraph("<b>6. Distribution and Comparative Analysis</b>", styles["Heading2"]))
story.append(Paragraph(
    "Distribution plots, boxplots, correlation matrices, and station-wise averages "
    "provide insights into variability, relationships, and spatial differences.",
    styles["Normal"]
))
story.append(Spacer(1,0.2*inch))

story.append(Image("images/boxplot.png", 6*inch, 3*inch))
story.append(Spacer(1,0.2*inch))
story.append(Image("images/correlation.png", 4.5*inch, 4.5*inch))
story.append(Spacer(1,0.2*inch))
story.append(Image("images/station_mean.png", 6.5*inch, 3*inch))

story.append(PageBreak())
story.append(Paragraph("<b>7. Runtime Information</b>", styles["Heading2"]))
story.append(Paragraph(
    f"Total execution time: {time.time()-start_time:.2f} seconds.",
    styles["Normal"]
))

story.append(PageBreak())
story.append(Paragraph("<b>8. Anomaly Occurrence and Interpretation</b>", styles["Heading2"]))

reasons = {
    "PM2.5": "combustion from residential heating, traffic emissions, and stagnant winter meteorology",
    "PM10": "road dust resuspension, construction activity, and wind-driven particles",
    "SO2": "coal combustion from power generation and industrial sources",
    "NO2": "vehicular emissions and high traffic density periods",
    "CO": "incomplete combustion processes and traffic congestion",
    "O3": "photochemical reactions driven by sunlight and precursor gases"
}

for c in cols:
    lb, ub = bounds[c]
    extreme = df.loc[df[c+"_anomaly"], ["datetime", c]].sort_values(c, ascending=False).head(3)
    story.append(Paragraph(f"<b>{c}</b>", styles["Normal"]))
    for _, r in extreme.iterrows():
        story.append(Paragraph(
            f"An anomaly was observed on {r['datetime']} with a concentration of {r[c]}. "
            f"The normal upper bound for this pollutant is approximately {round(ub,2)}. "
            f"Such events may be attributed to {reasons[c]}.",
            styles["Normal"]
        ))
    story.append(Spacer(1,0.2*inch))

pdf.build(story)

print(f"Completed successfully in {time.time()-start_time:.2f} seconds")