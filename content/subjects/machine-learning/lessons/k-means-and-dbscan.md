---
lesson: k-means-and-dbscan
title: K-Means & Density-Based Clustering
summary: Clustering without labels: the k-means objective and Lloyd's algorithm, initialisation with k-means++, choosing k with the elbow method and silhouette scores, and density-based clustering with DBSCAN's core, border, and noise points.
minutes: 45
type: theory
objectives:
  - Run k-means by hand and in code, explain its objective, and choose k with the elbow method or silhouette score
  - Apply DBSCAN, classify points as core, border, or noise, and choose eps and minPts
  - Compare k-means and DBSCAN on cluster shape, outliers, scaling, and parameter sensitivity
review: ai-draft
---
## Introduction

Often we have data but no labels: customer purchase histories, sensor readings, news articles, GPS traces. **Clustering** groups similar items so that structure emerges: customer segments, topics, hotspots, or anomalies. There is no single correct answer, because "similar" depends on the features and the purpose. The two most widely used approaches are **k-means**, which finds compact, centre-based clusters, and **DBSCAN**, which finds dense regions of any shape and marks outliers.

**Before you start:** you should know Euclidean distance and *Feature Scaling & One-Hot Encoding*.

## Core theory

### The k-means objective

k-means partitions $n$ points into $k$ clusters, each represented by its **centroid** $\boldsymbol{\mu}_j$, to minimise the **inertia** (within-cluster sum of squares):

$$J = \sum_{j=1}^{k}\sum_{\mathbf{x} \in C_j}\|\mathbf{x} - \boldsymbol{\mu}_j\|^2$$

### Lloyd's algorithm

1. Choose $k$ initial centroids.
2. **Assign** each point to its nearest centroid.
3. **Update** each centroid to the mean of its assigned points.
4. Repeat steps 2 and 3 until the assignments stop changing.

Each step can only lower $J$, so the algorithm always converges, but to a **local** minimum that depends on the starting centroids. Each iteration costs $O(nkd)$.

### Initialisation and choosing k

- **k-means++** picks the first centroid at random and each further one with probability proportional to its squared distance from the nearest centroid already chosen. Spreading the starting centroids out gives better and more consistent results; libraries also run several restarts and keep the best.
- **Elbow method:** plot inertia against $k$. Inertia always falls as $k$ grows (it is 0 when every point is its own cluster), so look for the "elbow" where improvements level off.
- **Silhouette score:** for each point, $a$ is its mean distance to its own cluster and $b$ its mean distance to the nearest other cluster; $s = \frac{b - a}{\max(a, b)}$ ranges from −1 to 1, and a higher average means better-separated clusters.

k-means assumes roughly **spherical clusters of similar size**, is pulled by outliers (every point must belong to a cluster), and needs **scaled features**.

### DBSCAN

**Density-Based Spatial Clustering of Applications with Noise** has two parameters: a radius $\varepsilon$ (eps) and a count **minPts**.

- A **core point** has at least minPts points (including itself) within distance $\varepsilon$.
- A **border point** is within $\varepsilon$ of a core point but is not itself core.
- A **noise point** is neither.

A cluster is grown from a core point by repeatedly adding all points within $\varepsilon$ of core points in the cluster (a breadth-first expansion). DBSCAN finds clusters of **arbitrary shape**, decides the number of clusters itself, and labels outliers as noise. It struggles when clusters have very different densities, since one $\varepsilon$ cannot suit all of them; **OPTICS** and **HDBSCAN** address this. A common way to choose $\varepsilon$ is to plot each point's distance to its minPts-th nearest neighbour, sorted, and pick the value at the bend.

**Hierarchical clustering**, which merges the closest clusters step by step and records the merges in a dendrogram, is a third widely used family.

## Worked examples

### Example 1: Three groups and a stray point

