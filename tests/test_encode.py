import sys, os
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_path, '..'))

import PIL.Image
from blurhash_numba import encode, decode, components
import numpy as np
import pytest


def test_encode():
    image = PIL.Image.open(os.path.join(base_path, "cool_cat.jpg"))
    image_array = np.array(image.convert("RGB"), dtype=np.float)
    blur_hash = encode(image_array)
    assert blur_hash == "UBMOZfK1GG%LBBNG,;Rj2skq=eE1s9n4S5Na"
    
def test_decode():
    image_array = np.array(decode("UBMOZfK1GG%LBBNG,;Rj2skq=eE1s9n4S5Na", 100, 100)).astype('uint8')
    ref_image = PIL.Image.open(os.path.join(base_path, "cool_cat_decoded.jpg"))
    ref_image_array = np.array(ref_image.convert("RGB"))
    assert np.sum(np.abs(image_array - ref_image_array)) < 1.0

def test_asymmetric():
    image = PIL.Image.open(os.path.join(base_path, "cool_cat.jpg"))
    image_array = np.array(image.convert("RGB"), dtype=np.float)
    blur_hash = encode(image_array, components_x = 2, components_y = 8)
    assert blur_hash == "%BMOZfK1BBNG2skqs9n4?HvgJ.Nav}J-$%sm"
    
    decoded_image = decode(blur_hash, 32, 32)
    assert np.sum(np.var(decoded_image, axis = 0)) > np.sum(np.var(decoded_image, axis = 1))

    blur_hash = encode(image_array, components_x = 8, components_y = 2)
    decoded_image = decode(blur_hash, 32, 32)
    assert np.sum(np.var(decoded_image, axis = 0)) < np.sum(np.var(decoded_image, axis = 1))

def test_components():
    image = PIL.Image.open(os.path.join(base_path, "cool_cat.jpg"))
    image_array = np.array(image.convert("RGB"), dtype=np.float)
    blur_hash = encode(image_array, components_x = 8, components_y = 3)
    size_x, size_y = components(blur_hash)
    assert size_x == 8
    assert size_y == 3

def test_linear_dc_only():
    image = PIL.Image.open(os.path.join(base_path, "cool_cat.jpg"))
    linearish_image = np.array(image.convert("RGB"), dtype=np.float) / 255.0
    blur_hash = encode(linearish_image, components_x = 1, components_y = 1, linear = True)
    avg_color = decode(blur_hash, 1, 1, linear = True)
    reference_avg_color = np.mean(linearish_image.reshape(linearish_image.shape[0] * linearish_image.shape[1], -1), 0)
    assert np.sum(np.abs(avg_color - reference_avg_color)) < 0.01
    
def test_invalid_parameters():
    image = np.array(PIL.Image.open(os.path.join(base_path, "cool_cat.jpg")).convert("RGB"), dtype=np.float)
    
    with pytest.raises(ValueError):
         decode("UBMO", 32, 32)
         
    with pytest.raises(ValueError):
         decode("UBMOZfK1GG%LBBNG", 32, 32)
         
    with pytest.raises(ValueError):
        encode(image, components_x = 0, components_y = 1)
    
    with pytest.raises(ValueError):
        encode(image, components_x = 1, components_y = 0)    
    
    with pytest.raises(ValueError):
        encode(image, components_x = 1, components_y = 10)
      
    with pytest.raises(ValueError):
        encode(image, components_x = 10, components_y = 1)