import torch
import torch.nn as nn


class EncoderBlock(nn.Module):
    def __init__(self, in_channels, out_channels, batchnorm=True):
        super().__init__()
        layers = [
            nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=4, stride=2, padding=1, bias=not batchnorm)
        ]
        if batchnorm:
            layers.append(nn.BatchNorm2d(out_channels))
        layers.append(nn.LeakyReLU(0.2, inplace=True))
        self.model = nn.Sequential(*layers)
    def forward(self, x):
        return self.model(x)
    

class DecoderBlock(nn.Module):
    def __init__(self, in_channels, out_channels, dropout=True):
        super().__init__()
        layers = [
            nn.ConvTranspose2d(in_channels=in_channels, out_channels=out_channels, kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(out_channels)
        ]
        if dropout:
            layers.append(nn.Dropout(0.5))
        self.up_block = nn.Sequential(*layers)
        self.relu = nn.ReLU(inplace=True)
    
    def forward(self, x, skip_input):
        x = self.up_block(x)
        x = torch.cat((x, skip_input), dim=1)
        x = self.relu(x)
        return x


class Generator(nn.Module):
    def __init__(self, in_channels=5, out_channels=1):
        super().__init__()
        self.e1 = EncoderBlock(in_channels=in_channels, out_channels=64, batchnorm=False)
        self.e2 = EncoderBlock(in_channels=64, out_channels=128)
        self.e3 = EncoderBlock(in_channels=128, out_channels=256)
        self.e4 = EncoderBlock(in_channels=256, out_channels=512)
        self.e5 = EncoderBlock(in_channels=512, out_channels=512)
        self.e6 = EncoderBlock(in_channels=512, out_channels=512)
        self.e7 = EncoderBlock(in_channels=512, out_channels=512)

        self.bottleneck_conv = nn.Conv2d(in_channels=512, out_channels=512, kernel_size=4, stride=2, padding=1)
        self.bottleneck_relu = nn.ReLU(inplace=True)

        self.d1 = DecoderBlock(in_channels=512, out_channels=512)
        self.d2 = DecoderBlock(in_channels=1024, out_channels=512)
        self.d3 = DecoderBlock(in_channels=1024, out_channels=512)
        self.d4 = DecoderBlock(in_channels=1024, out_channels=512, dropout=False)
        self.d5 = DecoderBlock(in_channels=1024, out_channels=256, dropout=False)
        self.d6 = DecoderBlock(in_channels=512, out_channels=128, dropout=False)
        self.d7 = DecoderBlock(in_channels=256, out_channels=64, dropout=False)
        self.final_conv = nn.ConvTranspose2d(in_channels=128, out_channels=out_channels, kernel_size=4, stride=2, padding=1)
        self.tanh = nn.Tanh()
    
    def forward(self, input):
        e1 = self.e1(input)
        e2 = self.e2(e1)
        e3 = self.e3(e2)
        e4 = self.e4(e3)
        e5 = self.e5(e4)
        e6 = self.e6(e5)
        e7 = self.e7(e6)
        bottleneck1 = self.bottleneck_conv(e7)
        bottleneck2 = self.bottleneck_relu(bottleneck1)
        d1 = self.d1(bottleneck2, e7)
        d2 = self.d2(d1, e6)
        d3 = self.d3(d2, e5)
        d4 = self.d4(d3, e4)
        d5 = self.d5(d4, e3)
        d6 = self.d6(d5, e2)
        d7 = self.d7(d6, e1)
        out1 = self.final_conv(d7)
        out2 = self.tanh(out1)
        return out2