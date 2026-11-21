Natural language processing (NLP) gives computers the ability to work with human language: to classify it, extract information from it, translate it, and generate it. Search engines, spam filters, voice assistants, translation services, and chatbots such as LuminaLearn's own tutor all rely on NLP. The field has moved from hand-built rules to statistics to neural networks, and each stage still explains something about how today's large language models work.

This subject follows that path. It begins with turning raw text into numbers: normalisation, bag-of-words and TF-IDF representations, and subword tokenisation with byte-pair encoding and WordPiece. It then covers n-gram language models and perplexity, text classification and sentiment analysis, and sequence labelling for part-of-speech tagging and named entity recognition. Word2Vec introduces dense word embeddings and distributional semantics. Sequence-to-sequence models with attention show how neural machine translation works. The final modules compare encoder and decoder transformer models, explain how large language models are pretrained, fine-tuned, and prompted, and show how embeddings and retrieval-augmented generation ground a model's answers in source documents.

Each lesson includes small worked examples, such as computing TF-IDF scores or bigram probabilities by hand.

## What you will learn
- Normalise text and represent documents with bag-of-words and TF-IDF
- Explain subword tokenisation with BPE and WordPiece and why it handles unseen words
- Build n-gram language models, apply smoothing, and evaluate them with perplexity
- Train and evaluate text classifiers for tasks such as sentiment analysis
- Tag sequences for part-of-speech tagging and named entity recognition
- Explain how Word2Vec learns embeddings and what vector arithmetic on words reveals
- Describe encoder-decoder models with attention for machine translation
- Compare encoder-only, decoder-only, and encoder-decoder transformers
- Explain pretraining, fine-tuning, and prompting of large language models
- Build retrieval-augmented generation pipelines with embeddings and vector search

## Prerequisites
- Python programming
- Probability basics: conditional probability and Bayes' theorem
- Machine learning and deep learning fundamentals, including neural networks (see the Deep Learning subject)

## Glossary
- **Token**: a unit of text, such as a word or subword, that a model processes
- **Corpus**: a large collection of text used for training or analysis
- **TF-IDF**: term frequency-inverse document frequency; a word weight that favours terms distinctive to a document
- **Language model**: a model that assigns probabilities to sequences of tokens
- **Perplexity**: a measure of how well a language model predicts text; lower is better
- **Embedding**: a dense vector representing a token or text so that similar meanings lie close together
- **Named entity recognition (NER)**: labelling spans of text as people, places, organisations, and so on
- **Attention**: a mechanism that lets a model weigh different parts of its input for each output
- **Transformer**: a neural architecture built on self-attention instead of recurrence
- **Fine-tuning**: further training of a pretrained model on a smaller task-specific dataset
- **Prompt**: the input text that instructs a language model what to produce
- **Retrieval-augmented generation (RAG)**: retrieving relevant documents and giving them to a model as context for its answer

## Further reading
- Daniel Jurafsky and James H. Martin, *Speech and Language Processing* (Prentice Hall)
- Yoav Goldberg, *Neural Network Methods for Natural Language Processing* (Morgan & Claypool)
- Lewis Tunstall, Leandro von Werra, and Thomas Wolf, *Natural Language Processing with Transformers* (O'Reilly Media)
- Ashish Vaswani et al., "Attention Is All You Need", *Advances in Neural Information Processing Systems* (2017)
