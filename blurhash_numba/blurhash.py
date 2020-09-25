import math
import numpy as np
import numba as nb
from numba import types

alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%*+,-.:;=?@[]^_{|}~"

@nb.njit(nb.uint64(types.string))
def base83_decode(base83_str):
    value = 0
    for base83_char in base83_str:
        value = value * 83 + alphabet.index(base83_char)
    return value

@nb.njit(types.string(nb.uint64, nb.uint8))
def base83_encode(value, length):
    if value // (83 ** (length)) != 0:
        raise ValueError("Specified length is too short to encode given value.")
        
    result = ""
    for i in range(1, length + 1):
        digit = value // (83 ** (length - i)) % 83
        result += alphabet[int(digit)]
    return result

@nb.njit(nb.float64(nb.float64))
def srgb_to_linear(value):
    value = float(value) / 255.0
    if value <= 0.04045:
        return value / 12.92
    return math.pow((value + 0.055) / 1.055, 2.4)

@nb.njit(nb.float64(nb.float64,nb.float32))
def sign_pow(value, exp):
    return math.copysign(math.pow(abs(value), exp), value)

@nb.njit(nb.float64(nb.float64))
def linear_to_srgb(value):
    value = max(0.0, min(1.0, value))
    if value <= 0.0031308:
        return value * 12.92 * 255 + 0.5
    return (1.055 * math.pow(value, 1 / 2.4) - 0.055) * 255 + 0.5

@nb.njit(types.UniTuple(nb.uint16,2)(types.string))
def blurhash_components(blurhash):
    if len(blurhash) < 6:
        raise ValueError("BlurHash must be at least 6 characters long.")
    
    # Decode metadata
    size_info = base83_decode(blurhash[0])
    size_y = int(size_info / 9) + 1
    size_x = (size_info % 9) + 1
    
    return size_x, size_y

@nb.njit(nb.float64[:, :, :](types.string, nb.uint16, nb.uint16, nb.float64, nb.boolean))
def blurhash_decode(blurhash, width, height, punch, linear):
    if len(blurhash) < 6:
        raise ValueError("BlurHash must be at least 6 characters long.")
    
    # Decode metadata
    size_info = base83_decode(blurhash[0])
    size_y = int(size_info / 9) + 1
    size_x = (size_info % 9) + 1
    
    quant_max_value = base83_decode(blurhash[1])
    real_max_value = (float(quant_max_value + 1) / 166.0) * punch
    
    # Make sure we at least have the right number of characters
    if len(blurhash) != 4 + 2 * size_x * size_y:
        raise ValueError("Invalid BlurHash length.")
        
    # Decode DC component
    dc_value = base83_decode(blurhash[2:6])
    colours = [(
        srgb_to_linear(dc_value >> 16),
        srgb_to_linear((dc_value >> 8) & 255),
        srgb_to_linear(dc_value & 255)
    )]
    
    # Decode AC components
    for component in range(1, size_x * size_y):
        ac_value = base83_decode(blurhash[4+component*2:4+(component+1)*2])
        colours.append((
            sign_pow((float(int(ac_value / (19 * 19))) - 9.0) / 9.0, 2.0) * real_max_value,
            sign_pow((float(int(ac_value / 19) % 19) - 9.0) / 9.0, 2.0) * real_max_value,
            sign_pow((float(ac_value % 19) - 9.0) / 9.0, 2.0) * real_max_value
        ))
    
    # Return image RGB values, as a list of lists of lists, 
    # consumable by something like numpy or PIL.
    pixels = np.zeros((height, width, 3))
    for y in range(height):
        for x in range(width):
            for j in range(size_y):
                for i in range(size_x):
                    basis = math.cos(math.pi * float(x) * float(i) / float(width)) * \
                            math.cos(math.pi * float(y) * float(j) / float(height))
                    colour = colours[i + j * size_x]
                    pixels[y][x][0] += colour[0] * basis
                    pixels[y][x][1] += colour[1] * basis
                    pixels[y][x][2] += colour[2] * basis
            if linear == False:
                pixels[y][x][0] = linear_to_srgb(pixels[y][x][0])
                pixels[y][x][1] = linear_to_srgb(pixels[y][x][1])
                pixels[y][x][2] = linear_to_srgb(pixels[y][x][2])
    return pixels

@nb.njit(types.string(nb.float64[:, :, :], nb.uint16, nb.uint16, nb.boolean))
def blurhash_encode(image, x_components, y_components, linear):
    if x_components < 1 or x_components > 9 or y_components < 1 or y_components > 9: 
        raise ValueError("x and y component counts must be between 1 and 9 inclusive.")
    height = len(image)
    width = len(image[0])
    
    # Convert to linear if neeeded
    
    if linear == False:
        image_linear = np.zeros(image.shape)
        for y in range(height):
            for x in range(width):
                image_linear[y][x][0] = srgb_to_linear(image[y][x][0])
                image_linear[y][x][1] = srgb_to_linear(image[y][x][1])
                image_linear[y][x][2] = srgb_to_linear(image[y][x][2])
    else:
        image_linear = image

    # Calculate components
    components = []
    max_ac_component = 0.0
    for j in range(y_components):
        for i in range(x_components):
            norm_factor = 1.0 if (i == 0 and j == 0) else 2.0
            component = [0.0, 0.0, 0.0]
            for y in range(height):
                for x in range(width):
                    basis = norm_factor * math.cos(math.pi * float(i) * float(x) / width) * \
                                          math.cos(math.pi * float(j) * float(y) / height)
                    component[0] += basis * image_linear[y][x][0]
                    component[1] += basis * image_linear[y][x][1]
                    component[2] += basis * image_linear[y][x][2]
                    
            component[0] /= (width * height)
            component[1] /= (width * height)
            component[2] /= (width * height)
            components.append(component)
            
            if not (i == 0 and j == 0):
                max_ac_component = max(max_ac_component, abs(component[0]), abs(component[1]), abs(component[2]))
                
    # Encode components
    dc_value = (int(linear_to_srgb(components[0][0])) << 16) + \
               (int(linear_to_srgb(components[0][1])) << 8) + \
               int(linear_to_srgb(components[0][2]))
    
    quant_max_ac_component = int(max(0, min(82, math.floor(max_ac_component * 166 - 0.5))))
    ac_component_norm_factor = float(quant_max_ac_component + 1) / 166.0
    
    ac_values = []
    for r, g, b in components[1:]:
        ac_values.append(
            int(max(0.0, min(18.0, math.floor(sign_pow(r / ac_component_norm_factor, 0.5) * 9.0 + 9.5)))) * 19 * 19 + \
            int(max(0.0, min(18.0, math.floor(sign_pow(g / ac_component_norm_factor, 0.5) * 9.0 + 9.5)))) * 19 + \
            int(max(0.0, min(18.0, math.floor(sign_pow(b / ac_component_norm_factor, 0.5) * 9.0 + 9.5))))
        )
        
    # Build final blurhash
    blurhash = ""
    blurhash += base83_encode((x_components - 1) + (y_components - 1) * 9, 1)
    blurhash += base83_encode(quant_max_ac_component, 1)
    blurhash += base83_encode(dc_value, 4)
    for ac_value in ac_values:
        blurhash += base83_encode(ac_value, 2)
    
    return blurhash

def decode(blurhash, width, height, punch = 1.0, linear = False):
    return blurhash_decode(blurhash, width, height, punch, linear)

def encode(image, x_components = 4, y_components = 4, linear = False):
    return blurhash_encode(image, x_components, y_components, linear)