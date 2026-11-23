Deep learning trains neural networks with many layers to learn useful representations directly from raw data such as pixels, audio, and text. It is the technology behind modern image recognition, speech recognition, machine translation, and large language models. The ideas are surprisingly compact: layers of simple units, a loss to minimise, and the chain rule to compute how every weight should change.

This subject builds those ideas from the ground up. It starts with the multilayer perceptron expressed in matrix form and the activation functions that make networks non-linear, along with how activations affect gradient flow. It then explains loss functions and the training loop, and derives backpropagation from computational graphs and the chain rule. The optimisation modules cover the Adam optimiser and adaptive learning rates, and regularisation with dropout, batch normalisation, and weight decay. The architecture modules introduce convolutional networks and transfer learning for images, recurrent networks with LSTM and gated units for sequences, and finally self-attention and the transformer.

Lessons pair each formula with a small numerical example, so you can compute a forward and backward pass by hand before trusting a framework to do it.

## What you will learn
- Express a multilayer perceptron as matrix operations and compute a forward pass
- Compare activation functions and explain vanishing and exploding gradients
- Choose loss functions for regression and classification and write a training loop
- Derive backpropagation on a computational graph using the chain rule
- Explain how momentum and Adam adapt learning rates during training
- Reduce overfitting with dropout, batch normalisation, and weight decay
- Explain convolution, pooling, and why CNNs suit images, and apply transfer learning
- Describe recurrent networks and how LSTM and GRU gates preserve information over time
- Explain self-attention and the structure of a transformer

## Prerequisites
- Python programming
- Linear algebra: matrix multiplication and vectors (see the Linear Algebra subject)
- Calculus: derivatives and the chain rule (see the Calculus subject)
- Machine learning basics: training and test sets, loss functions, and overfitting

## Glossary
- **Neuron**: a unit that computes a weighted sum of its inputs plus a bias and applies an activation function
- **Layer**: a group of neurons that transforms its input vector into an output vector
- **Activation function**: a non-linear function such as ReLU or sigmoid applied to a neuron's output
- **Loss function**: a measure of the difference between predictions and targets, minimised during training
- **Backpropagation**: computing the gradient of the loss with respect to every weight using the chain rule
- **Epoch**: one full pass through the training data
- **Learning rate**: the step size used when updating weights
- **Adam**: an optimiser that adapts each parameter's step size using running averages of gradients
- **Dropout**: randomly disabling units during training to reduce overfitting
- **Batch normalisation**: normalising layer inputs over a mini-batch to stabilise training
- **Convolution**: sliding a small learned filter over an input to detect local patterns
- **LSTM**: long short-term memory; a recurrent unit with gates that control what is remembered
- **Self-attention**: a mechanism in which each position in a sequence weighs every other position

## Further reading
- Ian Goodfellow, Yoshua Bengio, and Aaron Courville, *Deep Learning* (MIT Press)
- Simon J. D. Prince, *Understanding Deep Learning* (MIT Press)
- Aston Zhang, Zachary C. Lipton, Mu Li, and Alexander J. Smola, *Dive into Deep Learning* (Cambridge University Press)
- Michael Nielsen, *Neural Networks and Deep Learning* (Determination Press)
