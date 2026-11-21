Machine learning builds programs that improve from data instead of following hand-written rules. A spam filter, a house-price estimator, and a recommendation engine all learn patterns from examples and apply them to new cases. This subject covers the core algorithms and, just as importantly, the practices that decide whether a model actually works on data it has not seen.

It begins with the end-to-end workflow: framing a problem, preparing data, training, evaluating, and deploying. Data preparation covers feature scaling and one-hot encoding. The regression module derives linear regression and trains it with gradient descent. The classification modules cover logistic regression, decision trees, k-nearest neighbours, naive Bayes, support vector machines, and ensemble methods such as bagging, random forests, and boosting. Unsupervised learning is introduced through k-means and density-based clustering, and principal component analysis reduces dimensionality. The evaluation modules explain precision, recall, ROC curves, cross-validation, and model selection, and the subject closes with regularisation, the bias-variance trade-off, and an introduction to reinforcement learning.

Examples use small datasets and short Python programs, so you can follow every calculation from raw data to a final prediction.

## What you will learn
- Describe the stages of a machine learning project from problem framing to deployment
- Prepare data with scaling, encoding, and train-test splits that avoid data leakage
- Fit linear regression with the normal equation and with gradient descent
- Train and interpret logistic regression, decision trees, k-NN, naive Bayes, and support vector machines
- Combine models with bagging, random forests, and boosting
- Group unlabelled data with k-means and density-based clustering
- Reduce dimensionality with principal component analysis
- Evaluate classifiers with confusion matrices, precision, recall, F1, and ROC curves
- Select models and hyperparameters with cross-validation
- Control overfitting with L1 and L2 regularisation and explain the bias-variance trade-off
- Describe agents, rewards, and policies in reinforcement learning

## Prerequisites
- Python programming, including lists, functions, and loops
- Linear algebra basics: vectors, matrices, and dot products
- Probability and statistics basics: mean, variance, and conditional probability
- Derivatives, for gradient descent (see the Calculus subject)

## Glossary
- **Feature**: an input variable used by a model to make a prediction
- **Label**: the target value a supervised model learns to predict
- **Supervised learning**: learning from examples that include the correct labels
- **Unsupervised learning**: finding structure in data without labels
- **Training set**: the data used to fit a model's parameters
- **Test set**: held-out data used only to estimate performance on unseen examples
- **Loss function**: a measure of how far a model's predictions are from the targets
- **Gradient descent**: an iterative method that adjusts parameters in the direction that reduces the loss
- **Overfitting**: fitting noise in the training data so well that performance on new data suffers
- **Regularisation**: adding a penalty on model complexity to reduce overfitting
- **Cross-validation**: repeatedly splitting data into training and validation folds to estimate performance
- **Precision and recall**: the fraction of predicted positives that are correct, and the fraction of actual positives that are found
- **Ensemble**: a model that combines the predictions of several base models

## Further reading
- Gareth James, Daniela Witten, Trevor Hastie, and Robert Tibshirani, *An Introduction to Statistical Learning* (Springer)
- Aurélien Géron, *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow* (O'Reilly Media)
- Christopher M. Bishop, *Pattern Recognition and Machine Learning* (Springer)
- Richard S. Sutton and Andrew G. Barto, *Reinforcement Learning: An Introduction* (MIT Press)