Twelve points form three visible groups, and one stray point sits between them. The program runs k-means with farthest-first initialisation (a deterministic cousin of k-means++), computes inertia for $k = 1$ to 5, and runs DBSCAN.

```python
import math

points = [(1, 1), (1.5, 2), (2, 1), (1.2, 1.5),           # group near (1.5, 1.5)
          (5, 5), (5.5, 6), (6, 5), (5.2, 5.5),           # group near (5.5, 5.5)
          (9, 1), (8.5, 1.5), (9.5, 2), (9, 0.5),         # group near (9, 1)
          (5, 2.5)]                                        # a stray point


def kmeans(k, iterations=20):
    centroids = [points[0]]                                # farthest-first initialisation
    while len(centroids) < k:
        centroids.append(max(points, key=lambda p: min(math.dist(p, c) for c in centroids)))
    for _ in range(iterations):
        clusters = [[] for _ in range(k)]
        for p in points:
            clusters[min(range(k), key=lambda i: math.dist(p, centroids[i]))].append(p)
        new = [tuple(sum(v) / len(c) for v in zip(*c)) for c in clusters]
        if new == centroids:
            break
        centroids = new
    inertia = sum(min(math.dist(p, c) ** 2 for c in centroids) for p in points)
    return centroids, clusters, inertia


centroids, clusters, inertia = kmeans(3)
for c, members in zip(centroids, clusters):
    print(f"centroid ({c[0]:.2f}, {c[1]:.2f}) <- {len(members)} points")
print("elbow:", ", ".join(f"k={k}: {kmeans(k)[2]:.2f}" for k in range(1, 6)))


def dbscan(eps, min_pts):
    labels, cluster = {}, 0
    neighbours = {p: [q for q in points if math.dist(p, q) <= eps] for p in points}
    for p in points:
        if p in labels or len(neighbours[p]) < min_pts:
            continue
        cluster += 1
        labels[p] = cluster
        queue = list(neighbours[p])
        while queue:
            q = queue.pop()
            if labels.get(q, 0) == 0:          # unvisited or previously marked noise
                labels[q] = cluster
                if len(neighbours[q]) >= min_pts:
                    queue.extend(neighbours[q])  # q is a core point: keep expanding
    return [labels.get(p, 0) for p in points]   # 0 means noise


print("DBSCAN(eps=1.2, minPts=3) labels:", dbscan(1.2, 3))
```

Output:

```text
centroid (1.43, 1.38) <- 4 points
centroid (9.00, 1.25) <- 4 points
centroid (5.34, 4.80) <- 5 points
elbow: k=1: 163.28, k=2: 68.79, k=3: 11.02, k=4: 4.26, k=5: 3.26
DBSCAN(eps=1.2, minPts=3) labels: [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 0]
```

k-means finds the three groups, but the stray point (5, 2.5) must join one of them: the middle cluster gets 5 points, and its centroid is dragged from (5.43, 5.38), the centre of its four real members, down to (5.34, 4.80). The elbow is clear: inertia falls steeply from 163 to 69 to 11 as $k$ goes from 1 to 3, then only to 4.3 and 3.3, so $k = 3$ is the natural choice. DBSCAN with $\varepsilon = 1.2$ and minPts = 3 finds the same three clusters without being told how many, and labels the stray point 0, meaning noise: it is more than 1.2 away from every other point.

### Example 2: k-means by hand in one dimension

Points: 1, 2, 4, 5, 11, 12, with $k = 2$ and initial centroids 1 and 5.

| Iteration | Cluster 1 | Cluster 2 | New centroids |
| :--- | :--- | :--- | :--- |
| 1 | {1, 2} | {4, 5, 11, 12} | 1.5 and 8 |
| 2 | {1, 2, 4} | {5, 11, 12} | 2.33 and 9.33 |
| 3 | {1, 2, 4, 5} | {11, 12} | 3 and 11.5 |
| 4 | {1, 2, 4, 5} | {11, 12} | unchanged: converged |

