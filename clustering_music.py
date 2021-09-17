import pandas as pd
import numpy as np
from time import time
from datetime import datetime
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.metrics import silhouette_score, homogeneity_score, completeness_score, \
v_measure_score, adjusted_rand_score, adjusted_mutual_info_score
import matplotlib.pyplot as plt


def import_df(path="final_df.csv"):
        return pd.read_csv(path, index_col=0)

def create_model(df, init_algo="k-means++", n_clusters=10, n_init=4):
        scaler = StandardScaler()
        kmeans = KMeans(init=init_algo, n_clusters=n_clusters, n_init=n_init, random_state=0)
        t0 = time()
        print("Initiating fit...")
        model = make_pipeline(scaler, kmeans).fit(df)
        fit_time = time() - t0
        print(f"Fit ended in {fit_time:.3f} seconds.")
        results = (model, model[-1].inertia_, fit_time)
        return results

def evaluate_model():
        return 0

def save_model(model, path="music_model.pkl"):
        kmeans_model = model[-1]
        save_text = f"Model saved - {kmeans_model}\nInertia = {kmeans_model.inertia_:.2f}\n"
        time_text = str(datetime.now())[:-10] + "h" + "\n"
        file_text = f"Filename: {path}\n"

        with open(path, "wb") as f:
                pickle.dump(model,f)

        with open("model_log.txt", "a") as f:
                f.write("--------------\n" + save_text + time_text + file_text)
        
        return 0

def load_model(path="music_model.pkl"):

        try:
                with open(path, "rb") as f:
                        model = pickle.load(f)
        except FileNotFoundError: 
                print("Model pickle not found!") 
        
        return model

def cluster_song():
        return 0

def visualise_model(df, init_algo="k-means++", n_clusters=10, n_init=4):

        reduced_data = PCA(n_components=2).fit_transform(df)
        kmeans = KMeans(init=init_algo, n_clusters=n_clusters, n_init=n_init, random_state=0)
        kmeans.fit(reduced_data)

        # Step size of the mesh. Decrease to increase the quality of the VQ.
        h = .02     # point in the mesh [x_min, x_max]x[y_min, y_max].

        # Plot the decision boundary. For that, we will assign a color to each
        x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
        y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

        # Obtain labels for each point in mesh. Use last trained model.
        Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

        # Put the result into a color plot
        Z = Z.reshape(xx.shape) 
        plt.figure(1)
        plt.clf()
        plt.imshow(Z, interpolation="nearest",
                   extent=(xx.min(), xx.max(), yy.min(), yy.max()),
                   cmap=plt.cm.Paired, aspect="auto", origin="lower")

        plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
        # Plot the centroids as a white X
        centroids = kmeans.cluster_centers_
        plt.scatter(centroids[:, 0], centroids[:, 1], marker="x", s=169, linewidths=3,
                    color="w", zorder=10)
        plt.title("K-means clustering on the songs dataset (PCA-reduced data)\n"
                  "Centroids are marked with white cross\n"
                  f"Number of clusters used = {n_clusters}\n"
                  f"Inertia = {kmeans.inertia_:.2f}")
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        plt.xticks(())
        plt.yticks(())
        plt.show()

def elbow_graph(df):
        K = range(2, 21, 2)
        inertia = []

        for k in K:
                time0 = time()
                kmeans = KMeans(n_clusters=k,
                            random_state=1234)
                scaler = StandardScaler()
                pipe = make_pipeline(scaler, kmeans)
                pipe.fit(df)
                time_trained = time()-time0
                inertia.append(pipe[-1].inertia_)
                print(f"Trained a K-Means model with {k} neighbours! Time needed = {time_trained:.3f} seconds.")

        plt.figure(figsize=(16,8))
        plt.plot(K, inertia, 'bx-')
        plt.xlabel('k')
        plt.ylabel('inertia')
        plt.xticks(np.arange(min(K), max(K)+1, 1.0))
        plt.title('Elbow Method showing the optimal k')
        plt.show()

        return 0

def silhouette_graph(df):
        K = range(2, 21, 2)
        silhouette = []

        for k in K:

                time0 = time()
                kmeans = KMeans(n_clusters=k,
                            random_state=1234)
                scaler = StandardScaler()
                pipe = make_pipeline(scaler, kmeans)
                pipe.fit(df)
                silhouette.append(silhouette_score(df, pipe.predict(df)))
                time_trained = time()- time0

                print(f"Calculated silhouette with {k} neighbours! Time needed = {time_trained:.3f} seconds.")



        plt.figure(figsize=(16,8))
        plt.plot(K, silhouette, 'bx-')
        plt.xlabel('k')
        plt.ylabel('silhouette score')
        plt.xticks(np.arange(min(K), max(K)+1, 1.0))
        plt.title('Silhouette Method showing the optimal k')
        plt.show()

def main():
        df = import_df(path="spotify_songs.csv")
        modeling_df = df.drop(columns=["song_name", "song_id", "artist_name", "artist_id"])
        
        #elbow_graph(modeling_df)
        #silhouette_graph(modeling_df)
        #visualise_model(modeling_df, n_clusters=15)

        model, inertia, fit_time = create_model(modeling_df, n_clusters=20)

        save_model(model, path="music_model.pkl")

        kmeans_model = model[-1]

        print(f"Results for {kmeans_model}: inertia = {inertia:.2f}; fit_time = {fit_time:.3f}")

        return 0




if __name__=="__main__":
        main()