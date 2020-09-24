# blurhash-numba

## What is BlurHash?

BlurHash is a compact representation of a placeholder for an image.  

<img src="https://raw.githubusercontent.com/woltapp/blurhash/master/Media/WhyBlurHash.png" width="600">

BlurHash encoder consumes an image, and provides a short string (only 20-30 characters!) that represents the placeholder for the image. You perform this on the backend of your service, and store the string along with the image. When you send data to any client, you send both the URL to the image, and the BlurHash string. Your client then takes the string, and decodes it into an image that it shows while the real image is loading over the network. The string is short enough that it comfortably fits into whatever data format you use. For instance, it can easily be added as a field in a JSON object.

In summary:

<img src="https://raw.githubusercontent.com/woltapp/blurhash/master/Media/HowItWorks1.jpg" width="250">&nbsp;&nbsp;&nbsp;<img src="https://raw.githubusercontent.com/woltapp/blurhash/master/Media/HowItWorks2.jpg" width="250">

Ream more about the algorithm [here](https://github.com/woltapp/blurhash/blob/master/Algorithm.md).

## Why blurhash-numba?

Currently, there is no numpy+numba implementation of the BlurHash algorithm. This project is based on the [pure python implementation](https://github.com/halcy/blurhash-python) of BlurHash and supercharges it using **numba** to provide fast encoding and decoding of images.

# Installation

You can install `blurhash-numba` using pip3
```
$ pip3 install blurhash-numba
```

# Usage

Create blurhash from image file
```python
import blurhash_numba as bn

with open('image.jpg', 'r') as image_file:
    hash = bn.encode(image_file, x_components=4, y_components=3)
```
You can also pass file name as parameter to the function
```python
import blurhash_numba as bn

hash = bn.encode('image.jpg', x_components=4, y_components=3)
```
`y_components` and `x_components` parameters adjust the amount of
vertical and horizontal AC components in hashed image. Both parameters must
be `>= 1` and `<= 9`.


# Tests

Run test suite with `pytest` in virtual environment
```
$ pytest
```
Use `tox` to run test suite against all supported python versions
```
$ tox
```
