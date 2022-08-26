

def compute_conv_out(n_input, stride, filter_size, padding):
    """
    computes the number of variables in the output of the convolutional layer dimension
    """
    return ((n_input - filter_size + 2 * padding) / stride) + 1