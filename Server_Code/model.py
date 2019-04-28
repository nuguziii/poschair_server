import numpy as np
import torch
import torch.nn as nn
from torch.nn.modules.loss import _Loss
import torch.nn.init as init
from torchvision import models
import torch.nn.functional as F

class PosCNN(nn.Module):
    def __init__(self, Net = []):
        super(PosCNN, self).__init__()

        self.fc1 = torch.load(Net[0])
        self.fc2 = torch.load(Net[1])
        self.fc3 = torch.load(Net[2])
        self.fc4 = torch.load(Net[3])

    def forward(self, x):
        x1 = self.fc1(x)
        x2 = self.fc2(x)
        x3 = self.fc3(x)
        x4 = self.fc4(x)
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

class PosCNN_pretrain(nn.Module):
    def __init__(self, num=1, in_channels=1):
        super(PosCNN_pretrain, self).__init__()

        self.net = FCNet(num=num, in_channels=in_channels)

        self._initialize_weights()

    def forward(self, x):
        return self.net(x)

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                init.orthogonal_(m.weight)
                print('init weight')
                if m.bias is not None:
                    init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                init.xavier_uniform(m.weight)
                print('init weight')
                if m.bias is not None:
                    m.bias.data.fill_(0.01)

class FCNet(torch.nn.Module):
    def __init__(self, num=1, in_channels=1, w=10, requires_grad=False):
        super(FCNet, self).__init__()

        self.conv1 = nn.Conv2d(in_channels=in_channels*num, out_channels=in_channels//2, kernel_size=3, padding=1, bias=False)
        self.conv2 = nn.Conv2d(in_channels=in_channels//2, out_channels=16, kernel_size=3, padding=1, bias=False)
        #self.bn1 = nn.BatchNorm2d(2, eps=0.0001, momentum = 0.95)
        #self.relu = nn.ReLU(inplace=True)
        self.pool = nn.MaxPool2d(2,2)

        self.fc1 = nn.Linear(in_features=w*w*16, out_features=64)
        self.fc2 = nn.Linear(in_features=64, out_features=4)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        x = x.view(x.size(0),-1)
        x = F.relu(self.fc1(x))
        x = F.sigmoid(self.fc2(x))
        #x = F.sigmoid(x)
        return x

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
        return vgg22
