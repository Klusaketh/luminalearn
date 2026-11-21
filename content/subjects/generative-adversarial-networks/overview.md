A generative adversarial network (GAN) learns to create new data, such as realistic images, by setting two neural networks against each other. A generator turns random noise into samples, and a discriminator tries to tell those samples from real data. As each improves, the generator is pushed towards producing samples the discriminator cannot distinguish from the real thing. GANs, introduced in 2014, produced the first convincingly realistic synthetic faces and remain a key idea in generative modelling.

This subject starts with generative modelling in general and the difference between explicit and implicit density models. It then examines the generator and its latent space, and the discriminator as a classifier or, in Wasserstein GANs, a critic. The training module frames GAN learning as a two-player minimax game and explains why training is unstable. The loss module introduces the Wasserstein loss and the earth mover's distance. Architecture modules cover DCGAN design principles, conditional GANs, and image-to-image translation with pix2pix and CycleGAN. The subject closes with mode collapse, evaluation with the Fréchet Inception Distance, a comparison of GANs with variational autoencoders and diffusion models, and the responsible use of generative models.

The lessons focus on understanding why each design choice was made, so that published GAN papers become readable.

## What you will learn
- Distinguish explicit and implicit generative models and explain what a GAN learns
- Describe generator architectures and how a latent space encodes variation
- Explain the discriminator's role as a classifier and as a critic
- Formulate GAN training as a minimax game and explain its equilibrium
- Explain the Wasserstein loss and why the earth mover's distance gives more useful gradients
- Apply DCGAN architectural guidelines for stable image generation
- Condition generation on labels and translate images with pix2pix and CycleGAN
- Recognise mode collapse and evaluate generators with the Fréchet Inception Distance
- Compare GANs, VAEs, and diffusion models and discuss the risks of synthetic media

## Prerequisites
- Deep learning: neural networks, backpropagation, and convolutional layers (see the Deep Learning subject)
- Probability: distributions and expectation (see the Probability subject)
- Python programming

## Glossary
- **Generative model**: a model that learns a data distribution well enough to produce new samples from it
- **Generator**: the network that maps random latent vectors to synthetic samples
- **Discriminator**: the network that estimates whether a sample is real or generated
- **Critic**: the Wasserstein GAN's discriminator, which outputs a score instead of a probability
- **Latent space**: the space of random input vectors from which the generator creates samples
- **Minimax game**: a game in which one player minimises an objective that the other maximises
- **Mode collapse**: a failure in which the generator produces only a few kinds of output
- **Wasserstein distance**: a measure of the cost of transforming one distribution into another
- **Conditional GAN**: a GAN whose generator and discriminator also receive a label or other condition
- **Fréchet Inception Distance (FID)**: a metric comparing feature statistics of real and generated images; lower is better
- **Diffusion model**: a generative model that learns to reverse a gradual noising process

## Further reading
- Ian Goodfellow et al., "Generative Adversarial Nets", *Advances in Neural Information Processing Systems* (2014)
- Martin Arjovsky, Soumith Chintala, and Léon Bottou, "Wasserstein Generative Adversarial Networks", *Proceedings of the International Conference on Machine Learning* (2017)
- David Foster, *Generative Deep Learning* (O'Reilly Media)
- Ian Goodfellow, Yoshua Bengio, and Aaron Courville, *Deep Learning* (MIT Press)
