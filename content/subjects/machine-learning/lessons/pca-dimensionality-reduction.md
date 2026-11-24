---
lesson: pca-dimensionality-reduction
title: Principal Component Analysis (PCA)
summary: Principal component analysis: centring data, the covariance matrix, eigenvectors as directions of maximum variance, explained variance and choosing the number of components, projection and reconstruction, the SVD connection, and limitations.
minutes: 45
type: theory
objectives:
  - Compute principal components from the covariance matrix of centred data and interpret their directions and eigenvalues
  - Choose the number of components using explained variance, and project and reconstruct data
  - Explain the link between PCA and SVD, when to standardise, and the limitations of linear dimensionality reduction
review: ai-draft
---
## Introduction

Datasets often have dozens or thousands of features, many of them correlated: a student's marks in maths and physics move together; neighbouring pixels in an image are nearly equal. **Dimensionality reduction** compresses such data into fewer numbers while keeping most of the information, which helps with visualisation, storage, noise reduction, and the speed and stability of later models. **Principal component analysis** (PCA) is the classic linear method and a beautiful application of eigenvectors.

**Before you start:** you should know variance and covariance and the eigenvalue ideas in *Eigenvalue Decomposition & SVD*.

## Core theory

### Why reduce dimensions?

High-dimensional data are hard to visualise, expensive to store and process, and suffer from the **curse of dimensionality**: distances lose meaning and models need far more data. Correlated features also carry redundant information. PCA replaces the original features with a few new ones, **principal components**, that are uncorrelated and capture as much variance as possible.

### The algorithm

1. **Centre** the data by subtracting each feature's mean (and **standardise** if features have different units).
2. Compute the **covariance matrix** $C = \frac{1}{n - 1}X^\top X$ of the centred data matrix $X$ ($n$ rows, $d$ features).
3. Compute the **eigenvectors** and **eigenvalues** of $C$: $C\mathbf{v}_i = \lambda_i\mathbf{v}_i$. Because $C$ is symmetric, the eigenvectors are orthogonal.
4. Sort by eigenvalue. The first principal component $\mathbf{v}_1$ is the direction of **maximum variance**; $\lambda_1$ is the variance of the data along it. Each later component captures the most remaining variance while being orthogonal to the earlier ones.
5. Keep the top $k$ components $V_k$ and **project**: $Z = XV_k$ gives each point's $k$ new coordinates (scores).
6. **Reconstruct** approximately with $\hat{X} = ZV_k^\top$ plus the mean.

### Explained variance and choosing k

The **explained variance ratio** of component $i$ is $\lambda_i / \sum_j \lambda_j$. Choose $k$ to keep, say, 95% of the variance, or look for an elbow in a **scree plot** of the eigenvalues. Among all projections onto $k$ dimensions, PCA's has the **smallest squared reconstruction error**, equal to the sum of the discarded eigenvalues (scaled by $(n - 1)/n$ for a per-point average).

### PCA through the SVD

Writing the centred data as $X = U\Sigma V^\top$ (the singular value decomposition), the columns of $V$ are the principal directions and $\lambda_i = \sigma_i^2/(n - 1)$. Libraries compute PCA through the SVD because it avoids forming $X^\top X$, which squares the condition number and loses precision.

### Practical points and limitations

- Fit the means and components on **training data only**, then apply them to new data.
- Standardise when features have different units; otherwise the feature with the largest variance dominates.
- PCA is **linear**: it cannot unfold curved structures. Kernel PCA and autoencoders are non-linear alternatives; **t-SNE** and **UMAP** are popular for 2-D visualisation.
- High variance does not guarantee relevance to a prediction task: a low-variance direction can be the one that separates classes.
- Components are mixtures of features, so they can be harder to interpret than the originals. PCA is also sensitive to outliers.

## Worked examples

### Example 1: Compressing two exam scores into one number

Eight students' maths and physics marks are strongly correlated. The program centres them, computes the covariance matrix and its eigenvalues, projects onto the first component, and reconstructs.

```python
import math

maths = [62, 70, 75, 80, 85, 88, 92, 96]
physics = [58, 68, 70, 79, 81, 86, 89, 97]
n = len(maths)

mx, my = sum(maths) / n, sum(physics) / n
X = [(a - mx, b - my) for a, b in zip(maths, physics)]            # centre the data
sxx = sum(a * a for a, _ in X) / (n - 1)
syy = sum(b * b for _, b in X) / (n - 1)
sxy = sum(a * b for a, b in X) / (n - 1)
print(f"means: maths {mx:.2f}, physics {my:.2f}")
print(f"covariance matrix: [[{sxx:.2f}, {sxy:.2f}], [{sxy:.2f}, {syy:.2f}]]")

# Eigen-decomposition of the 2x2 symmetric covariance matrix
mid, rad = (sxx + syy) / 2, math.sqrt(((sxx - syy) / 2) ** 2 + sxy ** 2)
l1, l2 = mid + rad, mid - rad
v = (sxy, l1 - sxx)
norm = math.hypot(*v)
pc1 = (v[0] / norm, v[1] / norm)
print(f"eigenvalues {l1:.2f} and {l2:.2f}; explained variance ratio of PC1 = {l1 / (l1 + l2):.4f}")
print(f"PC1 direction = ({pc1[0]:.4f}, {pc1[1]:.4f})")

scores = [a * pc1[0] + b * pc1[1] for a, b in X]                 # 1-D representation
print("PC1 scores:", [round(s, 2) for s in scores])
recon = [(mx + s * pc1[0], my + s * pc1[1]) for s in scores]
err = sum((a - ra) ** 2 + (b - rb) ** 2 for (a, b), (ra, rb) in zip(zip(maths, physics), recon)) / n
print(f"student 1 reconstructed from one number: ({recon[0][0]:.1f}, {recon[0][1]:.1f}) vs actual (62, 58)")
print(f"mean squared reconstruction error {err:.3f} = l2 * (n - 1) / n = {l2 * (n - 1) / n:.3f}")
```

