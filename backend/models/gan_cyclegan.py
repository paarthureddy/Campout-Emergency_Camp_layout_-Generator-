"""
Cycle-Consistent GAN (CycleGAN) Architecture
Evaluated for: Shivam Kharat (CB.SC.U4CSE23445)
Project: ReliefPlan AI (Emergency Camp Layout Generator)

Architecture:
- Generators: Dual ResNet-based Generators:
    - G_AB: Satellite Imagery (Domain X) -> Emergency Camp Blueprint (Domain Y)
    - G_BA: Emergency Camp Blueprint (Domain Y) -> Satellite Imagery (Domain X)
- Discriminators: Dual 70x70 PatchGAN Discriminators (D_A and D_B)
Objective:
- Unpaired Adversarial Loss + Cycle-Consistency Loss + Identity Mapping Loss
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class ResidualBlock(nn.Module):
    """Residual Block with Reflection Padding and Instance Normalization"""
    def __init__(self, channels):
        super(ResidualBlock, self).__init__()
        self.block = nn.Sequential(
            nn.ReflectionPad2d(1),
            nn.Conv2d(channels, channels, kernel_size=3, bias=False),
            nn.InstanceNorm2d(channels, affine=True),
            nn.ReLU(inplace=True),
            nn.ReflectionPad2d(1),
            nn.Conv2d(channels, channels, kernel_size=3, bias=False),
            nn.InstanceNorm2d(channels, affine=True)
        )

    def forward(self, x):
        return x + self.block(x)


class CycleGANGenerator(nn.Module):
    """
    ResNet Generator for Unpaired Image Translation
    6 Residual Blocks for 256x256 resolution
    """
    def __init__(self, in_channels=3, out_channels=3, num_res_blocks=6):
        super(CycleGANGenerator, self).__init__()

        # Initial convolution block with reflection padding
        model = [
            nn.ReflectionPad2d(3),
            nn.Conv2d(in_channels, 64, kernel_size=7, bias=False),
            nn.InstanceNorm2d(64, affine=True),
            nn.ReLU(inplace=True)
        ]

        # Downsampling blocks (stride 2)
        in_features = 64
        out_features = in_features * 2
        for _ in range(2):
            model += [
                nn.Conv2d(in_features, out_features, kernel_size=3, stride=2, padding=1, bias=False),
                nn.InstanceNorm2d(out_features, affine=True),
                nn.ReLU(inplace=True)
            ]
            in_features = out_features
            out_features = in_features * 2

        # Residual blocks (bottleneck)
        for _ in range(num_res_blocks):
            model += [ResidualBlock(in_features)]

        # Upsampling blocks (ConvTranspose2d)
        out_features = in_features // 2
        for _ in range(2):
            model += [
                nn.ConvTranspose2d(in_features, out_features, kernel_size=3, stride=2, padding=1, output_padding=1, bias=False),
                nn.InstanceNorm2d(out_features, affine=True),
                nn.ReLU(inplace=True)
            ]
            in_features = out_features
            out_features = in_features // 2

        # Output convolution block
        model += [
            nn.ReflectionPad2d(3),
            nn.Conv2d(64, out_channels, kernel_size=7),
            nn.Tanh()
        ]

        self.model = nn.Sequential(*model)

    def forward(self, x):
        return self.model(x)


class CycleGANDiscriminator(nn.Module):
    """
    70x70 PatchGAN Discriminator for CycleGAN (Single domain evaluation)
    Evaluates realism of a single image without conditioning
    """
    def __init__(self, in_channels=3):
        super(CycleGANDiscriminator, self).__init__()

        def discriminator_block(in_filters, out_filters, normalize=True):
            layers = [nn.Conv2d(in_filters, out_filters, kernel_size=4, stride=2, padding=1)]
            if normalize:
                layers.append(nn.InstanceNorm2d(out_filters, affine=True))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return layers

        self.model = nn.Sequential(
            *discriminator_block(in_channels, 64, normalize=False),  # 256 -> 128
            *discriminator_block(64, 128),                           # 128 -> 64
            *discriminator_block(128, 256),                          # 64 -> 32
            nn.ZeroPad2d((1, 0, 1, 0)),
            nn.Conv2d(256, 512, kernel_size=4, padding=1, bias=False),  # 32 -> 31
            nn.InstanceNorm2d(512, affine=True),
            nn.LeakyReLU(0.2, inplace=True),
            nn.ZeroPad2d((1, 0, 1, 0)),
            nn.Conv2d(512, 1, kernel_size=4, padding=1)                  # 31 -> 30
        )

    def forward(self, x):
        return self.model(x)


class CycleGANModel(nn.Module):
    """
    Full CycleGAN Pipeline Wrapper
    Allocated for: Shivam Kharat (CB.SC.U4CSE23445)
    """
    def __init__(self, in_channels=3, out_channels=3, lambda_cyc=10.0, lambda_id=5.0):
        super(CycleGANModel, self).__init__()
        self.student_name = "Shivam Kharat"
        self.roll_no = "CB.SC.U4CSE23445"
        self.model_type = "Cycle-Consistent GAN (CycleGAN)"
        self.lambda_cyc = lambda_cyc
        self.lambda_id = lambda_id

        # Dual generators
        self.G_AB = CycleGANGenerator(in_channels, out_channels)  # Satellite -> Camp Layout Blueprint
        self.G_BA = CycleGANGenerator(out_channels, in_channels)  # Camp Layout Blueprint -> Satellite

        # Dual discriminators
        self.D_A = CycleGANDiscriminator(in_channels)             # Real vs Fake Satellite
        self.D_B = CycleGANDiscriminator(out_channels)            # Real vs Fake Blueprint

        # Loss functions
        self.criterion_gan = nn.MSELoss()  # LSGAN formulation for stable training
        self.criterion_cycle = nn.L1Loss()
        self.criterion_identity = nn.L1Loss()

    def forward(self, real_A):
        """Standard inference: Satellite (A) -> Blueprint (B)"""
        return self.G_AB(real_A)

    def compute_generator_loss(self, real_A, real_B):
        # Identity loss
        id_A = self.G_BA(real_A)
        loss_id_A = self.criterion_identity(id_A, real_A) * self.lambda_id
        id_B = self.G_AB(real_B)
        loss_id_B = self.criterion_identity(id_B, real_B) * self.lambda_id
        loss_identity = (loss_id_A + loss_id_B) * 0.5

        # Adversarial loss
        fake_B = self.G_AB(real_A)
        pred_fake_B = self.D_B(fake_B)
        loss_gan_AB = self.criterion_gan(pred_fake_B, torch.ones_like(pred_fake_B))

        fake_A = self.G_BA(real_B)
        pred_fake_A = self.D_A(fake_A)
        loss_gan_BA = self.criterion_gan(pred_fake_A, torch.ones_like(pred_fake_A))
        loss_gan = (loss_gan_AB + loss_gan_BA) * 0.5

        # Cycle-consistency loss: A -> B -> A and B -> A -> B
        recov_A = self.G_BA(fake_B)
        loss_cycle_A = self.criterion_cycle(recov_A, real_A) * self.lambda_cyc

        recov_B = self.G_AB(fake_A)
        loss_cycle_B = self.criterion_cycle(recov_B, real_B) * self.lambda_cyc
        loss_cycle = (loss_cycle_A + loss_cycle_B) * 0.5

        total_g_loss = loss_gan + loss_cycle + loss_identity
        return total_g_loss, loss_gan, loss_cycle, loss_identity, fake_B, fake_A

    def compute_discriminator_loss_A(self, real_A, fake_A):
        pred_real = self.D_A(real_A)
        loss_real = self.criterion_gan(pred_real, torch.ones_like(pred_real))
        pred_fake = self.D_A(fake_A.detach())
        loss_fake = self.criterion_gan(pred_fake, torch.zeros_like(pred_fake))
        return (loss_real + loss_fake) * 0.5

    def compute_discriminator_loss_B(self, real_B, fake_B):
        pred_real = self.D_B(real_B)
        loss_real = self.criterion_gan(pred_real, torch.ones_like(pred_real))
        pred_fake = self.D_B(fake_B.detach())
        loss_fake = self.criterion_gan(pred_fake, torch.zeros_like(pred_fake))
        return (loss_real + loss_fake) * 0.5
