import torch
import torch.nn as nn
import torch.nn.functional as F

class ASPP(nn.Module):
    """
    Atrous Spatial Pyramid Pooling (ASPP)
    Captures multi-scale contextual information.
    """
    def __init__(self, in_channels, out_channels, atrous_rates):
        super(ASPP, self).__init__()
        
        # 1x1 convolution
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU()
        )
        
        # Dilated convolutions
        self.conv2 = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=atrous_rates[0], dilation=atrous_rates[0], bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU()
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=atrous_rates[1], dilation=atrous_rates[1], bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU()
        )
        self.conv4 = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=atrous_rates[2], dilation=atrous_rates[2], bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU()
        )
        
        # Global Average Pooling
        self.gap = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_channels, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU()
        )
        
        self.project = nn.Sequential(
            nn.Conv2d(5 * out_channels, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(),
            nn.Dropout(0.5)
        )

    def forward(self, x):
        res1 = self.conv1(x)
        res2 = self.conv2(x)
        res3 = self.conv3(x)
        res4 = self.conv4(x)
        
        res5 = self.gap(x)
        res5 = F.interpolate(res5, size=x.shape[2:], mode='bilinear', align_corners=False)
        
        out = torch.cat([res1, res2, res3, res4, res5], dim=1)
        return self.project(out)

class DeepLabV3Plus(nn.Module):
    """
    DeepLabV3+ with a simplified backbone (ResNet-like block)
    Provides robust multi-scale feature extraction compared to U-Net.
    """
    def __init__(self, n_channels=3, n_classes=7):
        super(DeepLabV3Plus, self).__init__()
        
        # Simplified backbone (Entry flow)
        self.backbone_low = nn.Sequential(
            nn.Conv2d(n_channels, 64, 3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU()
        )
        
        self.backbone_high = nn.Sequential(
            nn.MaxPool2d(3, stride=2, padding=1),
            nn.Conv2d(64, 128, 3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(128, 256, 3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU()
        )
        
        # ASPP Module
        self.aspp = ASPP(in_channels=256, out_channels=256, atrous_rates=[6, 12, 18])
        
        # Decoder
        self.low_level_project = nn.Sequential(
            nn.Conv2d(64, 48, 1, bias=False),
            nn.BatchNorm2d(48),
            nn.ReLU()
        )
        
        self.decoder = nn.Sequential(
            nn.Conv2d(304, 256, 3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Conv2d(256, 256, 3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Conv2d(256, n_classes, 1)
        )

    def forward(self, x):
        input_shape = x.shape[2:]
        
        # Backbone extraction
        low_level_features = self.backbone_low(x)
        high_level_features = self.backbone_high(low_level_features)
        
        # ASPP
        aspp_features = self.aspp(high_level_features)
        
        # Decoder path
        aspp_up = F.interpolate(aspp_features, size=low_level_features.shape[2:], mode='bilinear', align_corners=False)
        low_level_proj = self.low_level_project(low_level_features)
        
        concat_features = torch.cat([aspp_up, low_level_proj], dim=1)
        
        out = self.decoder(concat_features)
        out = F.interpolate(out, size=input_shape, mode='bilinear', align_corners=False)
        
        return out
