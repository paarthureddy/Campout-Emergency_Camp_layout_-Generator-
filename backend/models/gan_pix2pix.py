"""
Pix2Pix Conditional GAN (cGAN) Architecture
Evaluated for: Paarthu Reddy (CB.SC.U4CSE23639) - Team Lead
Project: ReliefPlan AI (Emergency Camp Layout Generator)

Architecture:
- Generator: U-Net 256 Encoder-Decoder with Skip Connections
- Discriminator: 70x70 PatchGAN Markovian Discriminator
Objective:
- Conditional Adversarial Loss + L1 Reconstruction Loss
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class UNetDown(nn.Module):
    """Encoder downsampling block: Conv -> InstanceNorm -> LeakyReLU"""
    def __init__(self, in_channels, out_channels, normalize=True, dropout=0.0):
        super(UNetDown, self).__init__()
        layers = [nn.Conv2d(in_channels, out_channels, kernel_size=4, stride=2, padding=1, bias=False)]
        if normalize:
            layers.append(nn.InstanceNorm2d(out_channels, affine=True))
        layers.append(nn.LeakyReLU(0.2, inplace=True))
        if dropout > 0:
            layers.append(nn.Dropout(dropout))
        self.block = nn.Sequential(*layers)

    def forward(self, x):
        return self.block(x)


class UNetUp(nn.Module):
    """Decoder upsampling block: ConvTranspose -> InstanceNorm -> ReLU (+ Skip Concat)"""
    def __init__(self, in_channels, out_channels, dropout=0.0):
        super(UNetUp, self).__init__()
        layers = [
            nn.ConvTranspose2d(in_channels, out_channels, kernel_size=4, stride=2, padding=1, bias=False),
            nn.InstanceNorm2d(out_channels, affine=True),
            nn.ReLU(inplace=True)
        ]
        if dropout > 0:
            layers.append(nn.Dropout(dropout))
        self.block = nn.Sequential(*layers)

    def forward(self, x, skip_input):
        x = self.block(x)
        # Concatenate along channel dimension with skip connection
        x = torch.cat((x, skip_input), dim=1)
        return x


class Pix2PixGenerator(nn.Module):
    """
    U-Net 256 Generator for Paired Image Translation (Satellite Image -> Camp Layout Blueprint)
    """
    def __init__(self, in_channels=3, out_channels=3):
        super(Pix2PixGenerator, self).__init__()
        self.down1 = UNetDown(in_channels, 64, normalize=False)  # 256 -> 128
        self.down2 = UNetDown(64, 128)                           # 128 -> 64
        self.down3 = UNetDown(128, 256)                          # 64 -> 32
        self.down4 = UNetDown(256, 512, dropout=0.5)             # 32 -> 16
        self.down5 = UNetDown(512, 512, dropout=0.5)             # 16 -> 8
        self.down6 = UNetDown(512, 512, dropout=0.5)             # 8 -> 4
        self.down7 = UNetDown(512, 512, dropout=0.5)             # 4 -> 2
        self.down8 = UNetDown(512, 512, normalize=False)         # 2 -> 1 (Bottleneck)

        self.up1 = UNetUp(512, 512, dropout=0.5)                 # 1 -> 2
        self.up2 = UNetUp(1024, 512, dropout=0.5)                # 2 -> 4
        self.up3 = UNetUp(1024, 512, dropout=0.5)                # 4 -> 8
        self.up4 = UNetUp(1024, 512)                             # 8 -> 16
        self.up5 = UNetUp(1024, 256)                             # 16 -> 32
        self.up6 = UNetUp(512, 128)                              # 32 -> 64
        self.up7 = UNetUp(256, 64)                               # 64 -> 128

        self.final = nn.Sequential(
            nn.ConvTranspose2d(128, out_channels, kernel_size=4, stride=2, padding=1),  # 128 -> 256
            nn.Tanh()  # Output range [-1, 1]
        )

    def forward(self, x):
        d1 = self.down1(x)
        d2 = self.down2(d1)
        d3 = self.down3(d2)
        d4 = self.down4(d3)
        d5 = self.down5(d4)
        d6 = self.down6(d5)
        d7 = self.down7(d6)
        d8 = self.down8(d7)

        u1 = self.up1(d8, d7)
        u2 = self.up2(u1, d6)
        u3 = self.up3(u2, d5)
        u4 = self.up4(u3, d4)
        u5 = self.up5(u4, d3)
        u6 = self.up6(u5, d2)
        u7 = self.up7(u6, d1)

        return self.final(u7)


class PatchGANDiscriminator(nn.Module):
    """
    70x70 PatchGAN Discriminator evaluating realism of conditioned layout image
    Input: Concatenation of Condition (Satellite) + Target (Blueprint), total channels = in_channels * 2
    """
    def __init__(self, in_channels=3):
        super(PatchGANDiscriminator, self).__init__()

        def discriminator_block(in_filters, out_filters, normalize=True):
            layers = [nn.Conv2d(in_filters, out_filters, kernel_size=4, stride=2, padding=1)]
            if normalize:
                layers.append(nn.InstanceNorm2d(out_filters, affine=True))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return layers

        self.model = nn.Sequential(
            *discriminator_block(in_channels * 2, 64, normalize=False),  # 256 -> 128
            *discriminator_block(64, 128),                               # 128 -> 64
            *discriminator_block(128, 256),                              # 64 -> 32
            nn.ZeroPad2d((1, 0, 1, 0)),
            nn.Conv2d(256, 512, kernel_size=4, padding=1, bias=False),  # 32 -> 31
            nn.InstanceNorm2d(512, affine=True),
            nn.LeakyReLU(0.2, inplace=True),
            nn.ZeroPad2d((1, 0, 1, 0)),
            nn.Conv2d(512, 1, kernel_size=4, padding=1)                  # 31 -> 30 (Patch outputs)
        )

    def forward(self, img_cond, img_target):
        # Concatenate condition image and target image along channels
        img_input = torch.cat((img_cond, img_target), dim=1)
        return self.model(img_input)


class Pix2PixModel(nn.Module):
    """
    Full Pix2Pix Pipeline Wrapper with Generator and Discriminator
    Allocated for: Paarthu Reddy (CB.SC.U4CSE23639)
    """
    def __init__(self, in_channels=3, out_channels=3, lambda_l1=100.0):
        super(Pix2PixModel, self).__init__()
        self.student_name = "Paarthu Reddy"
        self.roll_no = "CB.SC.U4CSE23639"
        self.model_type = "Pix2Pix Conditional GAN (cGAN)"
        self.lambda_l1 = lambda_l1

        self.generator = Pix2PixGenerator(in_channels, out_channels)
        self.discriminator = PatchGANDiscriminator(in_channels)
        self.criterion_gan = nn.BCEWithLogitsLoss()
        self.criterion_l1 = nn.L1Loss()

    def forward(self, x):
        return self.generator(x)

    def compute_generator_loss(self, real_satellite, fake_blueprint, real_blueprint):
        # Discriminator prediction for fake pair
        pred_fake = self.discriminator(real_satellite, fake_blueprint)
        loss_gan = self.criterion_gan(pred_fake, torch.ones_like(pred_fake))
        # L1 reconstruction loss between generated blueprint and ground truth layout
        loss_l1 = self.criterion_l1(fake_blueprint, real_blueprint) * self.lambda_l1
        total_g_loss = loss_gan + loss_l1
        return total_g_loss, loss_gan, loss_l1

    def compute_discriminator_loss(self, real_satellite, fake_blueprint, real_blueprint):
        # Real loss
        pred_real = self.discriminator(real_satellite, real_blueprint)
        loss_real = self.criterion_gan(pred_real, torch.ones_like(pred_real))
        # Fake loss (detach fake to not backprop through generator)
        pred_fake = self.discriminator(real_satellite, fake_blueprint.detach())
        loss_fake = self.criterion_gan(pred_fake, torch.zeros_like(pred_fake))
        total_d_loss = (loss_real + loss_fake) * 0.5
        return total_d_loss, loss_real, loss_fake
