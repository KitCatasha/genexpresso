import plotly.express as px 
import pandas as pd
import umap
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from django.conf import settings

def save_plot(fig, filename):
    """Save the plotly figure as an image file and return the file path."""
    image_path = os.path.join(settings.MEDIA_ROOT, filename)
    fig.write_image(image_path, format="png")  # Save as PNG
    return f"{settings.MEDIA_URL}{filename}"  # Return the accessible media URL

def generate_heatmap(data, sample_labels, top_n=20):
    sorted_genes = data.mean(axis=1).nlargest(top_n).index
    filtered_data = data.loc[sorted_genes]
    renamed_data = filtered_data.rename(columns=sample_labels)

    fig = px.imshow(
        renamed_data,
        labels=dict(x="Samples", y="Genes", color="Expression Level"),
        color_continuous_scale="Viridis"
    )
    fig.update_layout(title="Top 20 Expressed Genes Heatmap", width=800, height=500)

    return save_plot(fig, "heatmap.png")  # Save and return URL

def generate_pca(data, sample_labels):
    scaled_data = StandardScaler().fit_transform(data.T)
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(scaled_data)

    pca_df = pd.DataFrame(pca_result, columns=["PCA1", "PCA2"])
    pca_df["Label"] = [sample_labels[col] for col in data.columns]

    fig = px.scatter(
        pca_df, x="PCA1", y="PCA2", color="Label",
        title="PCA Plot of Samples", hover_name="Label",
        color_discrete_map={"Control": "red", "Experimental": "green"}
    )

    return save_plot(fig, "pca.png")  # Save and return URL

def generate_umap(data, sample_labels):
    scaled_data = StandardScaler().fit_transform(data.T)
    reducer = umap.UMAP()
    umap_result = reducer.fit_transform(scaled_data)

    umap_df = pd.DataFrame(umap_result, columns=["UMAP1", "UMAP2"])
    umap_df["Label"] = [sample_labels[col] for col in data.columns]

    fig = px.scatter(
        umap_df, x="UMAP1", y="UMAP2", color="Label",
        title="UMAP Visualization of Samples", hover_name="Label",
        color_discrete_map={"Control": "red", "Experimental": "green"}
    )

    return save_plot(fig, "umap.png")  # Save and return URL
