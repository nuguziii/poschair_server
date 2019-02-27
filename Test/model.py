# -*- coding: utf-8 -*-

# =============================================================================
# PosCNN deep learning model network
#
# by Chae Eun Lee (02/2019)
# nuguziii@naver.com
# https://github.com/nuguziii
# =============================================================================

# no need to run this code separately!!

import numpy as np
import torch
import torch.nn as nn
from torch.nn.modules.loss import _Loss
import torch.nn.init as init
from torchvision import models

class PosCNN(nn.Module):
    def __init__(self):
        super(PosCNN, self).__init__()
        layers = []

        self.vgg = vgg19()
        self.vgg.eval()

        layers.append(nn.Linear(in_features=11*11*512, out_features=4096))
        layers.append(nn.Linear(in_features=4096, out_features=1000))
        layers.append(nn.Linear(in_features=1000, out_features=12))

        self.fc = nn.Sequential(*layers)
        self._initialize_weights()

    def forward(self, x):
        x = self.vgg(x)[1]
        x = x.view(x.size(0),-1)
        out = self.fc(x)
        return out

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                init.orthogonal_(m.weight)
                print('init weight')
                if m.bias is not None:
                    init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                init.xavier_uniform(m.weight)
                if m.bias is not None:
                    m.bias.data.fill_(0.01)

class vgg19(torch.nn.Module):
    def __init__(self, requires_grad=False):
        super(vgg19, self).__init__()
        vgg_pretrained_features = models.vgg19(pretrained=True).features
        self.slice1 = torch.nn.Sequential()
        self.slice2 = torch.nn.Sequential()

        for x in range(8):
            self.slice1.add_module(str(x), vgg_pretrained_features[x])
        for x in range(8, 35):
            self.slice2.add_module(str(x), vgg_pretrained_features[x])
        if not requires_grad:
            for param in self.parameters():
                param.requires_grad = False

    def forward(self, x):
        h = self.slice1(x)
        vgg22 = h
        h = self.slice2(h)
        vgg54 = h
        return vgg22, vgg54
