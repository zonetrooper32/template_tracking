# template_tracking
My Python Implementation of Hyperplane Template Tracking Algorithm, and other Template Matching based Tracking algorithm with a touch of Machine Learning methods.

## Introduction

This repo focuses on simple, straightforward implementations of some Template Matching based Tracking algorithms. Those trackers are good study cases for classic combination of Machine Learning and Computer Vision.

This repo is intended for learning purpose only. For general and high performance purpose, feel free to check: [List of Deep Learning based Tracking Methods](https://github.com/foolwood/benchmark_results).

For more complex and efficient use cases of registration-based tracking methods, please check [MTF](http://webdocs.cs.ualberta.ca/~vis/mtf/index.html).

Some key papers in regards of the implementations:

 - [Real Time Robust Template Matching](https://pdfs.semanticscholar.org/7fbc/4c4f01eb9716959ffef8b4a620a3d1c38577.pdf)
 
 - [Hyperplane Approximation for Template Matching](https://ieeexplore.ieee.org/abstract/document/1017625)

 - [Realtime Registration-Based Tracking via Approximate Nearest Neighbour Search](http://www.roboticsproceedings.org/rss09/p44.pdf)

## Requirements
- Python 3.6
- Numpy
- OpenCV
- scikit-learn
- pyflann, optional only for Nearest Neighbor Tracker, [modified version](https://github.com/nashory/pyflann) for python3 support

## Demo
Some demo results for Hyperplane Template Tracker, red box shows the result from the tracker:
<p align="center">
  <img src="images/result_book3.gif" width="128" height="128">
  <img src="images/result_box.gif" width="128" height="128">
  <img src="images/result_cereal.gif" width="170" height="128">
  <img src="images/result_towel.gif" width="170" height="128">
</p>

## Note
Currently, the Hyperplane tracker works with the following conditions:

 - Simply textured planar objects.
 - No strong reflective surface.
 - No strong illumination changes.
 - No occlusions.
 
The implementions to improve the general tracking robustness is ongoing.

## TO-DOs
Some of the to-dos listed here to keep track of implementation progress.

 - [x] Original Uniform Corner Sampling. Done. However not performing as good as the current Gaussian sampling. Not uploaded for now.

 - [ ] Original region sampling using grid points.

 - [ ] Multiple sub-templates tracking.

