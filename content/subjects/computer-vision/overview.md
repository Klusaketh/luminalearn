Computer vision teaches computers to extract meaning from images and video: to recognise objects, locate them, measure them, and understand scenes. It powers face unlock on phones, medical image analysis, quality inspection on production lines, and the perception systems of self-driving cars. Modern vision combines classical image processing with deep neural networks, and this subject covers both.

It begins with how images are formed and stored: pixels, colour spaces, and histograms. The classical modules cover spatial convolution, smoothing and sharpening filters, edge detection, feature detection and description, and geometric transformations with camera models. The deep learning modules study the backbones that turn images into features: residual networks with skip connections, and vision transformers that treat an image as a sequence of patches. The final modules cover single-shot object detection with YOLO, two-stage detectors, detection metrics such as intersection over union and mean average precision, and semantic and instance segmentation.

Lessons work through small numerical examples, such as applying a 3×3 filter by hand or computing an IoU score, before showing how the same operations scale to real images.

## What you will learn
- Represent images as arrays, convert between colour spaces, and interpret histograms
- Apply convolution filters for smoothing, sharpening, and edge detection
- Detect and describe keypoints and match features between images
- Apply geometric transformations and explain the pinhole camera model
- Explain how residual connections make very deep networks trainable
- Describe how vision transformers process images as sequences of patches
- Compare single-shot detectors such as YOLO with two-stage detectors
- Evaluate detectors with intersection over union and mean average precision
- Distinguish semantic segmentation from instance segmentation and describe models for each

## Prerequisites
- Python programming, ideally with NumPy
- Linear algebra: matrices and transformations (see the Linear Algebra subject)
- Deep learning basics, especially convolutional networks (see the Deep Learning subject)

## Glossary
- **Pixel**: the smallest element of a digital image, holding intensity or colour values
- **Colour space**: a system for representing colour, such as RGB or HSV
- **Histogram**: a count of how many pixels have each intensity value
- **Convolution**: sliding a small kernel over an image and computing weighted sums
- **Edge detection**: finding locations where image intensity changes sharply
- **Keypoint**: a distinctive image location, such as a corner, that can be found again in other images
- **Homography**: a transformation mapping points between two views of a plane
- **Residual connection**: a shortcut that adds a layer's input to its output
- **Vision transformer (ViT)**: a transformer that processes an image as a sequence of patches
- **Bounding box**: a rectangle locating an object in an image
- **Intersection over union (IoU)**: the overlap between a predicted and a true box divided by their union
- **Semantic segmentation**: labelling every pixel with a class
- **Instance segmentation**: labelling every pixel with both a class and the individual object it belongs to

## Further reading
- Richard Szeliski, *Computer Vision: Algorithms and Applications* (Springer)
- Rafael C. Gonzalez and Richard E. Woods, *Digital Image Processing* (Pearson)
- David A. Forsyth and Jean Ponce, *Computer Vision: A Modern Approach* (Pearson)
- Simon J. D. Prince, *Understanding Deep Learning* (MIT Press)
