import numpy as np
import torch
import torch.nn as nn
from torch.nn.modules.loss import _Loss
import torch.nn.init as init
from torchvision import models

class PosCNN(nn.Module):
    def __init__(self):
        super(PosCNN, self).__init__()

        self.fc1 = fc()
        self.fc2 = fc()
        self.fc3 = fc()
        self.fc4 = fc()

        self._initialize_weights()

    def forward(self, x):
        x1 = self.fc1(x.view(x.size(0),-1))
        x2 = self.fc2(x.view(x.size(0),-1))
        x3 = self.fc3(x.view(x.size(0),-1))
        x4 = self.fc4(x.view(x.size(0),-1))
        return x1, x2, x3, x4

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

class fc(torch.nn.Module):
    def __init__(self, requires_grad=False):
        super(fc, self).__init__()

        layers = []

        layers.append(nn.Linear(in_features=5*5*512, out_features=4096))
        layers.append(nn.Linear(in_features=4096, out_features=1000))
        layers.append(nn.Linear(in_features=1000, out_features=2))

        self.fc = nn.Sequential(*layers)

    def forward(self, x):
        return self.fc(x)

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
        return vgg54
