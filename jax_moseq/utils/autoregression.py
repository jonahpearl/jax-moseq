import jax
import jax.numpy as jnp
import jax.random as jr

import tensorflow_probability.substrates.jax.distributions as tfd

from jax_moseq.utils import apply_affine
from jax_moseq.utils.distributions import sample_mniw

na = jnp.newaxis


def apply_ar_params(x, Ab):
    nlags = get_nlags(Ab)
    x_in = get_lags(x, nlags)
    return apply_affine(x_in, Ab)


def ar_log_likelihood(x, params):
    Ab, Q = params
    nlags = get_nlags(Ab)
    mu = apply_ar_params(x, Ab)
    x = x[..., nlags:, :]
    return tfd.MultivariateNormalFullCovariance(mu, Q).log_prob(x)


def get_lags(x, nlags):
    """
    Get lags of a multivariate time series. Lags are concatenated along
    the last dim in time-order. So if the last rows of ``x`` look like

    .. math::

        \begin{bmatrix} 
            x_{t-2}     \\
            x_{t-1}     \\
            x_{t} 
        \end{bmatrix}


    then with ``nlags=3`` they would become

    .. math::

        \begin{bmatrix} 
            x_{t-5} & x_{t-4} & x_{t-3} \\
            x_{t-4} & x_{t-3} & x_{t-2} \\
            x_{t-3} & x_{t-2} & x_{t-1}
        \end{bmatrix}  


    Parameters
    ----------  
    nlags: int
        Number of lags
        
    x: jax array, shape (dims, t, d)
        Batch of d-dimensional time series 
    
    Returns
    -------
    x_lagged: jax array, shape (dims, t-nlags, d*nlags)

    """
    lags = [jnp.roll(x, t, axis=-2) for t in range(1, nlags + 1)]
    return jnp.concatenate(lags[::-1], axis=-1)[..., nlags:, :]


def get_nlags(Ab):
    return Ab.shape[-1] // Ab.shape[-2]