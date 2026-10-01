import GEOparse
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import umap

def fetch_geo_data(geo_id):
    """
    Fetch GEO data using GEOparse and return expression data and group labels.
    """
    geo = GEOparse.get_GEO(geo=geo_id, destdir="./datasets")
    data = {
        sample.name: sample.table['VALUE'].values for sample in geo.gsms.values()
    }
    group_labels = {
        sample.name: "Control" if "control" in sample.metadata.get("characteristics_ch1", [""])[0].lower() else "Experimental"
        for sample in geo.gsms.values()
    }
    expression_data = pd.DataFrame(data).T
    return expression_data, group_labels

def preprocess_geo_data(expression_data):
    if expression_data.empty:
        print("Expression data is empty!")
    else:
        print("Expression data before preprocessing:", expression_data.head())

    expression_data = np.log2(expression_data + 1).dropna(axis=1)
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(expression_data)

    processed_data = pd.DataFrame(scaled_data, index=expression_data.index, columns=expression_data.columns)
    print("Processed data:", processed_data.head())
    return processed_data

def generate_heatmap(data, group_labels):
    """
    Generate a heatmap for the top 10 samples with the highest expression.
    """
    top_samples = data.sum(axis=1).nlargest(10).index
    data_subset = data.loc[top_samples]
    fig = px.imshow(data_subset, labels={"color": "Expression"}, title="Top 10 Samples Heatmap")
    return fig.to_html(full_html=False)

def generate_pca(data, group_labels):
    """
    Generate a PCA plot for the data.
    """
    pca = PCA(n_components=2)
    result = pca.fit_transform(data)
    labels = [group_labels[sample] for sample in data.index]
    fig = px.scatter(result, x=0, y=1, color=labels, labels={"color": "Group"}, title="PCA Plot")
    return fig.to_html(full_html=False)

def generate_umap(data, group_labels):
    """
    Generate a UMAP plot for the data.
    """
    reducer = umap.UMAP()
    result = reducer.fit_transform(data)
    labels = [group_labels[sample] for sample in data.index]
    fig = px.scatter(result, x=0, y=1, color=labels, labels={"color": "Group"}, title="UMAP Plot")
    return fig.to_html(full_html=False)
