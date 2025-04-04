# Age and Gender Classification

This project uses a pretrained ONNX model to classify the age and gender of every face detected in an image. All ONNX models are available in the `models` directory.

Follow the instructions below to run the server.

### Install dependencies

Run this in the root directory of the project:
```
poetry install
```

Activate the environment:
```
poetry env activate
```

### Start the server

Run this in the root directory of the project:
```
python -m age_and_gender_detection.server
```

Use [RescueBox-Desktop](https://github.com/UMass-Rescue/RescueBox-Desktop) to connect to the server and classify images.

### Attribution and References

This project uses code and ONNX models from the following repo: https://github.com/onnx/models/tree/main/validated/vision/body_analysis/age_gender

* Levi et al. - [Age and Gender Classification Using Convolutional Neural Networks](https://talhassner.github.io/home/publication/2015_CVPR).
* Rothe et al. - [IMDB-WIKI – 500k+ face images with age and gender labels](https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/).
* Lapuschkin et al. - [Understanding and Comparing Deep Neural Networks for Age and Gender Classification](https://github.com/sebastian-lapuschkin/understanding-age-gender-deep-learning-models).
* Caffe to ONNX: [unofficial converter](https://github.com/asiryan/caffe-onnx).