In iteration 2, point 4 is 2.5 from 1.5 but 4 from 8, so it switches; in iteration 3, point 5 is 2.67 from 2.33 but 4.33 from 9.33, so it switches too. The final inertia is $(4 + 1 + 1 + 4) + (0.25 + 0.25) = 10.5$. A bad start can still converge to a worse answer, which is why restarts and k-means++ matter.

## Applications

- **Customer segmentation:** grouping customers by behaviour for targeted marketing.
- **Image compression:** k-means colour quantisation replaces millions of colours with $k$ representative ones.
- **Geospatial analysis:** DBSCAN finds hotspots in GPS or incident data and ignores scattered points.
- **Anomaly detection:** DBSCAN noise points and far-from-centroid points flag unusual cases.
- **Document organisation:** clustering news articles or support tickets by topic.

## Common mistakes

- **Clustering unscaled features.** One large-range feature decides everything.
- **Trusting a single k-means run.** Use k-means++ and several restarts.
- **Expecting k-means to find non-spherical shapes.** Rings, crescents, and elongated clusters need DBSCAN or other methods.
- **Reading meaning into every cluster.** Algorithms always return clusters, even in structureless data; validate them.
- **Choosing eps by guesswork.** Use a k-distance plot and domain knowledge.

## Revision notes

- k-means minimises inertia $\sum\|\mathbf{x} - \boldsymbol{\mu}\|^2$; Lloyd's algorithm alternates assignment and mean update.
- Converges to a local optimum; use k-means++ and restarts.
- Choose $k$ with the elbow method or silhouette $s = (b - a)/\max(a, b)$.
- DBSCAN: core (≥ minPts within $\varepsilon$), border, noise; clusters of any shape; finds the number of clusters.
- DBSCAN struggles with varying densities (use OPTICS or HDBSCAN).
- Scale features for both.

## Practice questions

:::question basic
What quantity does k-means minimise?
:::answer
The inertia, or within-cluster sum of squares: the sum over all points of the squared Euclidean distance from each point to the centroid of its cluster.
:::

:::question basic
Define core, border, and noise points in DBSCAN.
:::answer
A core point has at least minPts points (including itself) within radius $\varepsilon$. A border point is within $\varepsilon$ of some core point but has fewer than minPts neighbours itself. A noise point is neither a core point nor within $\varepsilon$ of any core point.
:::

:::question intermediate
Why does k-means need feature scaling and multiple initialisations?
:::answer
It assigns points by Euclidean distance, so a feature with a large range dominates the clustering unless features are scaled. And Lloyd's algorithm only reaches a local minimum that depends on the starting centroids; running it from several k-means++ initialisations and keeping the lowest inertia makes a poor solution much less likely.
:::

:::question intermediate
Data form two concentric rings. Which algorithm, k-means or DBSCAN, would separate them, and why?
:::answer
DBSCAN. Each ring is a connected region of high density, so DBSCAN grows each ring into its own cluster. k-means assigns points to the nearest centroid, producing roughly convex regions; since both rings share the same centre, it would cut the rings into halves instead of separating inner from outer.
:::

:::question advanced
A point has mean distance 1.0 to the other members of its cluster and mean distance 3.0 to the members of the nearest other cluster. Compute its silhouette and interpret it. What would a negative silhouette mean?
:::answer
$s = (b - a)/\max(a, b) = (3.0 - 1.0)/3.0 \approx 0.67$: the point is much closer to its own cluster than to the next, so it is well clustered. A negative silhouette ($a > b$) means the point is, on average, closer to another cluster than to its own, suggesting it is misassigned or the clusters overlap.
:::

## Further learning

- **Next:** *Principal Component Analysis (PCA)* reduces dimensions before clustering or visualisation.
- **Related:** *Feature Scaling & One-Hot Encoding* covers the scaling that distance-based clustering requires.
