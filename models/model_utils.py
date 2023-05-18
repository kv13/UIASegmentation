import torch
from models import uia_models as models

def get_model(which_model, config):
    '''
    This function initializes the model

    Parameters
    ----------
    which_model: The options are:
        1) Unet encoder/decoder without skip-connections
        2) ...

    Returns
    -------
    model: Torch neural network
    '''
    if which_model == 'unet_no_skip_connections':
        model = models.SimpleUNet3D(activation_func = config.activation_function, 
                                    in_channels     = 1, 
                                    out_channels    = 1, 
                                    exp_type        = config.experiment_type)
        return model
    elif which_model == 'unet_skip_connections':
        model = models.UNet3D(activation_func = config.activation_function,
                              in_channels     = 1,
                              out_channels    = 1,
                              exp_type        = config.experiment_type)
        return model
    elif which_model == 'graph-unet':
        return None
    else:
        raise NotImplementedError(f'The model {which_model} is not implemented')

def get_optimizer(model, which_optimizer, lr=0.01, wd=0.01):
    '''
    This function initializes the optimizer

    Parameters
    ----------
    model: The used model
    which_optimizer: The options are:
        1) adam
        2) ...
    lr: learning rate
    wd: weight decay
    Returns
    -------
    optimizer
    '''
    if which_optimizer.lower() == 'adam':
        optimizer = torch.optim.Adam(model.parameters(), lr = lr, weight_decay = wd)
        return optimizer
    elif which_optimizer.lower() == 'adamw':
        # Good for image classification. To achieve state-of-the-art results is used 
        # with OneCycleLR scheduler
        optimizer = torch.optim.AdamW(model.parameters(), lr = lr, weight_decay = wd)
        return optimizer
    elif which_optimizer.lower() == 'adagrad':
        # You can avoid using a scheduler because, Adagrad dynamically adapts the learning
        # rate itself. It is used for sparse datasets.
        optimizer = torch.optim.Adagrad(model.parameters(), lr = lr, weight_decay = wd)
        return optimizer

def get_loss(which_loss):
    '''
    This function defines the criterion used for optimizing

    Parameters
    ----------
    which_loss: The options are:
        1) ...
        2) ...

    Returns
    -------
    criterion
    '''
    if which_loss == 'dice_loss':
        return dice_loss
    return None

#---------- losses
def dice_loss(batch_preds, batch_targets, smooth = 1e-05, reduction = 'mean'):
    
    pflat        = batch_preds.float().contiguous().view(batch_preds.shape[0], -1)
    tflat        = batch_targets.float().contiguous().view(batch_targets.shape[0], -1)
    intersection = torch.sum(torch.mul(pflat, tflat), dim = 1)
    nom          = 2. * intersection + smooth
    denom        = torch.sum(pflat, dim=1) + torch.sum(tflat, dim = 1) + smooth
    dice_losses  = 1 - nom/denom
    
    if reduction == 'mean':
        loss = torch.mean(dice_losses)
    elif reduction == 'sum':
        loss = torch.sum(dice_losses)
    else:
        raise NotImplementedError(f'Dice loss reduction {reduction} not implemented') 
    return loss 