Output:

```text
means: maths 81.00, physics 78.50
covariance matrix: [[132.86, 144.43], [144.43, 159.71]]
eigenvalues 291.34 and 1.23; explained variance ratio of PC1 = 0.9958
PC1 direction = (0.6736, 0.7391)
PC1 scores: [-27.95, -15.17, -10.32, -0.3, 4.54, 10.26, 15.17, 23.78]
student 1 reconstructed from one number: (62.2, 57.8) vs actual (62, 58)
mean squared reconstruction error 1.080 = l2 * (n - 1) / n = 1.080
```

The covariance between subjects (144.43) is almost as large as each variance, signalling strong correlation. The first eigenvalue (291.34) dwarfs the second (1.23), so the first component captures 99.58% of the variance: one number per student is enough. Its direction (0.67, 0.74) weights both subjects almost equally, so the score acts as an "overall science ability". Student 1, reconstructed from a single number, comes out as (62.2, 57.8) against an actual (62, 58). The average squared reconstruction error equals the discarded eigenvalue scaled by $(n - 1)/n$, exactly as theory predicts.

### Example 2: PCA by hand

Suppose the centred data have covariance matrix

$$C = \begin{pmatrix} 2 & 1 \\ 1 & 2 \end{pmatrix}$$

Its eigenvalues solve $(2 - \lambda)^2 - 1 = 0$, so $\lambda_1 = 3$ and $\lambda_2 = 1$, with eigenvectors $\mathbf{v}_1 = \frac{1}{\sqrt{2}}(1, 1)$ and $\mathbf{v}_2 = \frac{1}{\sqrt{2}}(1, -1)$. The first component explains $3/(3 + 1) = 75\%$ of the variance.

Project the centred point $(2, 0)$: $z_1 = \frac{2 + 0}{\sqrt{2}} \approx 1.414$. Reconstruct: $1.414 \times \frac{1}{\sqrt{2}}(1, 1) = (1, 1)$. The error vector is $(2, 0) - (1, 1) = (1, -1)$, which lies along the discarded component $\mathbf{v}_2$, with squared length 2.

## Applications

- **Visualisation:** projecting high-dimensional data to 2-D or 3-D to look for structure.
- **Preprocessing:** reducing features before regression or clustering to cut noise and computation.
- **Image compression and face recognition:** "eigenfaces" represent faces with a few components.
- **Genomics:** summarising thousands of gene measurements, revealing population structure.
- **Finance:** a few factors explain most of the co-movement of asset returns.

## Common mistakes

- **Forgetting to centre the data.** Without centring, the first component points towards the mean instead of along the spread.
- **Mixing units without standardising.** Centimetres and kilograms would be weighted by their arbitrary scales.
- **Fitting PCA on all the data before splitting.** It leaks test information; fit on training data.
- **Assuming the top components are the most predictive.** Variance is not the same as relevance to the target.
- **Using PCA for non-linear structure.** It cannot unroll curved manifolds.

## Revision notes

- Centre (and usually standardise), compute the covariance matrix, eigendecompose, sort, project.
- PC1 = direction of maximum variance; eigenvalue = variance along it; components are orthogonal.
- Explained variance ratio $\lambda_i/\sum\lambda_j$; choose $k$ for about 95% or by a scree plot.
- PCA minimises reconstruction error among linear $k$-dimensional projections.
- SVD of centred $X$: principal directions in $V$, $\lambda_i = \sigma_i^2/(n - 1)$; numerically preferred.
- Limitations: linear, outlier-sensitive, variance is not relevance, less interpretable.

## Practice questions

:::question basic
Why must the data be centred before PCA?
:::answer
PCA looks for directions of maximum variance around the mean. Without centring, the analysis is dominated by the offset of the data from the origin, and the first component points roughly towards the mean instead of along the direction in which the data actually spread.
:::

:::question basic
A covariance matrix has eigenvalues 5, 3, 1.5, and 0.5. What fraction of the variance do the first two components explain?
:::answer
$(5 + 3)/(5 + 3 + 1.5 + 0.5) = 8/10 = 80\%$.
:::

:::question intermediate
Why should features be standardised before PCA when one is height in centimetres and another is weight in kilograms?
:::answer
PCA maximises variance, and variance depends on units: measured in centimetres, height has a much larger numerical variance than it would in metres. Without standardising, the components would reflect arbitrary unit choices. Standardising (equivalently, using the correlation matrix) gives each feature equal initial importance.
:::

:::question intermediate
How does PCA differ from feature selection?
:::answer
Feature selection keeps a subset of the original features unchanged, so results stay interpretable in original terms. PCA creates new features that are linear combinations of all the originals, capturing shared variance more efficiently but making each component harder to interpret.
:::

:::question advanced
Explain how PCA can be computed from the SVD of the centred data matrix and why this is preferred numerically.
:::answer
With $X = U\Sigma V^\top$, we have $X^\top X = V\Sigma^2V^\top$, so the right singular vectors (columns of $V$) are the eigenvectors of the covariance matrix and the eigenvalues are $\sigma_i^2/(n - 1)$; the scores are $XV = U\Sigma$. Forming $X^\top X$ explicitly squares the condition number, so small eigenvalues can lose most of their accuracy in floating point. Computing the SVD directly from $X$ avoids that squaring and is more accurate.
:::

## Further learning

- **Next:** *Classification Metrics & ROC Curves* turns to evaluating classifiers.
- **Related:** *Eigenvalue Decomposition & SVD* in Linear Algebra covers the mathematics behind PCA.
